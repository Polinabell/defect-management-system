"""
Модели для управления проектами
"""

from django.db import models
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.utils import timezone
from apps.common.models import BaseModel, Status, Priority
from apps.common.utils import create_slug

User = get_user_model()


class Project(BaseModel):
    """
    Модель строительного проекта
    """
    
    class Status(models.TextChoices):
        PLANNING = 'planning', 'Планирование'
        IN_PROGRESS = 'in_progress', 'В работе'
        ON_HOLD = 'on_hold', 'Приостановлен'
        COMPLETED = 'completed', 'Завершён'
        CANCELLED = 'cancelled', 'Отменён'
    
    # Основная информация
    name = models.CharField(
        verbose_name='Название проекта',
        max_length=200,
        unique=True,
        help_text='Уникальное название проекта'
    )
    slug = models.SlugField(
        verbose_name='Слаг',
        max_length=200,
        unique=True,
        blank=True,
        help_text='Автоматически генерируется из названия'
    )
    description = models.TextField(
        verbose_name='Описание проекта',
        help_text='Подробное описание проекта'
    )
    
    # Адрес и местоположение
    address = models.TextField(
        verbose_name='Адрес объекта',
        help_text='Полный адрес строительного объекта'
    )
    coordinates_lat = models.DecimalField(
        verbose_name='Широта',
        max_digits=10,
        decimal_places=8,
        null=True,
        blank=True,
        help_text='Координаты объекта (широта)'
    )
    coordinates_lng = models.DecimalField(
        verbose_name='Долгота',
        max_digits=11,
        decimal_places=8,
        null=True,
        blank=True,
        help_text='Координаты объекта (долгота)'
    )
    
    # Заказчик и контракт
    customer = models.CharField(
        verbose_name='Заказчик',
        max_length=300,
        help_text='Название организации-заказчика'
    )
    customer_contact = models.CharField(
        verbose_name='Контактное лицо заказчика',
        max_length=200,
        blank=True,
        help_text='ФИО контактного лица'
    )
    customer_phone = models.CharField(
        verbose_name='Телефон заказчика',
        max_length=20,
        blank=True,
        help_text='Контактный телефон'
    )
    customer_email = models.EmailField(
        verbose_name='Email заказчика',
        blank=True,
        help_text='Контактный email'
    )
    
    contract_number = models.CharField(
        verbose_name='Номер договора',
        max_length=100,
        blank=True,
        help_text='Номер договора с заказчиком'
    )
    contract_date = models.DateField(
        verbose_name='Дата договора',
        null=True,
        blank=True,
        help_text='Дата заключения договора'
    )
    contract_amount = models.DecimalField(
        verbose_name='Сумма договора',
        max_digits=15,
        decimal_places=2,
        null=True,
        blank=True,
        help_text='Общая сумма договора в рублях'
    )
    
    # Управление проектом
    manager = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name='managed_projects',
        verbose_name='Менеджер проекта',
        help_text='Ответственный менеджер проекта'
    )
    members = models.ManyToManyField(
        User,
        through='ProjectMember',
        related_name='projects',
        verbose_name='Участники проекта',
        help_text='Пользователи, участвующие в проекте'
    )
    
    # Даты и статус
    start_date = models.DateField(
        verbose_name='Дата начала',
        help_text='Плановая дата начала проекта'
    )
    end_date = models.DateField(
        verbose_name='Дата завершения',
        help_text='Плановая дата завершения проекта'
    )
    actual_start_date = models.DateField(
        verbose_name='Фактическая дата начала',
        null=True,
        blank=True,
        help_text='Фактическая дата начала работ'
    )
    actual_end_date = models.DateField(
        verbose_name='Фактическая дата завершения',
        null=True,
        blank=True,
        help_text='Фактическая дата завершения работ'
    )
    
    status = models.CharField(
        verbose_name='Статус проекта',
        max_length=20,
        choices=Status.choices,
        default=Status.PLANNING,
        help_text='Текущий статус проекта'
    )
    priority = models.CharField(
        verbose_name='Приоритет',
        max_length=20,
        choices=Priority.choices,
        default=Priority.MEDIUM,
        help_text='Приоритет проекта'
    )
    
    # Дополнительная информация
    total_area = models.DecimalField(
        verbose_name='Общая площадь (м²)',
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        help_text='Общая площадь строительства'
    )
    building_type = models.CharField(
        verbose_name='Тип здания',
        max_length=100,
        blank=True,
        choices=[
            ('residential', 'Жилое'),
            ('commercial', 'Коммерческое'),
            ('industrial', 'Промышленное'),
            ('infrastructure', 'Инфраструктура'),
            ('other', 'Другое'),
        ],
        help_text='Тип строительного объекта'
    )
    floors_count = models.PositiveSmallIntegerField(
        verbose_name='Количество этажей',
        null=True,
        blank=True,
        help_text='Количество этажей в здании'
    )
    
    # Настройки уведомлений
    notify_on_defect_creation = models.BooleanField(
        verbose_name='Уведомлять о новых дефектах',
        default=True,
        help_text='Отправлять уведомления при создании дефектов'
    )
    notify_on_status_change = models.BooleanField(
        verbose_name='Уведомлять об изменении статусов',
        default=True,
        help_text='Отправлять уведомления при изменении статусов дефектов'
    )
    
    class Meta:
        verbose_name = 'Проект'
        verbose_name_plural = 'Проекты'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['status']),
            models.Index(fields=['manager']),
            models.Index(fields=['start_date', 'end_date']),
            models.Index(fields=['priority']),
        ]
    
    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        """Переопределяем save для автогенерации slug"""
        if not self.slug:
            self.slug = create_slug(self.name)
        super().save(*args, **kwargs)
    
    def clean(self):
        """Валидация модели"""
        super().clean()
        
        # Проверяем даты
        if self.start_date and self.end_date:
            if self.start_date > self.end_date:
                raise ValidationError('Дата начала не может быть позже даты завершения')
        
        if self.actual_start_date and self.actual_end_date:
            if self.actual_start_date > self.actual_end_date:
                raise ValidationError('Фактическая дата начала не может быть позже даты завершения')
        
        # Проверяем, что менеджер имеет соответствующую роль
        if self.manager and not self.manager.role in ['admin', 'manager']:
            raise ValidationError('Менеджером проекта может быть только пользователь с ролью "Менеджер" или "Администратор"')
    
    @property
    def duration_planned(self):
        """Планируемая продолжительность проекта в днях"""
        if self.start_date and self.end_date:
            return (self.end_date - self.start_date).days
        return None
    
    @property
    def duration_actual(self):
        """Фактическая продолжительность проекта в днях"""
        if self.actual_start_date and self.actual_end_date:
            return (self.actual_end_date - self.actual_start_date).days
        return None
    
    @property
    def progress_percentage(self):
        """Процент выполнения проекта на основе дефектов"""
        total_defects = self.defects.count()
        if total_defects == 0:
            return 100 if self.status == self.Status.COMPLETED else 0
        
        closed_defects = self.defects.filter(status='closed').count()
        return round((closed_defects / total_defects) * 100, 1)
    
    @property
    def is_overdue(self):
        """Проверка просрочки проекта"""
        if self.status in [self.Status.COMPLETED, self.Status.CANCELLED]:
            return False
        
        today = timezone.now().date()
        return self.end_date < today
    
    @property
    def days_remaining(self):
        """Количество дней до завершения проекта"""
        if self.status in [self.Status.COMPLETED, self.Status.CANCELLED]:
            return 0
        
        today = timezone.now().date()
        if self.end_date >= today:
            return (self.end_date - today).days
        return -(today - self.end_date).days  # Отрицательное значение для просроченных
    
    def get_defects_stats(self):
        """Статистика дефектов по проекту"""
        defects = self.defects.all()
        
        return {
            'total': defects.count(),
            'new': defects.filter(status='new').count(),
            'in_progress': defects.filter(status='in_progress').count(),
            'review': defects.filter(status='review').count(),
            'closed': defects.filter(status='closed').count(),
            'cancelled': defects.filter(status='cancelled').count(),
            'critical': defects.filter(priority='critical').count(),
            'high': defects.filter(priority='high').count(),
        }
    
    def add_member(self, user, role='member'):
        """Добавление участника в проект"""
        member, created = ProjectMember.objects.get_or_create(
            project=self,
            user=user,
            defaults={'role': role}
        )
        return member, created
    
    def remove_member(self, user):
        """Удаление участника из проекта"""
        ProjectMember.objects.filter(project=self, user=user).delete()
    
    def is_member(self, user):
        """Проверка участия пользователя в проекте"""
        return self.members.filter(id=user.id).exists()


class ProjectMember(models.Model):
    """
    Модель участника проекта
    """
    
    class Role(models.TextChoices):
        MANAGER = 'manager', 'Менеджер'
        ENGINEER = 'engineer', 'Инженер'
        OBSERVER = 'observer', 'Наблюдатель'
        COORDINATOR = 'coordinator', 'Координатор'
    
    project = models.ForeignKey(
        Project,
        on_delete=models.CASCADE,
        related_name='project_members',
        verbose_name='Проект'
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='project_memberships',
        verbose_name='Пользователь'
    )
    role = models.CharField(
        verbose_name='Роль в проекте',
        max_length=20,
        choices=Role.choices,
        default=Role.ENGINEER,
        help_text='Роль пользователя в проекте'
    )
    joined_at = models.DateTimeField(
        verbose_name='Дата присоединения',
        auto_now_add=True,
        help_text='Дата присоединения к проекту'
    )
    is_active = models.BooleanField(
        verbose_name='Активный участник',
        default=True,
        help_text='Активен ли участник в проекте'
    )
    
    class Meta:
        verbose_name = 'Участник проекта'
        verbose_name_plural = 'Участники проектов'
        unique_together = ['project', 'user']
        indexes = [
            models.Index(fields=['project', 'is_active']),
            models.Index(fields=['user', 'is_active']),
        ]
    
    def __str__(self):
        return f"{self.user.get_full_name()} в {self.project.name}"


class ProjectStage(BaseModel):
    """
    Модель этапа проекта
    """
    
    class Status(models.TextChoices):
        NOT_STARTED = 'not_started', 'Не начат'
        IN_PROGRESS = 'in_progress', 'В работе'
        COMPLETED = 'completed', 'Завершён'
        ON_HOLD = 'on_hold', 'Приостановлен'
        CANCELLED = 'cancelled', 'Отменён'
    
    project = models.ForeignKey(
        Project,
        on_delete=models.CASCADE,
        related_name='stages',
        verbose_name='Проект'
    )
    name = models.CharField(
        verbose_name='Название этапа',
        max_length=200,
        help_text='Название этапа работ'
    )
    description = models.TextField(
        verbose_name='Описание этапа',
        blank=True,
        help_text='Подробное описание этапа'
    )
    order = models.PositiveSmallIntegerField(
        verbose_name='Порядок',
        default=0,
        help_text='Порядок выполнения этапа'
    )
    
    # Даты
    start_date = models.DateField(
        verbose_name='Дата начала',
        help_text='Плановая дата начала этапа'
    )
    end_date = models.DateField(
        verbose_name='Дата завершения',
        help_text='Плановая дата завершения этапа'
    )
    actual_start_date = models.DateField(
        verbose_name='Фактическая дата начала',
        null=True,
        blank=True,
        help_text='Фактическая дата начала этапа'
    )
    actual_end_date = models.DateField(
        verbose_name='Фактическая дата завершения',
        null=True,
        blank=True,
        help_text='Фактическая дата завершения этапа'
    )
    
    # Ответственный и статус
    responsible = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='responsible_stages',
        verbose_name='Ответственный',
        help_text='Ответственный за этап'
    )
    status = models.CharField(
        verbose_name='Статус этапа',
        max_length=20,
        choices=Status.choices,
        default=Status.NOT_STARTED,
        help_text='Текущий статус этапа'
    )
    
    # Дополнительная информация
    estimated_hours = models.PositiveIntegerField(
        verbose_name='Плановые часы',
        null=True,
        blank=True,
        help_text='Планируемое количество часов на этап'
    )
    actual_hours = models.PositiveIntegerField(
        verbose_name='Фактические часы',
        null=True,
        blank=True,
        help_text='Фактически затраченные часы'
    )
    completion_percentage = models.PositiveSmallIntegerField(
        verbose_name='Процент выполнения',
        default=0,
        help_text='Процент выполнения этапа (0-100)'
    )
    
    class Meta:
        verbose_name = 'Этап проекта'
        verbose_name_plural = 'Этапы проектов'
        ordering = ['project', 'order', 'start_date']
        unique_together = ['project', 'order']
        indexes = [
            models.Index(fields=['project', 'status']),
            models.Index(fields=['responsible']),
            models.Index(fields=['start_date', 'end_date']),
        ]
    
    def __str__(self):
        return f"{self.project.name} - {self.name}"
    
    def clean(self):
        """Валидация модели"""
        super().clean()
        
        # Проверяем даты
        if self.start_date and self.end_date:
            if self.start_date > self.end_date:
                raise ValidationError('Дата начала не может быть позже даты завершения')
        
        # Проверяем, что даты этапа входят в рамки проекта
        if self.project_id:
            if self.start_date < self.project.start_date:
                raise ValidationError('Дата начала этапа не может быть раньше даты начала проекта')
            if self.end_date > self.project.end_date:
                raise ValidationError('Дата завершения этапа не может быть позже даты завершения проекта')
        
        # Проверяем процент выполнения
        if self.completion_percentage < 0 or self.completion_percentage > 100:
            raise ValidationError('Процент выполнения должен быть от 0 до 100')
    
    @property
    def duration_planned(self):
        """Планируемая продолжительность этапа в днях"""
        if self.start_date and self.end_date:
            return (self.end_date - self.start_date).days
        return None
    
    @property
    def duration_actual(self):
        """Фактическая продолжительность этапа в днях"""
        if self.actual_start_date and self.actual_end_date:
            return (self.actual_end_date - self.actual_start_date).days
        return None
    
    @property
    def is_overdue(self):
        """Проверка просрочки этапа"""
        if self.status in [self.Status.COMPLETED, self.Status.CANCELLED]:
            return False
        
        today = timezone.now().date()
        return self.end_date < today
    
    @property
    def days_remaining(self):
        """Количество дней до завершения этапа"""
        if self.status in [self.Status.COMPLETED, self.Status.CANCELLED]:
            return 0
        
        today = timezone.now().date()
        if self.end_date >= today:
            return (self.end_date - today).days
        return -(today - self.end_date).days


class ProjectTemplate(BaseModel):
    """
    Модель шаблона проекта для быстрого создания типовых проектов
    """
    name = models.CharField(
        verbose_name='Название шаблона',
        max_length=200,
        unique=True,
        help_text='Название шаблона проекта'
    )
    description = models.TextField(
        verbose_name='Описание шаблона',
        help_text='Описание назначения шаблона'
    )
    building_type = models.CharField(
        verbose_name='Тип здания',
        max_length=100,
        choices=[
            ('residential', 'Жилое'),
            ('commercial', 'Коммерческое'),
            ('industrial', 'Промышленное'),
            ('infrastructure', 'Инфраструктура'),
            ('other', 'Другое'),
        ],
        help_text='Тип строительного объекта'
    )
    is_active = models.BooleanField(
        verbose_name='Активный',
        default=True,
        help_text='Доступен ли шаблон для использования'
    )
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='created_templates',
        verbose_name='Создал'
    )
    
    class Meta:
        verbose_name = 'Шаблон проекта'
        verbose_name_plural = 'Шаблоны проектов'
        ordering = ['name']
    
    def __str__(self):
        return self.name


class ProjectStageTemplate(models.Model):
    """
    Модель шаблона этапа проекта
    """
    template = models.ForeignKey(
        ProjectTemplate,
        on_delete=models.CASCADE,
        related_name='stage_templates',
        verbose_name='Шаблон проекта'
    )
    name = models.CharField(
        verbose_name='Название этапа',
        max_length=200,
        help_text='Название этапа работ'
    )
    description = models.TextField(
        verbose_name='Описание этапа',
        blank=True,
        help_text='Описание этапа'
    )
    order = models.PositiveSmallIntegerField(
        verbose_name='Порядок',
        help_text='Порядок выполнения этапа'
    )
    estimated_days = models.PositiveIntegerField(
        verbose_name='Планируемая длительность (дни)',
        help_text='Планируемая продолжительность этапа в днях'
    )
    estimated_hours = models.PositiveIntegerField(
        verbose_name='Плановые часы',
        null=True,
        blank=True,
        help_text='Планируемое количество часов на этап'
    )
    
    class Meta:
        verbose_name = 'Шаблон этапа'
        verbose_name_plural = 'Шаблоны этапов'
        ordering = ['template', 'order']
        unique_together = ['template', 'order']
    
    def __str__(self):
        return f"{self.template.name} - {self.name}"
