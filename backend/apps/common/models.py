"""
Базовые модели для всех приложений
"""

from django.db import models
from django.utils import timezone


class TimeStampedModel(models.Model):
    """
    Абстрактная модель с полями создания и обновления
    """
    created_at = models.DateTimeField(
        verbose_name='Дата создания',
        auto_now_add=True,
        help_text='Автоматически устанавливается при создании'
    )
    updated_at = models.DateTimeField(
        verbose_name='Дата обновления',
        auto_now=True,
        help_text='Автоматически обновляется при изменении'
    )

    class Meta:
        abstract = True


class SoftDeleteManager(models.Manager):
    """
    Менеджер для моделей с мягким удалением
    """
    def get_queryset(self):
        return super().get_queryset().filter(deleted_at__isnull=True)
    
    def with_deleted(self):
        return super().get_queryset()
    
    def deleted_only(self):
        return super().get_queryset().filter(deleted_at__isnull=False)


class SoftDeleteModel(models.Model):
    """
    Абстрактная модель с мягким удалением
    """
    deleted_at = models.DateTimeField(
        verbose_name='Дата удаления',
        null=True,
        blank=True,
        help_text='Если заполнено, объект считается удалённым'
    )
    
    objects = SoftDeleteManager()
    all_objects = models.Manager()
    
    class Meta:
        abstract = True
    
    def delete(self, using=None, keep_parents=False):
        """
        Мягкое удаление объекта
        """
        self.deleted_at = timezone.now()
        self.save(using=using)
    
    def hard_delete(self, using=None, keep_parents=False):
        """
        Полное удаление объекта
        """
        super().delete(using=using, keep_parents=keep_parents)
    
    def restore(self):
        """
        Восстановление удалённого объекта
        """
        self.deleted_at = None
        self.save()
    
    @property
    def is_deleted(self):
        """
        Проверка, удалён ли объект
        """
        return self.deleted_at is not None


class BaseModel(TimeStampedModel, SoftDeleteModel):
    """
    Базовая модель с временными метками и мягким удалением
    """
    class Meta:
        abstract = True


class Priority(models.TextChoices):
    """
    Уровни приоритета для задач и дефектов
    """
    LOW = 'low', 'Низкий'
    MEDIUM = 'medium', 'Средний'
    HIGH = 'high', 'Высокий'
    CRITICAL = 'critical', 'Критический'


class Status(models.TextChoices):
    """
    Базовые статусы для различных объектов
    """
    ACTIVE = 'active', 'Активный'
    INACTIVE = 'inactive', 'Неактивный'
    DRAFT = 'draft', 'Черновик'
    ARCHIVED = 'archived', 'Архивный'
