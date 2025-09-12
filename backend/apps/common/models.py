"""
Общие модели для всех приложений
"""

from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone

User = get_user_model()


class BaseModel(models.Model):
    """
    Базовая модель с общими полями
    """
    created_at = models.DateTimeField(
        verbose_name='Дата создания',
        auto_now_add=True
    )
    updated_at = models.DateTimeField(
        verbose_name='Дата обновления',
        auto_now=True
    )
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='%(class)s_created',
        verbose_name='Создано пользователем'
    )
    updated_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='%(class)s_updated',
        verbose_name='Обновлено пользователем'
    )
    
    class Meta:
        abstract = True


class Notification(BaseModel):
    """
    Модель уведомлений
    """
    
    class NotificationType(models.TextChoices):
        DEFECT_CREATED = 'defect_created', 'Создан дефект'
        DEFECT_ASSIGNED = 'defect_assigned', 'Дефект назначен'
        DEFECT_STATUS_CHANGED = 'defect_status_changed', 'Изменён статус дефекта'
        DEFECT_DUE_SOON = 'defect_due_soon', 'Скоро истекает срок дефекта'
        DEFECT_OVERDUE = 'defect_overdue', 'Просрочен дефект'
        COMMENT_ADDED = 'comment_added', 'Добавлен комментарий'
        PROJECT_UPDATED = 'project_updated', 'Обновлён проект'
        USER_MENTIONED = 'user_mentioned', 'Упоминание пользователя'
        SYSTEM_ALERT = 'system_alert', 'Системное уведомление'
    
    class Priority(models.TextChoices):
        LOW = 'low', 'Низкий'
        NORMAL = 'normal', 'Обычный'
        HIGH = 'high', 'Высокий'
        URGENT = 'urgent', 'Срочный'
    
    class Status(models.TextChoices):
        PENDING = 'pending', 'Ожидает отправки'
        SENT = 'sent', 'Отправлено'
        DELIVERED = 'delivered', 'Доставлено'
        FAILED = 'failed', 'Ошибка отправки'
        READ = 'read', 'Прочитано'
    
    # Основная информация
    recipient = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='notifications',
        verbose_name='Получатель'
    )
    notification_type = models.CharField(
        verbose_name='Тип уведомления',
        max_length=50,
        choices=NotificationType.choices
    )
    title = models.CharField(
        verbose_name='Заголовок',
        max_length=200
    )
    message = models.TextField(
        verbose_name='Сообщение'
    )
    
    # Метаданные
    priority = models.CharField(
        verbose_name='Приоритет',
        max_length=20,
        choices=Priority.choices,
        default=Priority.NORMAL
    )
    status = models.CharField(
        verbose_name='Статус',
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING
    )
    
    # Связанные объекты
    related_object_type = models.CharField(
        verbose_name='Тип связанного объекта',
        max_length=50,
        blank=True,
        help_text='Тип объекта, к которому относится уведомление'
    )
    related_object_id = models.PositiveIntegerField(
        verbose_name='ID связанного объекта',
        null=True,
        blank=True,
        help_text='ID объекта, к которому относится уведомление'
    )
    
    # Настройки отправки
    send_email = models.BooleanField(
        verbose_name='Отправить по email',
        default=True
    )
    send_sms = models.BooleanField(
        verbose_name='Отправить по SMS',
        default=False
    )
    send_push = models.BooleanField(
        verbose_name='Отправить push уведомление',
        default=True
    )
    
    # Временные метки
    sent_at = models.DateTimeField(
        verbose_name='Время отправки',
        null=True,
        blank=True
    )
    read_at = models.DateTimeField(
        verbose_name='Время прочтения',
        null=True,
        blank=True
    )
    
    # Дополнительные данные
    metadata = models.JSONField(
        verbose_name='Дополнительные данные',
        default=dict,
        blank=True,
        help_text='Дополнительные данные в формате JSON'
    )
    
    class Meta:
        verbose_name = 'Уведомление'
        verbose_name_plural = 'Уведомления'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['recipient', 'status']),
            models.Index(fields=['notification_type']),
            models.Index(fields=['created_at']),
            models.Index(fields=['related_object_type', 'related_object_id']),
        ]
    
    def __str__(self):
        return f"{self.title} - {self.recipient.get_full_name()}"
    
    def mark_as_read(self):
        """Отмечает уведомление как прочитанное"""
        if not self.read_at:
            self.read_at = timezone.now()
            self.status = self.Status.READ
            self.save(update_fields=['read_at', 'status'])
    
    def mark_as_sent(self):
        """Отмечает уведомление как отправленное"""
        self.sent_at = timezone.now()
        self.status = self.Status.SENT
        self.save(update_fields=['sent_at', 'status'])
    
    def mark_as_delivered(self):
        """Отмечает уведомление как доставленное"""
        self.status = self.Status.DELIVERED
        self.save(update_fields=['status'])
    
    def mark_as_failed(self):
        """Отмечает уведомление как неудачное"""
        self.status = self.Status.FAILED
        self.save(update_fields=['status'])
    
    @property
    def is_read(self):
        """Проверяет, прочитано ли уведомление"""
        return self.read_at is not None
    
    @property
    def is_sent(self):
        """Проверяет, отправлено ли уведомление"""
        return self.status in [self.Status.SENT, self.Status.DELIVERED, self.Status.READ]


class NotificationTemplate(BaseModel):
    """
    Шаблоны уведомлений
    """
    
    class Channel(models.TextChoices):
        EMAIL = 'email', 'Email'
        SMS = 'sms', 'SMS'
        PUSH = 'push', 'Push уведомление'
        IN_APP = 'in_app', 'В приложении'
    
    name = models.CharField(
        verbose_name='Название шаблона',
        max_length=100,
        unique=True
    )
    notification_type = models.CharField(
        verbose_name='Тип уведомления',
        max_length=50,
        choices=Notification.NotificationType.choices
    )
    channel = models.CharField(
        verbose_name='Канал отправки',
        max_length=20,
        choices=Channel.choices
    )
    
    # Шаблоны
    subject_template = models.CharField(
        verbose_name='Шаблон темы',
        max_length=200,
        blank=True,
        help_text='Шаблон темы (для email)'
    )
    message_template = models.TextField(
        verbose_name='Шаблон сообщения',
        help_text='Шаблон сообщения с переменными'
    )
    
    # Настройки
    is_active = models.BooleanField(
        verbose_name='Активен',
        default=True
    )
    priority = models.CharField(
        verbose_name='Приоритет по умолчанию',
        max_length=20,
        choices=Notification.Priority.choices,
        default=Notification.Priority.NORMAL
    )
    
    # Переменные шаблона
    available_variables = models.JSONField(
        verbose_name='Доступные переменные',
        default=list,
        blank=True,
        help_text='Список доступных переменных для шаблона'
    )
    
    class Meta:
        verbose_name = 'Шаблон уведомления'
        verbose_name_plural = 'Шаблоны уведомлений'
        unique_together = ['notification_type', 'channel']
    
    def __str__(self):
        return f"{self.name} ({self.get_channel_display()})"
    
    def render_message(self, context):
        """Рендерит сообщение с использованием контекста"""
        from django.template import Template, Context
        template = Template(self.message_template)
        return template.render(Context(context))
    
    def render_subject(self, context):
        """Рендерит тему с использованием контекста"""
        if not self.subject_template:
            return ""
        from django.template import Template, Context
        template = Template(self.subject_template)
        return template.render(Context(context))


class NotificationSettings(BaseModel):
    """
    Настройки уведомлений пользователя
    """
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='notification_settings',
        verbose_name='Пользователь'
    )
    
    # Email настройки
    email_enabled = models.BooleanField(
        verbose_name='Email уведомления включены',
        default=True
    )
    email_frequency = models.CharField(
        verbose_name='Частота email уведомлений',
        max_length=20,
        choices=[
            ('immediate', 'Мгновенно'),
            ('hourly', 'Каждый час'),
            ('daily', 'Ежедневно'),
            ('weekly', 'Еженедельно'),
        ],
        default='immediate'
    )
    
    # SMS настройки
    sms_enabled = models.BooleanField(
        verbose_name='SMS уведомления включены',
        default=False
    )
    sms_phone = models.CharField(
        verbose_name='Номер телефона для SMS',
        max_length=20,
        blank=True
    )
    
    # Push настройки
    push_enabled = models.BooleanField(
        verbose_name='Push уведомления включены',
        default=True
    )
    
    # Настройки по типам уведомлений
    notification_preferences = models.JSONField(
        verbose_name='Настройки по типам',
        default=dict,
        blank=True,
        help_text='Настройки для каждого типа уведомлений'
    )
    
    # Время тишины
    quiet_hours_start = models.TimeField(
        verbose_name='Начало времени тишины',
        null=True,
        blank=True,
        help_text='Время начала периода тишины (не отправлять уведомления)'
    )
    quiet_hours_end = models.TimeField(
        verbose_name='Конец времени тишины',
        null=True,
        blank=True,
        help_text='Время окончания периода тишины'
    )
    
    class Meta:
        verbose_name = 'Настройки уведомлений'
        verbose_name_plural = 'Настройки уведомлений'
    
    def __str__(self):
        return f"Настройки уведомлений {self.user.get_full_name()}"
    
    def is_quiet_time(self):
        """Проверяет, находится ли текущее время в периоде тишины"""
        if not self.quiet_hours_start or not self.quiet_hours_end:
            return False
        
        now = timezone.now().time()
        return self.quiet_hours_start <= now <= self.quiet_hours_end
    
    def should_send_notification(self, notification_type, channel):
        """Проверяет, нужно ли отправлять уведомление"""
        # Проверяем время тишины
        if self.is_quiet_time() and channel in ['push', 'sms']:
            return False
        
        # Проверяем общие настройки канала
        if channel == 'email' and not self.email_enabled:
            return False
        if channel == 'sms' and not self.sms_enabled:
            return False
        if channel == 'push' and not self.push_enabled:
            return False
        
        # Проверяем настройки по типу уведомления
        type_prefs = self.notification_preferences.get(notification_type, {})
        return type_prefs.get(channel, True)


class AuditLog(BaseModel):
    """
    Модель для аудита действий пользователей
    """
    
    class ActionType(models.TextChoices):
        CREATE = 'create', 'Создание'
        UPDATE = 'update', 'Обновление'
        DELETE = 'delete', 'Удаление'
        LOGIN = 'login', 'Вход в систему'
        LOGOUT = 'logout', 'Выход из системы'
        PASSWORD_CHANGE = 'password_change', 'Смена пароля'
        PERMISSION_CHANGE = 'permission_change', 'Изменение прав'
        STATUS_CHANGE = 'status_change', 'Изменение статуса'
        ASSIGNMENT = 'assignment', 'Назначение'
        FILE_UPLOAD = 'file_upload', 'Загрузка файла'
        FILE_DELETE = 'file_delete', 'Удаление файла'
        EXPORT = 'export', 'Экспорт данных'
        IMPORT = 'import', 'Импорт данных'
    
    user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='audit_logs',
        verbose_name='Пользователь'
    )
    action = models.CharField(
        verbose_name='Действие',
        max_length=50,
        choices=ActionType.choices
    )
    object_type = models.CharField(
        verbose_name='Тип объекта',
        max_length=50,
        blank=True,
        help_text='Тип объекта, с которым выполнялось действие'
    )
    object_id = models.PositiveIntegerField(
        verbose_name='ID объекта',
        null=True,
        blank=True,
        help_text='ID объекта, с которым выполнялось действие'
    )
    object_repr = models.CharField(
        verbose_name='Представление объекта',
        max_length=200,
        blank=True,
        help_text='Строковое представление объекта'
    )
    details = models.JSONField(
        verbose_name='Детали',
        default=dict,
        blank=True,
        help_text='Дополнительные детали действия'
    )
    ip_address = models.GenericIPAddressField(
        verbose_name='IP адрес',
        null=True,
        blank=True
    )
    user_agent = models.TextField(
        verbose_name='User Agent',
        blank=True
    )
    
    class Meta:
        verbose_name = 'Запись аудита'
        verbose_name_plural = 'Записи аудита'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'action']),
            models.Index(fields=['object_type', 'object_id']),
            models.Index(fields=['created_at']),
            models.Index(fields=['ip_address']),
        ]
    
    def __str__(self):
        if self.user:
            return f"{self.user.get_full_name()} - {self.get_action_display()}"
        return f"Система - {self.get_action_display()}"