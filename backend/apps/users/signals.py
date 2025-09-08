"""
Signals для пользователей
"""

from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.contrib.auth.signals import user_logged_in, user_logged_out, user_login_failed
from django.contrib.sessions.models import Session
from .models import User, UserProfile, UserSession
from apps.common.utils import get_client_ip
import logging

logger = logging.getLogger(__name__)


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """
    Создание профиля пользователя при создании пользователя
    """
    if created:
        UserProfile.objects.create(user=instance)
        logger.info(f"Создан профиль для пользователя {instance.email}")


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    """
    Сохранение профиля пользователя при сохранении пользователя
    """
    try:
        instance.profile.save()
    except UserProfile.DoesNotExist:
        # Если профиль не существует, создаём его
        UserProfile.objects.create(user=instance)
        logger.info(f"Создан недостающий профиль для пользователя {instance.email}")


@receiver(user_logged_in)
def log_user_login(sender, request, user, **kwargs):
    """
    Логирование успешного входа пользователя
    """
    ip_address = get_client_ip(request)
    user_agent = request.META.get('HTTP_USER_AGENT', '')
    
    # Обновляем IP последнего входа
    user.last_login_ip = ip_address
    user.save(update_fields=['last_login_ip'])
    
    # Создаём или обновляем сессию
    session_key = request.session.session_key
    if session_key:
        UserSession.objects.update_or_create(
            user=user,
            session_key=session_key,
            defaults={
                'ip_address': ip_address,
                'user_agent': user_agent,
                'is_active': True
            }
        )
    
    logger.info(
        f"Пользователь {user.email} вошёл в систему с IP {ip_address}",
        extra={
            'user_id': user.id,
            'ip_address': ip_address,
            'user_agent': user_agent
        }
    )


@receiver(user_logged_out)
def log_user_logout(sender, request, user, **kwargs):
    """
    Логирование выхода пользователя
    """
    if user:
        # Деактивируем сессию
        session_key = request.session.session_key
        if session_key:
            UserSession.objects.filter(
                user=user,
                session_key=session_key
            ).update(is_active=False)
        
        logger.info(
            f"Пользователь {user.email} вышел из системы",
            extra={'user_id': user.id}
        )


@receiver(user_login_failed)
def log_user_login_failed(sender, credentials, request, **kwargs):
    """
    Логирование неудачной попытки входа
    """
    email = credentials.get('username', credentials.get('email', 'unknown'))
    ip_address = get_client_ip(request)
    
    # Пытаемся найти пользователя и увеличить счётчик неудачных попыток
    try:
        user = User.objects.get(email=email)
        user.increment_failed_login()
    except User.DoesNotExist:
        pass
    
    logger.warning(
        f"Неудачная попытка входа для {email} с IP {ip_address}",
        extra={
            'email': email,
            'ip_address': ip_address,
            'user_agent': request.META.get('HTTP_USER_AGENT', '')
        }
    )


@receiver(post_delete, sender=Session)
def cleanup_user_session(sender, instance, **kwargs):
    """
    Очистка записей пользовательских сессий при удалении Django сессии
    """
    UserSession.objects.filter(session_key=instance.session_key).delete()


@receiver(post_save, sender=User)
def log_user_changes(sender, instance, created, **kwargs):
    """
    Логирование изменений пользователя
    """
    if created:
        logger.info(
            f"Создан новый пользователь: {instance.email} с ролью {instance.role}",
            extra={
                'user_id': instance.id,
                'action': 'user_created',
                'role': instance.role
            }
        )
    else:
        # Логируем важные изменения
        if hasattr(instance, '_state') and instance._state.adding is False:
            # Проверяем изменение роли
            if instance.tracker.has_changed('role'):
                old_role = instance.tracker.previous('role')
                logger.info(
                    f"Изменена роль пользователя {instance.email}: {old_role} → {instance.role}",
                    extra={
                        'user_id': instance.id,
                        'action': 'role_changed',
                        'old_role': old_role,
                        'new_role': instance.role
                    }
                )
            
            # Проверяем изменение статуса активности
            if instance.tracker.has_changed('is_active'):
                status = 'активирован' if instance.is_active else 'деактивирован'
                logger.info(
                    f"Пользователь {instance.email} {status}",
                    extra={
                        'user_id': instance.id,
                        'action': 'status_changed',
                        'is_active': instance.is_active
                    }
                )


# Добавляем трекер изменений для модели User
try:
    from model_utils import FieldTracker
    User.add_to_class('tracker', FieldTracker(fields=['role', 'is_active', 'email']))
except ImportError:
    # Если model_utils не установлен, логируем без детального трекинга
    logger.warning("model_utils не установлен, детальное отслеживание изменений недоступно")
