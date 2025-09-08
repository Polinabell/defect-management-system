"""
Модели для управления дефектами
"""

from django.db import models
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.utils import timezone
from apps.common.models import BaseModel, Priority
from apps.common.utils import generate_file_path
from apps.projects.models import Project, ProjectStage

User = get_user_model()


def defect_image_path(instance, filename):
    """Генерация пути для изображений дефектов"""
    return generate_file_path(instance, filename, 'defects/images')


def defect_document_path(instance, filename):
    """Генерация пути для документов дефектов"""
    return generate_file_path(instance, filename, 'defects/documents')


class DefectCategory(BaseModel):
    """
    Модель категории дефектов
    """
    name = models.CharField(
        verbose_name='Название категории',
        max_length=100,
        unique=True,
        help_text='Название категории дефектов'
    )
    description = models.TextField(
        verbose_name='Описание категории',
        blank=True,
        help_text='Подробное описание категории'
    )
    color = models.CharField(
        verbose_name='Цвет категории',
        max_length=7,
        default='#007bff',
        help_text='Цвет для отображения в интерфейсе (hex)'
    )
    icon = models.CharField(
        verbose_name='Иконка категории',
        max_length=50,
        blank=True,
        help_text='Название иконки для отображения'
    )
    is_active = models.BooleanField(
        verbose_name='Активная',
        default=True,
        help_text='Доступна ли категория для использования'
    )
    order = models.PositiveSmallIntegerField(
        verbose_name='Порядок сортировки',
        default=0,
        help_text='Порядок отображения в списках'
    )
    
    class Meta:
        verbose_name = 'Категория дефекта'
        verbose_name_plural = 'Категории дефектов'
        ordering = ['order', 'name']
    
    def __str__(self):
        return self.name


class Defect(BaseModel):
    """
    Модель дефекта
    """
    
    class Status(models.TextChoices):
        NEW = 'new', 'Новый'
        IN_PROGRESS = 'in_progress', 'В работе'
        REVIEW = 'review', 'На проверке'
        CLOSED = 'closed', 'Закрыт'
        CANCELLED = 'cancelled', 'Отменён'
    
    # Основная информация
    title = models.CharField(
        verbose_name='Заголовок дефекта',
        max_length=200,
        help_text='Краткое описание дефекта'
    )
    description = models.TextField(
        verbose_name='Описание дефекта',
        help_text='Подробное описание дефекта'
    )
    defect_number = models.CharField(
        verbose_name='Номер дефекта',
        max_length=50,
        unique=True,
        blank=True,
        help_text='Автоматически генерируемый номер дефекта'
    )
    
    # Связи с проектом
    project = models.ForeignKey(
        Project,
        on_delete=models.CASCADE,
        related_name='defects',
        verbose_name='Проект',
        help_text='Проект, к которому относится дефект'
    )
    stage = models.ForeignKey(
        ProjectStage,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='defects',
        verbose_name='Этап проекта',
        help_text='Этап проекта, на котором выявлен дефект'
    )
    
    # Категория и приоритет
    category = models.ForeignKey(
        DefectCategory,
        on_delete=models.PROTECT,
        related_name='defects',
        verbose_name='Категория',
        help_text='Категория дефекта'
    )
    priority = models.CharField(
        verbose_name='Приоритет',
        max_length=20,
        choices=Priority.choices,
        default=Priority.MEDIUM,
        help_text='Приоритет устранения дефекта'
    )
    
    # Местоположение и детали
    location = models.TextField(
        verbose_name='Местоположение',
        help_text='Детальное описание местоположения дефекта'
    )
    floor = models.CharField(
        verbose_name='Этаж',
        max_length=20,
        blank=True,
        help_text='Этаж, на котором находится дефект'
    )
    room = models.CharField(
        verbose_name='Помещение',
        max_length=100,
        blank=True,
        help_text='Помещение, в котором находится дефект'
    )
    coordinates_x = models.DecimalField(
        verbose_name='Координата X',
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        help_text='X координата на плане (в пикселях или метрах)'
    )
    coordinates_y = models.DecimalField(
        verbose_name='Координата Y',
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        help_text='Y координата на плане (в пикселях или метрах)'
    )
    
    # Ответственные лица
    author = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name='authored_defects',
        verbose_name='Автор',
        help_text='Пользователь, создавший дефект'
    )
    assignee = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='assigned_defects',
        verbose_name='Исполнитель',
        help_text='Пользователь, ответственный за устранение дефекта'
    )
    reviewer = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='reviewed_defects',
        verbose_name='Проверяющий',
        help_text='Пользователь, проверяющий устранение дефекта'
    )
    
    # Статус и даты
    status = models.CharField(
        verbose_name='Статус дефекта',
        max_length=20,
        choices=Status.choices,
        default=Status.NEW,
        help_text='Текущий статус дефекта'
    )
    due_date = models.DateField(
        verbose_name='Срок устранения',
        null=True,
        blank=True,
        help_text='Плановая дата устранения дефекта'
    )
    assigned_at = models.DateTimeField(
        verbose_name='Дата назначения',
        null=True,
        blank=True,
        help_text='Дата назначения исполнителя'
    )
    started_at = models.DateTimeField(
        verbose_name='Дата начала работ',
        null=True,
        blank=True,
        help_text='Дата начала работ по устранению'
    )
    completed_at = models.DateTimeField(
        verbose_name='Дата завершения',
        null=True,
        blank=True,
        help_text='Дата завершения работ по устранению'
    )
    closed_at = models.DateTimeField(
        verbose_name='Дата закрытия',
        null=True,
        blank=True,
        help_text='Дата закрытия дефекта после проверки'
    )
    
    # Дополнительная информация
    severity = models.CharField(
        verbose_name='Серьёзность',
        max_length=20,
        choices=[
            ('cosmetic', 'Косметический'),
            ('minor', 'Незначительный'),
            ('major', 'Значительный'),
            ('critical', 'Критический'),
            ('blocking', 'Блокирующий'),
        ],
        default='minor',
        help_text='Серьёзность дефекта'
    )
    estimated_cost = models.DecimalField(
        verbose_name='Ориентировочная стоимость устранения',
        max_digits=12,
        decimal_places=2,
        null=True,
        blank=True,
        help_text='Ориентировочная стоимость устранения в рублях'
    )
    actual_cost = models.DecimalField(
        verbose_name='Фактическая стоимость устранения',
        max_digits=12,
        decimal_places=2,
        null=True,
        blank=True,
        help_text='Фактическая стоимость устранения в рублях'
    )
    
    # Дополнительные поля для работы
    resolution_description = models.TextField(
        verbose_name='Описание решения',
        blank=True,
        help_text='Описание способа устранения дефекта'
    )
    prevention_measures = models.TextField(
        verbose_name='Меры предотвращения',
        blank=True,
        help_text='Меры для предотвращения подобных дефектов в будущем'
    )
    
    # Метаданные
    external_id = models.CharField(
        verbose_name='Внешний ID',
        max_length=100,
        blank=True,
        help_text='ID дефекта во внешней системе'
    )
    
    class Meta:
        verbose_name = 'Дефект'
        verbose_name_plural = 'Дефекты'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['project', 'status']),
            models.Index(fields=['assignee', 'status']),
            models.Index(fields=['author']),
            models.Index(fields=['category']),
            models.Index(fields=['priority', 'status']),
            models.Index(fields=['due_date']),
            models.Index(fields=['defect_number']),
        ]
        constraints = [
            models.CheckConstraint(
                check=models.Q(estimated_cost__gte=0),
                name='positive_estimated_cost'
            ),
            models.CheckConstraint(
                check=models.Q(actual_cost__gte=0),
                name='positive_actual_cost'
            ),
        ]
    
    def __str__(self):
        return f"{self.defect_number} - {self.title}"
    
    def save(self, *args, **kwargs):
        """Переопределяем save для автогенерации номера дефекта"""
        if not self.defect_number:
            self.defect_number = self._generate_defect_number()
        super().save(*args, **kwargs)
    
    def _generate_defect_number(self):
        """Генерация уникального номера дефекта"""
        year = timezone.now().year
        project_prefix = self.project.slug[:3].upper() if self.project.slug else 'DEF'
        
        # Находим последний номер дефекта для данного проекта в текущем году
        last_defect = Defect.objects.filter(
            project=self.project,
            defect_number__startswith=f"{project_prefix}-{year}-"
        ).order_by('-defect_number').first()
        
        if last_defect:
            try:
                last_number = int(last_defect.defect_number.split('-')[-1])
                next_number = last_number + 1
            except (ValueError, IndexError):
                next_number = 1
        else:
            next_number = 1
        
        return f"{project_prefix}-{year}-{next_number:04d}"
    
    def clean(self):
        """Валидация модели"""
        super().clean()
        
        # Проверяем, что этап принадлежит проекту
        if self.stage and self.stage.project != self.project:
            raise ValidationError('Этап должен принадлежать выбранному проекту')
        
        # Проверяем, что исполнитель является участником проекта
        if self.assignee and not self.project.is_member(self.assignee):
            raise ValidationError('Исполнитель должен быть участником проекта')
        
        # Проверяем срок устранения
        if self.due_date and self.due_date < timezone.now().date():
            if self.status == self.Status.NEW:
                raise ValidationError('Срок устранения не может быть в прошлом')
    
    @property
    def is_overdue(self):
        """Проверка просрочки дефекта"""
        if self.status in [self.Status.CLOSED, self.Status.CANCELLED]:
            return False
        
        if self.due_date:
            return timezone.now().date() > self.due_date
        return False
    
    @property
    def days_remaining(self):
        """Количество дней до срока устранения"""
        if not self.due_date or self.status in [self.Status.CLOSED, self.Status.CANCELLED]:
            return None
        
        today = timezone.now().date()
        if self.due_date >= today:
            return (self.due_date - today).days
        return -(today - self.due_date).days  # Отрицательное значение для просроченных
    
    @property
    def resolution_time(self):
        """Время решения дефекта в часах"""
        if self.closed_at and self.created_at:
            return (self.closed_at - self.created_at).total_seconds() / 3600
        return None
    
    def can_transition_to(self, new_status, user):
        """Проверка возможности смены статуса"""
        current_status = self.status
        
        # Правила переходов между статусами
        allowed_transitions = {
            self.Status.NEW: [self.Status.IN_PROGRESS, self.Status.CANCELLED],
            self.Status.IN_PROGRESS: [self.Status.REVIEW, self.Status.CANCELLED],
            self.Status.REVIEW: [self.Status.CLOSED, self.Status.IN_PROGRESS],
            self.Status.CLOSED: [],  # Закрытый дефект нельзя изменить
            self.Status.CANCELLED: [self.Status.NEW],  # Отменённый можно вернуть в новый
        }
        
        if new_status not in allowed_transitions.get(current_status, []):
            return False, f"Нельзя перевести дефект из статуса '{current_status}' в '{new_status}'"
        
        # Проверка прав пользователя
        if new_status == self.Status.IN_PROGRESS:
            if not (self.assignee == user or self.project.manager == user or user.is_admin):
                return False, "Только исполнитель или менеджер проекта может взять дефект в работу"
        
        if new_status == self.Status.REVIEW:
            if not (self.assignee == user or user.is_admin):
                return False, "Только исполнитель может отправить дефект на проверку"
        
        if new_status == self.Status.CLOSED:
            if not (self.reviewer == user or self.project.manager == user or user.is_admin):
                return False, "Только проверяющий или менеджер проекта может закрыть дефект"
        
        return True, ""
    
    def change_status(self, new_status, user, comment=None):
        """Изменение статуса дефекта"""
        can_change, error_message = self.can_transition_to(new_status, user)
        
        if not can_change:
            raise ValidationError(error_message)
        
        old_status = self.status
        self.status = new_status
        
        # Устанавливаем соответствующие даты
        now = timezone.now()
        
        if new_status == self.Status.IN_PROGRESS:
            if not self.started_at:
                self.started_at = now
        elif new_status == self.Status.REVIEW:
            self.completed_at = now
        elif new_status == self.Status.CLOSED:
            self.closed_at = now
            if not self.reviewer:
                self.reviewer = user
        
        self.save()
        
        # Добавляем комментарий о смене статуса
        DefectComment.objects.create(
            defect=self,
            author=user,
            content=comment or f"Статус изменён с '{old_status}' на '{new_status}'",
            comment_type=DefectComment.Type.STATUS_CHANGE
        )
    
    def assign_to(self, assignee, due_date=None, user=None):
        """Назначение исполнителя"""
        self.assignee = assignee
        self.assigned_at = timezone.now()
        
        if due_date:
            self.due_date = due_date
        
        if self.status == self.Status.NEW:
            self.status = self.Status.IN_PROGRESS
        
        self.save()
        
        # Добавляем комментарий о назначении
        if user:
            comment_text = f"Дефект назначен пользователю {assignee.get_full_name()}"
            if due_date:
                comment_text += f" до {due_date.strftime('%d.%m.%Y')}"
            
            DefectComment.objects.create(
                defect=self,
                author=user,
                content=comment_text,
                comment_type=DefectComment.Type.ASSIGNMENT
            )


class DefectFile(BaseModel):
    """
    Модель файла дефекта (изображения или документы)
    """
    
    class FileType(models.TextChoices):
        IMAGE = 'image', 'Изображение'
        DOCUMENT = 'document', 'Документ'
        VIDEO = 'video', 'Видео'
        AUDIO = 'audio', 'Аудио'
        OTHER = 'other', 'Другое'
    
    defect = models.ForeignKey(
        Defect,
        on_delete=models.CASCADE,
        related_name='files',
        verbose_name='Дефект'
    )
    file = models.FileField(
        verbose_name='Файл',
        upload_to=defect_image_path,
        help_text='Загруженный файл'
    )
    filename = models.CharField(
        verbose_name='Имя файла',
        max_length=255,
        help_text='Оригинальное имя файла'
    )
    file_type = models.CharField(
        verbose_name='Тип файла',
        max_length=20,
        choices=FileType.choices,
        help_text='Тип загруженного файла'
    )
    file_size = models.PositiveIntegerField(
        verbose_name='Размер файла',
        help_text='Размер файла в байтах'
    )
    mime_type = models.CharField(
        verbose_name='MIME тип',
        max_length=100,
        blank=True,
        help_text='MIME тип файла'
    )
    description = models.TextField(
        verbose_name='Описание файла',
        blank=True,
        help_text='Описание содержимого файла'
    )
    uploaded_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        verbose_name='Загружен пользователем'
    )
    is_main = models.BooleanField(
        verbose_name='Основное изображение',
        default=False,
        help_text='Является ли файл основным изображением дефекта'
    )
    
    class Meta:
        verbose_name = 'Файл дефекта'
        verbose_name_plural = 'Файлы дефектов'
        ordering = ['-is_main', 'created_at']
    
    def __str__(self):
        return f"{self.defect.defect_number} - {self.filename}"
    
    def save(self, *args, **kwargs):
        """Переопределяем save для определения типа файла"""
        if self.file and not self.file_type:
            self.file_type = self._determine_file_type()
        
        if self.file and not self.filename:
            self.filename = self.file.name
        
        if self.file:
            self.file_size = self.file.size
        
        super().save(*args, **kwargs)
    
    def _determine_file_type(self):
        """Определение типа файла по MIME типу"""
        if not self.mime_type:
            return self.FileType.OTHER
        
        if self.mime_type.startswith('image/'):
            return self.FileType.IMAGE
        elif self.mime_type.startswith('video/'):
            return self.FileType.VIDEO
        elif self.mime_type.startswith('audio/'):
            return self.FileType.AUDIO
        elif self.mime_type in ['application/pdf', 'application/msword', 
                               'application/vnd.openxmlformats-officedocument.wordprocessingml.document']:
            return self.FileType.DOCUMENT
        else:
            return self.FileType.OTHER


class DefectComment(BaseModel):
    """
    Модель комментария к дефекту
    """
    
    class Type(models.TextChoices):
        COMMENT = 'comment', 'Комментарий'
        STATUS_CHANGE = 'status_change', 'Изменение статуса'
        ASSIGNMENT = 'assignment', 'Назначение'
        RESOLUTION = 'resolution', 'Решение'
        REJECTION = 'rejection', 'Отклонение'
    
    defect = models.ForeignKey(
        Defect,
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name='Дефект'
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='defect_comments',
        verbose_name='Автор'
    )
    content = models.TextField(
        verbose_name='Содержание комментария',
        help_text='Текст комментария'
    )
    comment_type = models.CharField(
        verbose_name='Тип комментария',
        max_length=20,
        choices=Type.choices,
        default=Type.COMMENT,
        help_text='Тип комментария'
    )
    is_internal = models.BooleanField(
        verbose_name='Внутренний комментарий',
        default=False,
        help_text='Виден только участникам проекта'
    )
    reply_to = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='replies',
        verbose_name='Ответ на комментарий'
    )
    
    class Meta:
        verbose_name = 'Комментарий к дефекту'
        verbose_name_plural = 'Комментарии к дефектам'
        ordering = ['created_at']
        indexes = [
            models.Index(fields=['defect', 'created_at']),
            models.Index(fields=['author']),
        ]
    
    def __str__(self):
        return f"Комментарий к {self.defect.defect_number} от {self.author.get_full_name()}"


class DefectHistory(models.Model):
    """
    Модель истории изменений дефекта
    """
    defect = models.ForeignKey(
        Defect,
        on_delete=models.CASCADE,
        related_name='history',
        verbose_name='Дефект'
    )
    user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        verbose_name='Пользователь'
    )
    action = models.CharField(
        verbose_name='Действие',
        max_length=50,
        help_text='Тип выполненного действия'
    )
    field_name = models.CharField(
        verbose_name='Поле',
        max_length=50,
        blank=True,
        help_text='Название изменённого поля'
    )
    old_value = models.TextField(
        verbose_name='Старое значение',
        blank=True,
        help_text='Значение до изменения'
    )
    new_value = models.TextField(
        verbose_name='Новое значение',
        blank=True,
        help_text='Значение после изменения'
    )
    timestamp = models.DateTimeField(
        verbose_name='Время изменения',
        auto_now_add=True
    )
    ip_address = models.GenericIPAddressField(
        verbose_name='IP адрес',
        null=True,
        blank=True
    )
    
    class Meta:
        verbose_name = 'История изменений дефекта'
        verbose_name_plural = 'История изменений дефектов'
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['defect', 'timestamp']),
            models.Index(fields=['user']),
        ]
    
    def __str__(self):
        return f"{self.defect.defect_number} - {self.action} ({self.timestamp})"
