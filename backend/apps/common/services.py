"""
Сервисы для общих функций
"""

import logging
from typing import Dict, Any, List, Optional
from django.core.mail import send_mail, EmailMultiAlternatives
from django.template.loader import render_to_string
from django.conf import settings
from django.utils import timezone
from django.db import transaction
from celery import shared_task
from .models import Notification, NotificationTemplate, NotificationSettings

logger = logging.getLogger(__name__)


class NotificationService:
    """
    Сервис для отправки уведомлений
    """
    
    @staticmethod
    def create_notification(
        recipient,
        notification_type: str,
        title: str,
        message: str,
        priority: str = 'normal',
        related_object=None,
        metadata: Dict[str, Any] = None,
        send_immediately: bool = True
    ) -> Notification:
        """
        Создает уведомление
        """
        # Получаем настройки пользователя
        settings_obj, _ = NotificationSettings.objects.get_or_create(
            user=recipient
        )
        
        # Определяем связанный объект
        related_object_type = None
        related_object_id = None
        if related_object:
            related_object_type = related_object.__class__.__name__.lower()
            related_object_id = related_object.id
        
        # Создаем уведомление
        notification = Notification.objects.create(
            recipient=recipient,
            notification_type=notification_type,
            title=title,
            message=message,
            priority=priority,
            related_object_type=related_object_type,
            related_object_id=related_object_id,
            metadata=metadata or {},
            send_email=settings_obj.email_enabled,
            send_sms=settings_obj.sms_enabled,
            send_push=settings_obj.push_enabled
        )
        
        if send_immediately:
            NotificationService.send_notification.delay(notification.id)
        
        return notification
    
    @staticmethod
    @shared_task
    def send_notification(notification_id: int):
        """
        Отправляет уведомление (Celery задача)
        """
        try:
            notification = Notification.objects.get(id=notification_id)
            NotificationService._send_notification(notification)
        except Notification.DoesNotExist:
            logger.error(f"Уведомление с ID {notification_id} не найдено")
    
    @staticmethod
    def _send_notification(notification: Notification):
        """
        Внутренний метод отправки уведомления
        """
        try:
            # Получаем настройки пользователя
            settings_obj, _ = NotificationSettings.objects.get_or_create(
                user=notification.recipient
            )
            
            # Отправляем по email
            if notification.send_email and settings_obj.should_send_notification(
                notification.notification_type, 'email'
            ):
                NotificationService._send_email_notification(notification)
            
            # Отправляем SMS
            if notification.send_sms and settings_obj.should_send_notification(
                notification.notification_type, 'sms'
            ):
                NotificationService._send_sms_notification(notification)
            
            # Отправляем push уведомление
            if notification.send_push and settings_obj.should_send_notification(
                notification.notification_type, 'push'
            ):
                NotificationService._send_push_notification(notification)
            
            notification.mark_as_sent()
            
        except Exception as e:
            logger.error(f"Ошибка отправки уведомления {notification.id}: {str(e)}")
            notification.mark_as_failed()
    
    @staticmethod
    def _send_email_notification(notification: Notification):
        """
        Отправляет email уведомление
        """
        try:
            # Получаем шаблон
            template = NotificationTemplate.objects.filter(
                notification_type=notification.notification_type,
                channel='email',
                is_active=True
            ).first()
            
            if template:
                # Подготавливаем контекст
                context = {
                    'user': notification.recipient,
                    'notification': notification,
                    'title': notification.title,
                    'message': notification.message,
                    'site_url': getattr(settings, 'SITE_URL', 'http://localhost:8000'),
                }
                
                # Добавляем метаданные в контекст
                context.update(notification.metadata)
                
                # Рендерим тему и сообщение
                subject = template.render_subject(context)
                message = template.render_message(context)
            else:
                # Используем простой формат
                subject = notification.title
                message = notification.message
            
            # Отправляем email
            send_mail(
                subject=subject,
                message=message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[notification.recipient.email],
                fail_silently=False
            )
            
            logger.info(f"Email уведомление отправлено пользователю {notification.recipient.email}")
            
        except Exception as e:
            logger.error(f"Ошибка отправки email уведомления: {str(e)}")
            raise
    
    @staticmethod
    def _send_sms_notification(notification: Notification):
        """
        Отправляет SMS уведомление
        """
        try:
            # Получаем настройки пользователя
            settings_obj, _ = NotificationSettings.objects.get_or_create(
                user=notification.recipient
            )
            
            if not settings_obj.sms_phone:
                logger.warning(f"У пользователя {notification.recipient.email} не указан номер телефона для SMS")
                return
            
            # Получаем шаблон
            template = NotificationTemplate.objects.filter(
                notification_type=notification.notification_type,
                channel='sms',
                is_active=True
            ).first()
            
            if template:
                context = {
                    'user': notification.recipient,
                    'notification': notification,
                    'title': notification.title,
                    'message': notification.message,
                }
                context.update(notification.metadata)
                message = template.render_message(context)
            else:
                message = f"{notification.title}: {notification.message}"
            
            # TODO: Интеграция с SMS провайдером
            # В реальном проекте здесь будет отправка SMS через API провайдера
            logger.info(f"SMS уведомление отправлено на номер {settings_obj.sms_phone}: {message}")
            
        except Exception as e:
            logger.error(f"Ошибка отправки SMS уведомления: {str(e)}")
            raise
    
    @staticmethod
    def _send_push_notification(notification: Notification):
        """
        Отправляет push уведомление
        """
        try:
            # TODO: Интеграция с push сервисом (Firebase, OneSignal и т.д.)
            # В реальном проекте здесь будет отправка push уведомления
            logger.info(f"Push уведомление отправлено пользователю {notification.recipient.email}")
            
        except Exception as e:
            logger.error(f"Ошибка отправки push уведомления: {str(e)}")
            raise
    
    @staticmethod
    def send_bulk_notifications(
        recipients: List,
        notification_type: str,
        title: str,
        message: str,
        priority: str = 'normal',
        related_object=None,
        metadata: Dict[str, Any] = None
    ):
        """
        Отправляет уведомления нескольким пользователям
        """
        notifications = []
        
        for recipient in recipients:
            notification = NotificationService.create_notification(
                recipient=recipient,
                notification_type=notification_type,
                title=title,
                message=message,
                priority=priority,
                related_object=related_object,
                metadata=metadata,
                send_immediately=False
            )
            notifications.append(notification)
        
        # Отправляем все уведомления
        for notification in notifications:
            NotificationService.send_notification.delay(notification.id)
    
    @staticmethod
    def mark_notifications_as_read(user, notification_ids: List[int] = None):
        """
        Отмечает уведомления как прочитанные
        """
        queryset = Notification.objects.filter(recipient=user)
        
        if notification_ids:
            queryset = queryset.filter(id__in=notification_ids)
        else:
            queryset = queryset.filter(read_at__isnull=True)
        
        queryset.update(
            read_at=timezone.now(),
            status=Notification.Status.READ
        )
    
    @staticmethod
    def get_unread_count(user) -> int:
        """
        Возвращает количество непрочитанных уведомлений
        """
        return Notification.objects.filter(
            recipient=user,
            read_at__isnull=True
        ).count()
    
    @staticmethod
    def cleanup_old_notifications(days: int = 30):
        """
        Удаляет старые уведомления
        """
        cutoff_date = timezone.now() - timezone.timedelta(days=days)
        
        deleted_count, _ = Notification.objects.filter(
            created_at__lt=cutoff_date,
            status__in=[Notification.Status.READ, Notification.Status.DELIVERED]
        ).delete()
        
        logger.info(f"Удалено {deleted_count} старых уведомлений")
        return deleted_count


class EmailService:
    """
    Сервис для отправки email
    """
    
    @staticmethod
    def send_welcome_email(user):
        """
        Отправляет приветственное письмо новому пользователю
        """
        try:
            subject = f"Добро пожаловать в систему управления дефектами, {user.get_full_name()}!"
            
            context = {
                'user': user,
                'site_url': getattr(settings, 'SITE_URL', 'http://localhost:8000'),
            }
            
            html_message = render_to_string('emails/welcome.html', context)
            text_message = render_to_string('emails/welcome.txt', context)
            
            email = EmailMultiAlternatives(
                subject=subject,
                body=text_message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                to=[user.email]
            )
            email.attach_alternative(html_message, "text/html")
            email.send()
            
            logger.info(f"Приветственное письмо отправлено пользователю {user.email}")
            
        except Exception as e:
            logger.error(f"Ошибка отправки приветственного письма: {str(e)}")
    
    @staticmethod
    def send_password_reset_email(user, reset_token):
        """
        Отправляет письмо для сброса пароля
        """
        try:
            subject = "Сброс пароля - Система управления дефектами"
            
            context = {
                'user': user,
                'reset_token': reset_token,
                'site_url': getattr(settings, 'SITE_URL', 'http://localhost:8000'),
            }
            
            html_message = render_to_string('emails/password_reset.html', context)
            text_message = render_to_string('emails/password_reset.txt', context)
            
            email = EmailMultiAlternatives(
                subject=subject,
                body=text_message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                to=[user.email]
            )
            email.attach_alternative(html_message, "text/html")
            email.send()
            
            logger.info(f"Письмо для сброса пароля отправлено пользователю {user.email}")
            
        except Exception as e:
            logger.error(f"Ошибка отправки письма для сброса пароля: {str(e)}")
    
    @staticmethod
    def send_defect_assignment_email(defect, assignee):
        """
        Отправляет письмо о назначении дефекта
        """
        try:
            subject = f"Вам назначен дефект: {defect.title}"
            
            context = {
                'defect': defect,
                'assignee': assignee,
                'site_url': getattr(settings, 'SITE_URL', 'http://localhost:8000'),
            }
            
            html_message = render_to_string('emails/defect_assignment.html', context)
            text_message = render_to_string('emails/defect_assignment.txt', context)
            
            email = EmailMultiAlternatives(
                subject=subject,
                body=text_message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                to=[assignee.email]
            )
            email.attach_alternative(html_message, "text/html")
            email.send()
            
            logger.info(f"Письмо о назначении дефекта отправлено пользователю {assignee.email}")
            
        except Exception as e:
            logger.error(f"Ошибка отправки письма о назначении дефекта: {str(e)}")


class AuditService:
    """
    Сервис для аудита действий пользователей
    """
    
    @staticmethod
    def log_user_action(
        user,
        action: str,
        object_type: str = None,
        object_id: int = None,
        details: Dict[str, Any] = None,
        ip_address: str = None
    ):
        """
        Логирует действие пользователя
        """
        try:
            from .models import AuditLog
            
            AuditLog.objects.create(
                user=user,
                action=action,
                object_type=object_type,
                object_id=object_id,
                details=details or {},
                ip_address=ip_address
            )
            
        except Exception as e:
            logger.error(f"Ошибка логирования действия пользователя: {str(e)}")
