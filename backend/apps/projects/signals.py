"""
Сигналы для управления проектами
"""

from django.db.models.signals import post_save, post_delete, pre_save
from django.dispatch import receiver
from django.utils import timezone
from .models import Project, ProjectMember, ProjectStage
import logging

logger = logging.getLogger(__name__)


@receiver(post_save, sender=Project)
def log_project_changes(sender, instance, created, **kwargs):
    """
    Логирование изменений проекта
    """
    if created:
        logger.info(
            f"Создан новый проект: {instance.name} (менеджер: {instance.manager.get_full_name()})",
            extra={
                'project_id': instance.id,
                'project_name': instance.name,
                'manager_id': instance.manager.id,
                'action': 'project_created'
            }
        )
        
        # Автоматически добавляем менеджера как участника проекта
        if not instance.is_member(instance.manager):
            instance.add_member(instance.manager, role='manager')
            logger.info(
                f"Менеджер {instance.manager.get_full_name()} автоматически добавлен в проект {instance.name}"
            )
    else:
        # Логируем важные изменения
        if hasattr(instance, '_state') and instance._state.adding is False:
            # Отслеживаем изменение статуса
            if hasattr(instance, '_original_status') and instance._original_status != instance.status:
                logger.info(
                    f"Изменен статус проекта {instance.name}: {instance._original_status} → {instance.status}",
                    extra={
                        'project_id': instance.id,
                        'project_name': instance.name,
                        'old_status': instance._original_status,
                        'new_status': instance.status,
                        'action': 'status_changed'
                    }
                )
            
            # Отслеживаем изменение менеджера
            if hasattr(instance, '_original_manager') and instance._original_manager != instance.manager:
                old_manager = instance._original_manager
                new_manager = instance.manager
                logger.info(
                    f"Изменен менеджер проекта {instance.name}: {old_manager.get_full_name() if old_manager else 'None'} → {new_manager.get_full_name()}",
                    extra={
                        'project_id': instance.id,
                        'project_name': instance.name,
                        'old_manager_id': old_manager.id if old_manager else None,
                        'new_manager_id': new_manager.id,
                        'action': 'manager_changed'
                    }
                )
                
                # Добавляем нового менеджера как участника
                if not instance.is_member(new_manager):
                    instance.add_member(new_manager, role='manager')


@receiver(pre_save, sender=Project)
def store_original_values(sender, instance, **kwargs):
    """
    Сохраняем оригинальные значения для отслеживания изменений
    """
    if instance.pk:
        try:
            original = Project.objects.get(pk=instance.pk)
            instance._original_status = original.status
            instance._original_manager = original.manager
        except Project.DoesNotExist:
            pass


@receiver(post_save, sender=ProjectMember)
def log_member_changes(sender, instance, created, **kwargs):
    """
    Логирование изменений участников проекта
    """
    if created:
        logger.info(
            f"Пользователь {instance.user.get_full_name()} добавлен в проект {instance.project.name} с ролью {instance.get_role_display()}",
            extra={
                'project_id': instance.project.id,
                'project_name': instance.project.name,
                'user_id': instance.user.id,
                'user_name': instance.user.get_full_name(),
                'role': instance.role,
                'action': 'member_added'
            }
        )
    else:
        # Проверяем изменение активности
        if hasattr(instance, '_original_is_active') and instance._original_is_active != instance.is_active:
            action = 'member_activated' if instance.is_active else 'member_deactivated'
            status = 'активирован' if instance.is_active else 'деактивирован'
            
            logger.info(
                f"Участник {instance.user.get_full_name()} {status} в проекте {instance.project.name}",
                extra={
                    'project_id': instance.project.id,
                    'project_name': instance.project.name,
                    'user_id': instance.user.id,
                    'user_name': instance.user.get_full_name(),
                    'is_active': instance.is_active,
                    'action': action
                }
            )


@receiver(pre_save, sender=ProjectMember)
def store_member_original_values(sender, instance, **kwargs):
    """
    Сохраняем оригинальные значения участника для отслеживания изменений
    """
    if instance.pk:
        try:
            original = ProjectMember.objects.get(pk=instance.pk)
            instance._original_is_active = original.is_active
        except ProjectMember.DoesNotExist:
            pass


@receiver(post_save, sender=ProjectStage)
def log_stage_changes(sender, instance, created, **kwargs):
    """
    Логирование изменений этапов проекта
    """
    if created:
        logger.info(
            f"Создан новый этап '{instance.name}' в проекте {instance.project.name}",
            extra={
                'project_id': instance.project.id,
                'project_name': instance.project.name,
                'stage_id': instance.id,
                'stage_name': instance.name,
                'action': 'stage_created'
            }
        )
    else:
        # Отслеживаем изменение статуса этапа
        if hasattr(instance, '_original_stage_status') and instance._original_stage_status != instance.status:
            logger.info(
                f"Изменен статус этапа '{instance.name}' в проекте {instance.project.name}: {instance._original_stage_status} → {instance.status}",
                extra={
                    'project_id': instance.project.id,
                    'project_name': instance.project.name,
                    'stage_id': instance.id,
                    'stage_name': instance.name,
                    'old_status': instance._original_stage_status,
                    'new_status': instance.status,
                    'action': 'stage_status_changed'
                }
            )
        
        # Отслеживаем изменение процента выполнения
        if hasattr(instance, '_original_completion') and instance._original_completion != instance.completion_percentage:
            logger.info(
                f"Обновлен прогресс этапа '{instance.name}' в проекте {instance.project.name}: {instance._original_completion}% → {instance.completion_percentage}%",
                extra={
                    'project_id': instance.project.id,
                    'project_name': instance.project.name,
                    'stage_id': instance.id,
                    'stage_name': instance.name,
                    'old_completion': instance._original_completion,
                    'new_completion': instance.completion_percentage,
                    'action': 'stage_progress_updated'
                }
            )


@receiver(pre_save, sender=ProjectStage)
def store_stage_original_values(sender, instance, **kwargs):
    """
    Сохраняем оригинальные значения этапа для отслеживания изменений
    """
    if instance.pk:
        try:
            original = ProjectStage.objects.get(pk=instance.pk)
            instance._original_stage_status = original.status
            instance._original_completion = original.completion_percentage
        except ProjectStage.DoesNotExist:
            pass


@receiver(post_save, sender=ProjectStage)
def update_project_progress(sender, instance, **kwargs):
    """
    Обновление прогресса проекта при изменении этапов
    """
    project = instance.project
    
    # Пересчитываем прогресс проекта
    # Это будет происходить автоматически через property progress_percentage
    
    # Проверяем, завершены ли все этапы
    all_stages = project.stages.all()
    if all_stages.exists():
        completed_stages = all_stages.filter(status='completed')
        
        # Если все этапы завершены, можно предложить завершить проект
        if completed_stages.count() == all_stages.count():
            if project.status not in ['completed', 'cancelled']:
                logger.info(
                    f"Все этапы проекта {project.name} завершены. Рекомендуется завершить проект.",
                    extra={
                        'project_id': project.id,
                        'project_name': project.name,
                        'action': 'all_stages_completed'
                    }
                )


@receiver(post_delete, sender=ProjectMember)
def log_member_removal(sender, instance, **kwargs):
    """
    Логирование удаления участника проекта
    """
    logger.info(
        f"Пользователь {instance.user.get_full_name()} удален из проекта {instance.project.name}",
        extra={
            'project_id': instance.project.id,
            'project_name': instance.project.name,
            'user_id': instance.user.id,
            'user_name': instance.user.get_full_name(),
            'role': instance.role,
            'action': 'member_removed'
        }
    )


@receiver(post_delete, sender=ProjectStage)
def log_stage_removal(sender, instance, **kwargs):
    """
    Логирование удаления этапа проекта
    """
    logger.info(
        f"Этап '{instance.name}' удален из проекта {instance.project.name}",
        extra={
            'project_id': instance.project.id,
            'project_name': instance.project.name,
            'stage_name': instance.name,
            'action': 'stage_removed'
        }
    )


def check_project_deadlines():
    """
    Проверка приближающихся дедлайнов проектов
    Эту функцию можно вызывать через Celery задачу
    """
    from django.utils import timezone
    from datetime import timedelta
    
    # Находим проекты, которые завершаются в ближайшие 7 дней
    warning_date = timezone.now().date() + timedelta(days=7)
    projects_approaching_deadline = Project.objects.filter(
        end_date__lte=warning_date,
        end_date__gte=timezone.now().date(),
        status__in=['planning', 'in_progress']
    )
    
    for project in projects_approaching_deadline:
        days_left = (project.end_date - timezone.now().date()).days
        logger.warning(
            f"Проект {project.name} завершается через {days_left} дней",
            extra={
                'project_id': project.id,
                'project_name': project.name,
                'days_left': days_left,
                'action': 'deadline_approaching'
            }
        )
    
    # Находим просроченные проекты
    overdue_projects = Project.objects.filter(
        end_date__lt=timezone.now().date(),
        status__in=['planning', 'in_progress', 'on_hold']
    )
    
    for project in overdue_projects:
        days_overdue = (timezone.now().date() - project.end_date).days
        logger.error(
            f"Проект {project.name} просрочен на {days_overdue} дней",
            extra={
                'project_id': project.id,
                'project_name': project.name,
                'days_overdue': days_overdue,
                'action': 'project_overdue'
            }
        )
    
    return {
        'approaching_deadline': projects_approaching_deadline.count(),
        'overdue': overdue_projects.count()
    }
