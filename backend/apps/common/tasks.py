"""
Celery задачи для общих функций
"""

import os
import logging
from celery import shared_task
from django.core.management import call_command
from django.conf import settings
from .services import NotificationService

logger = logging.getLogger(__name__)


@shared_task
def backup_database_task():
    """
    Задача для автоматического резервного копирования базы данных
    """
    try:
        logger.info('Начинаем автоматическое резервное копирование базы данных')
        
        # Получаем настройки резервного копирования
        backup_dir = getattr(settings, 'BACKUP_DIR', 'backups')
        keep_days = getattr(settings, 'BACKUP_KEEP_DAYS', 30)
        compress = getattr(settings, 'BACKUP_COMPRESS', True)
        
        # Выполняем резервное копирование
        call_command(
            'backup_database',
            output_dir=backup_dir,
            keep_days=keep_days,
            compress=compress
        )
        
        logger.info('Автоматическое резервное копирование завершено успешно')
        
        # Отправляем уведомление администраторам о успешном резервном копировании
        from django.contrib.auth import get_user_model
        User = get_user_model()
        
        admins = User.objects.filter(
            is_staff=True,
            is_active=True
        )
        
        if admins.exists():
            NotificationService.send_bulk_notifications(
                recipients=list(admins),
                notification_type='system_alert',
                title='Резервное копирование завершено',
                message='Автоматическое резервное копирование базы данных выполнено успешно.',
                priority='normal'
            )
        
        return 'Резервное копирование выполнено успешно'
        
    except Exception as e:
        error_msg = f'Ошибка резервного копирования: {str(e)}'
        logger.error(error_msg)
        
        # Отправляем уведомление об ошибке администраторам
        from django.contrib.auth import get_user_model
        User = get_user_model()
        
        admins = User.objects.filter(
            is_staff=True,
            is_active=True
        )
        
        if admins.exists():
            NotificationService.send_bulk_notifications(
                recipients=list(admins),
                notification_type='system_alert',
                title='Ошибка резервного копирования',
                message=f'Произошла ошибка при выполнении резервного копирования: {str(e)}',
                priority='high'
            )
        
        raise


@shared_task
def cleanup_old_notifications_task():
    """
    Задача для очистки старых уведомлений
    """
    try:
        logger.info('Начинаем очистку старых уведомлений')
        
        # Получаем настройки очистки
        keep_days = getattr(settings, 'NOTIFICATION_KEEP_DAYS', 30)
        
        # Выполняем очистку
        deleted_count = NotificationService.cleanup_old_notifications(keep_days)
        
        logger.info(f'Очистка уведомлений завершена. Удалено: {deleted_count}')
        
        return f'Удалено {deleted_count} старых уведомлений'
        
    except Exception as e:
        error_msg = f'Ошибка очистки уведомлений: {str(e)}'
        logger.error(error_msg)
        raise


@shared_task
def cleanup_old_audit_logs_task():
    """
    Задача для очистки старых записей аудита
    """
    try:
        logger.info('Начинаем очистку старых записей аудита')
        
        from .models import AuditLog
        from django.utils import timezone
        from datetime import timedelta
        
        # Получаем настройки очистки
        keep_days = getattr(settings, 'AUDIT_LOG_KEEP_DAYS', 90)
        cutoff_date = timezone.now() - timedelta(days=keep_days)
        
        # Удаляем старые записи
        deleted_count, _ = AuditLog.objects.filter(
            created_at__lt=cutoff_date
        ).delete()
        
        logger.info(f'Очистка записей аудита завершена. Удалено: {deleted_count}')
        
        return f'Удалено {deleted_count} старых записей аудита'
        
    except Exception as e:
        error_msg = f'Ошибка очистки записей аудита: {str(e)}'
        logger.error(error_msg)
        raise


@shared_task
def send_daily_reports_task():
    """
    Задача для отправки ежедневных отчетов
    """
    try:
        logger.info('Начинаем отправку ежедневных отчетов')
        
        from django.contrib.auth import get_user_model
        from apps.defects.models import Defect
        from django.utils import timezone
        from datetime import timedelta
        
        User = get_user_model()
        
        # Получаем статистику за последние 24 часа
        yesterday = timezone.now() - timedelta(days=1)
        
        stats = {
            'new_defects': Defect.objects.filter(created_at__gte=yesterday).count(),
            'closed_defects': Defect.objects.filter(
                status='closed',
                closed_at__gte=yesterday
            ).count(),
            'overdue_defects': Defect.objects.filter(
                due_date__lt=timezone.now().date(),
                status__in=['new', 'in_progress', 'review']
            ).count(),
        }
        
        # Отправляем отчет менеджерам
        managers = User.objects.filter(
            role='manager',
            is_active=True
        )
        
        if managers.exists():
            message = f"""
Ежедневный отчет по дефектам:

• Новых дефектов: {stats['new_defects']}
• Закрытых дефектов: {stats['closed_defects']}
• Просроченных дефектов: {stats['overdue_defects']}

Дата: {timezone.now().strftime('%d.%m.%Y')}
            """.strip()
            
            NotificationService.send_bulk_notifications(
                recipients=list(managers),
                notification_type='system_alert',
                title='Ежедневный отчет по дефектам',
                message=message,
                priority='normal'
            )
        
        logger.info('Ежедневные отчеты отправлены')
        
        return 'Ежедневные отчеты отправлены успешно'
        
    except Exception as e:
        error_msg = f'Ошибка отправки ежедневных отчетов: {str(e)}'
        logger.error(error_msg)
        raise


@shared_task
def check_overdue_defects_task():
    """
    Задача для проверки просроченных дефектов
    """
    try:
        logger.info('Начинаем проверку просроченных дефектов')
        
        from apps.defects.models import Defect
        from django.utils import timezone
        
        # Находим просроченные дефекты
        overdue_defects = Defect.objects.filter(
            due_date__lt=timezone.now().date(),
            status__in=['new', 'in_progress', 'review']
        ).select_related('assignee', 'project')
        
        notifications_sent = 0
        
        for defect in overdue_defects:
            # Отправляем уведомление исполнителю
            if defect.assignee:
                NotificationService.create_notification(
                    recipient=defect.assignee,
                    notification_type='defect_overdue',
                    title=f'Просрочен дефект: {defect.title}',
                    message=f'Дефект "{defect.title}" просрочен. Срок выполнения: {defect.due_date}',
                    priority='high',
                    related_object=defect
                )
                notifications_sent += 1
            
            # Отправляем уведомление менеджеру проекта
            if defect.project.manager:
                NotificationService.create_notification(
                    recipient=defect.project.manager,
                    notification_type='defect_overdue',
                    title=f'Просрочен дефект в проекте: {defect.title}',
                    message=f'В проекте "{defect.project.name}" просрочен дефект "{defect.title}". Исполнитель: {defect.assignee.get_full_name() if defect.assignee else "Не назначен"}',
                    priority='high',
                    related_object=defect
                )
                notifications_sent += 1
        
        logger.info(f'Проверка просроченных дефектов завершена. Отправлено уведомлений: {notifications_sent}')
        
        return f'Отправлено {notifications_sent} уведомлений о просроченных дефектах'
        
    except Exception as e:
        error_msg = f'Ошибка проверки просроченных дефектов: {str(e)}'
        logger.error(error_msg)
        raise


@shared_task
def system_health_check_task():
    """
    Задача для проверки состояния системы
    """
    try:
        logger.info('Начинаем проверку состояния системы')
        
        from django.db import connection
        from django.core.cache import cache
        from django.utils import timezone
        
        health_status = {
            'timestamp': timezone.now().isoformat(),
            'database': False,
            'cache': False,
            'disk_space': False,
        }
        
        # Проверяем базу данных
        try:
            with connection.cursor() as cursor:
                cursor.execute("SELECT 1")
                health_status['database'] = True
        except Exception as e:
            logger.error(f'Ошибка подключения к базе данных: {str(e)}')
        
        # Проверяем кэш
        try:
            cache.set('health_check', 'ok', 10)
            if cache.get('health_check') == 'ok':
                health_status['cache'] = True
        except Exception as e:
            logger.error(f'Ошибка кэша: {str(e)}')
        
        # Проверяем свободное место на диске
        try:
            import shutil
            total, used, free = shutil.disk_usage('/')
            free_percent = (free / total) * 100
            health_status['disk_space'] = free_percent > 10  # Минимум 10% свободного места
            health_status['disk_free_percent'] = round(free_percent, 2)
        except Exception as e:
            logger.error(f'Ошибка проверки диска: {str(e)}')
        
        # Если есть проблемы, отправляем уведомление
        if not all([health_status['database'], health_status['cache'], health_status['disk_space']]):
            from django.contrib.auth import get_user_model
            User = get_user_model()
            
            admins = User.objects.filter(
                is_staff=True,
                is_active=True
            )
            
            if admins.exists():
                issues = []
                if not health_status['database']:
                    issues.append('База данных недоступна')
                if not health_status['cache']:
                    issues.append('Кэш недоступен')
                if not health_status['disk_space']:
                    issues.append(f'Мало свободного места на диске ({health_status.get("disk_free_percent", 0)}%)')
                
                message = f'Обнаружены проблемы в системе:\n' + '\n'.join(f'• {issue}' for issue in issues)
                
                NotificationService.send_bulk_notifications(
                    recipients=list(admins),
                    notification_type='system_alert',
                    title='Проблемы в системе',
                    message=message,
                    priority='urgent'
                )
        
        logger.info('Проверка состояния системы завершена')
        
        return health_status
        
    except Exception as e:
        error_msg = f'Ошибка проверки состояния системы: {str(e)}'
        logger.error(error_msg)
        raise
