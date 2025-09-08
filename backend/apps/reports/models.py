"""
Модели для отчётов и аналитики
"""

from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone
from apps.common.models import BaseModel
from apps.projects.models import Project

User = get_user_model()


class ReportTemplate(BaseModel):
    """
    Модель шаблона отчёта
    """
    
    class ReportType(models.TextChoices):
        PROJECT_SUMMARY = 'project_summary', 'Сводка по проекту'
        DEFECTS_ANALYSIS = 'defects_analysis', 'Анализ дефектов'
        PERFORMANCE_REPORT = 'performance_report', 'Отчёт о производительности'
        TIMELINE_REPORT = 'timeline_report', 'Временной отчёт'
        CUSTOM = 'custom', 'Пользовательский'
    
    class OutputFormat(models.TextChoices):
        PDF = 'pdf', 'PDF'
        EXCEL = 'excel', 'Excel (XLSX)'
        CSV = 'csv', 'CSV'
        JSON = 'json', 'JSON'
    
    name = models.CharField(
        verbose_name='Название шаблона',
        max_length=200,
        help_text='Название шаблона отчёта'
    )
    description = models.TextField(
        verbose_name='Описание',
        blank=True,
        help_text='Описание назначения отчёта'
    )
    report_type = models.CharField(
        verbose_name='Тип отчёта',
        max_length=30,
        choices=ReportType.choices,
        help_text='Тип отчёта'
    )
    output_format = models.CharField(
        verbose_name='Формат вывода',
        max_length=10,
        choices=OutputFormat.choices,
        default=OutputFormat.PDF,
        help_text='Формат файла отчёта'
    )
    
    # Настройки фильтрации
    filter_config = models.JSONField(
        verbose_name='Конфигурация фильтров',
        default=dict,
        blank=True,
        help_text='JSON конфигурация фильтров для отчёта'
    )
    
    # Настройки отображения
    display_config = models.JSONField(
        verbose_name='Конфигурация отображения',
        default=dict,
        blank=True,
        help_text='JSON конфигурация полей и их отображения'
    )
    
    # Параметры
    is_public = models.BooleanField(
        verbose_name='Публичный шаблон',
        default=False,
        help_text='Доступен ли шаблон всем пользователям'
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
        related_name='created_report_templates',
        verbose_name='Создал'
    )
    
    class Meta:
        verbose_name = 'Шаблон отчёта'
        verbose_name_plural = 'Шаблоны отчётов'
        ordering = ['name']
        indexes = [
            models.Index(fields=['report_type']),
            models.Index(fields=['is_active']),
            models.Index(fields=['created_by']),
        ]
    
    def __str__(self):
        return self.name


class GeneratedReport(BaseModel):
    """
    Модель сгенерированного отчёта
    """
    
    class Status(models.TextChoices):
        PENDING = 'pending', 'Ожидает'
        PROCESSING = 'processing', 'Обрабатывается'
        COMPLETED = 'completed', 'Завершён'
        FAILED = 'failed', 'Ошибка'
        EXPIRED = 'expired', 'Истёк'
    
    template = models.ForeignKey(
        ReportTemplate,
        on_delete=models.CASCADE,
        related_name='generated_reports',
        verbose_name='Шаблон отчёта'
    )
    name = models.CharField(
        verbose_name='Название отчёта',
        max_length=200,
        help_text='Название сгенерированного отчёта'
    )
    description = models.TextField(
        verbose_name='Описание',
        blank=True,
        help_text='Описание содержимого отчёта'
    )
    
    # Параметры генерации
    project = models.ForeignKey(
        Project,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='reports',
        verbose_name='Проект',
        help_text='Проект для которого генерируется отчёт'
    )
    date_from = models.DateField(
        verbose_name='Дата начала периода',
        null=True,
        blank=True,
        help_text='Начальная дата для отчёта'
    )
    date_to = models.DateField(
        verbose_name='Дата окончания периода',
        null=True,
        blank=True,
        help_text='Конечная дата для отчёта'
    )
    filter_params = models.JSONField(
        verbose_name='Параметры фильтрации',
        default=dict,
        blank=True,
        help_text='JSON параметры фильтрации данных'
    )
    
    # Статус и результат
    status = models.CharField(
        verbose_name='Статус',
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING,
        help_text='Статус генерации отчёта'
    )
    file = models.FileField(
        verbose_name='Файл отчёта',
        upload_to='reports/%Y/%m/',
        blank=True,
        null=True,
        help_text='Сгенерированный файл отчёта'
    )
    file_size = models.PositiveIntegerField(
        verbose_name='Размер файла',
        null=True,
        blank=True,
        help_text='Размер файла в байтах'
    )
    
    # Метаданные генерации
    generated_by = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='generated_reports',
        verbose_name='Сгенерировал'
    )
    generated_at = models.DateTimeField(
        verbose_name='Время генерации',
        null=True,
        blank=True,
        help_text='Время завершения генерации'
    )
    processing_time = models.DurationField(
        verbose_name='Время обработки',
        null=True,
        blank=True,
        help_text='Время затраченное на генерацию'
    )
    error_message = models.TextField(
        verbose_name='Сообщение об ошибке',
        blank=True,
        help_text='Описание ошибки при генерации'
    )
    
    # Срок действия
    expires_at = models.DateTimeField(
        verbose_name='Истекает',
        null=True,
        blank=True,
        help_text='Дата истечения срока действия отчёта'
    )
    download_count = models.PositiveIntegerField(
        verbose_name='Количество скачиваний',
        default=0,
        help_text='Сколько раз был скачан отчёт'
    )
    
    class Meta:
        verbose_name = 'Сгенерированный отчёт'
        verbose_name_plural = 'Сгенерированные отчёты'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['status']),
            models.Index(fields=['generated_by']),
            models.Index(fields=['project']),
            models.Index(fields=['created_at']),
            models.Index(fields=['expires_at']),
        ]
    
    def __str__(self):
        return f"{self.name} ({self.status})"
    
    @property
    def is_expired(self):
        """Проверка истечения срока действия"""
        if self.expires_at:
            return timezone.now() > self.expires_at
        return False
    
    @property
    def formatted_file_size(self):
        """Форматированный размер файла"""
        if self.file_size:
            from apps.common.utils import format_file_size
            return format_file_size(self.file_size)
        return None
    
    def mark_downloaded(self):
        """Отметить скачивание отчёта"""
        self.download_count += 1
        self.save(update_fields=['download_count'])


class Dashboard(BaseModel):
    """
    Модель дашборда
    """
    
    class DashboardType(models.TextChoices):
        EXECUTIVE = 'executive', 'Руководительский'
        PROJECT_MANAGER = 'project_manager', 'Менеджера проекта'
        ENGINEER = 'engineer', 'Инженера'
        CUSTOM = 'custom', 'Пользовательский'
    
    name = models.CharField(
        verbose_name='Название дашборда',
        max_length=200,
        help_text='Название дашборда'
    )
    description = models.TextField(
        verbose_name='Описание',
        blank=True,
        help_text='Описание назначения дашборда'
    )
    dashboard_type = models.CharField(
        verbose_name='Тип дашборда',
        max_length=20,
        choices=DashboardType.choices,
        help_text='Тип дашборда'
    )
    
    # Конфигурация виджетов
    widgets_config = models.JSONField(
        verbose_name='Конфигурация виджетов',
        default=list,
        help_text='JSON конфигурация виджетов дашборда'
    )
    
    # Настройки доступа
    is_default = models.BooleanField(
        verbose_name='По умолчанию',
        default=False,
        help_text='Дашборд по умолчанию для данного типа'
    )
    is_public = models.BooleanField(
        verbose_name='Публичный',
        default=False,
        help_text='Доступен всем пользователям'
    )
    allowed_roles = models.JSONField(
        verbose_name='Разрешённые роли',
        default=list,
        help_text='Список ролей с доступом к дашборду'
    )
    
    # Автор
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='created_dashboards',
        verbose_name='Создал'
    )
    
    class Meta:
        verbose_name = 'Дашборд'
        verbose_name_plural = 'Дашборды'
        ordering = ['dashboard_type', 'name']
        indexes = [
            models.Index(fields=['dashboard_type']),
            models.Index(fields=['is_default']),
            models.Index(fields=['created_by']),
        ]
    
    def __str__(self):
        return f"{self.name} ({self.get_dashboard_type_display()})"


class AnalyticsQuery(BaseModel):
    """
    Модель сохранённого аналитического запроса
    """
    
    class QueryType(models.TextChoices):
        DEFECTS = 'defects', 'Дефекты'
        PROJECTS = 'projects', 'Проекты'
        USERS = 'users', 'Пользователи'
        PERFORMANCE = 'performance', 'Производительность'
        CUSTOM = 'custom', 'Пользовательский'
    
    name = models.CharField(
        verbose_name='Название запроса',
        max_length=200,
        help_text='Название аналитического запроса'
    )
    description = models.TextField(
        verbose_name='Описание',
        blank=True,
        help_text='Описание назначения запроса'
    )
    query_type = models.CharField(
        verbose_name='Тип запроса',
        max_length=20,
        choices=QueryType.choices,
        help_text='Тип аналитического запроса'
    )
    
    # SQL запрос или конфигурация
    sql_query = models.TextField(
        verbose_name='SQL запрос',
        blank=True,
        help_text='SQL запрос для получения данных'
    )
    query_config = models.JSONField(
        verbose_name='Конфигурация запроса',
        default=dict,
        blank=True,
        help_text='JSON конфигурация параметров запроса'
    )
    
    # Настройки
    is_public = models.BooleanField(
        verbose_name='Публичный',
        default=False,
        help_text='Доступен всем пользователям'
    )
    is_cached = models.BooleanField(
        verbose_name='Кэшируется',
        default=True,
        help_text='Кэшировать результаты запроса'
    )
    cache_duration = models.PositiveIntegerField(
        verbose_name='Время кэширования (минуты)',
        default=60,
        help_text='Время кэширования результатов в минутах'
    )
    
    # Автор
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='created_queries',
        verbose_name='Создал'
    )
    
    # Статистика использования
    usage_count = models.PositiveIntegerField(
        verbose_name='Количество использований',
        default=0,
        help_text='Сколько раз был выполнен запрос'
    )
    last_used_at = models.DateTimeField(
        verbose_name='Последнее использование',
        null=True,
        blank=True,
        help_text='Когда запрос был выполнен последний раз'
    )
    
    class Meta:
        verbose_name = 'Аналитический запрос'
        verbose_name_plural = 'Аналитические запросы'
        ordering = ['query_type', 'name']
        indexes = [
            models.Index(fields=['query_type']),
            models.Index(fields=['is_public']),
            models.Index(fields=['created_by']),
            models.Index(fields=['last_used_at']),
        ]
    
    def __str__(self):
        return f"{self.name} ({self.get_query_type_display()})"
    
    def mark_used(self):
        """Отметить использование запроса"""
        self.usage_count += 1
        self.last_used_at = timezone.now()
        self.save(update_fields=['usage_count', 'last_used_at'])
