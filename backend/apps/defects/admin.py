"""
Административный интерфейс для управления дефектами
"""

from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.db.models import Count
from django.utils import timezone
from .models import Defect, DefectCategory, DefectFile, DefectComment, DefectHistory


class DefectFileInline(admin.TabularInline):
    """
    Inline редактор файлов дефекта
    """
    model = DefectFile
    extra = 0
    fields = ['file', 'filename', 'file_type', 'description', 'is_main', 'uploaded_by']
    readonly_fields = ['file_type', 'uploaded_by']


class DefectCommentInline(admin.TabularInline):
    """
    Inline редактор комментариев дефекта
    """
    model = DefectComment
    extra = 0
    fields = ['author', 'content', 'comment_type', 'is_internal', 'created_at']
    readonly_fields = ['author', 'created_at']
    ordering = ['-created_at']


@admin.register(DefectCategory)
class DefectCategoryAdmin(admin.ModelAdmin):
    """
    Административный интерфейс для категорий дефектов
    """
    list_display = [
        'name', 'color_display', 'defects_count', 'is_active', 'order'
    ]
    search_fields = ['name', 'description']
    list_filter = ['is_active', 'created_at']
    ordering = ['order', 'name']
    readonly_fields = ['created_at', 'updated_at', 'defects_count']
    
    fieldsets = (
        ('Основная информация', {
            'fields': ('name', 'description', 'order')
        }),
        ('Оформление', {
            'fields': ('color', 'icon')
        }),
        ('Настройки', {
            'fields': ('is_active',)
        }),
        ('Статистика', {
            'fields': ('defects_count',),
            'classes': ['collapse']
        }),
        ('Метаданные', {
            'fields': ('created_at', 'updated_at'),
            'classes': ['collapse']
        }),
    )
    
    def get_queryset(self, request):
        """Оптимизируем запросы"""
        return super().get_queryset(request).annotate(
            defects_count=Count('defects')
        )
    
    def color_display(self, obj):
        """Отображение цвета категории"""
        return format_html(
            '<div style="width: 20px; height: 20px; background-color: {}; border: 1px solid #ccc; border-radius: 3px;"></div>',
            obj.color
        )
    color_display.short_description = 'Цвет'
    
    def defects_count(self, obj):
        """Количество дефектов в категории"""
        count = obj.defects_count
        if count > 0:
            url = reverse('admin:defects_defect_changelist')
            return format_html(
                '<a href="{}?category__id__exact={}">{} дефектов</a>',
                url, obj.id, count
            )
        return '0 дефектов'
    defects_count.short_description = 'Дефекты'


@admin.register(Defect)
class DefectAdmin(admin.ModelAdmin):
    """
    Административный интерфейс для дефектов
    """
    inlines = [DefectFileInline, DefectCommentInline]
    
    # Поля для отображения в списке
    list_display = [
        'defect_number', 'title', 'project', 'category_display',
        'status_display', 'priority_display', 'severity_display',
        'author', 'assignee', 'due_date_display', 'created_at'
    ]
    
    # Поля для поиска
    search_fields = [
        'defect_number', 'title', 'description', 'location',
        'project__name', 'author__first_name', 'author__last_name',
        'assignee__first_name', 'assignee__last_name'
    ]
    
    # Фильтры
    list_filter = [
        'status', 'priority', 'severity', 'category',
        'project', 'created_at', 'due_date'
    ]
    
    # Поля только для чтения
    readonly_fields = [
        'defect_number', 'assigned_at', 'started_at', 'completed_at',
        'closed_at', 'created_at', 'updated_at', 'is_overdue',
        'days_remaining', 'resolution_time'
    ]
    
    # Сортировка по умолчанию
    ordering = ['-created_at']
    
    # Поля для автодополнения
    autocomplete_fields = ['project', 'stage', 'category', 'author', 'assignee', 'reviewer']
    
    # Поля для редактирования
    fieldsets = (
        ('Основная информация', {
            'fields': (
                'defect_number', 'title', 'description',
                'project', 'stage', 'category'
            )
        }),
        ('Приоритет и классификация', {
            'fields': ('priority', 'severity', 'status')
        }),
        ('Местоположение', {
            'fields': (
                'location', 'floor', 'room',
                ('coordinates_x', 'coordinates_y')
            )
        }),
        ('Ответственные лица', {
            'fields': ('author', 'assignee', 'reviewer')
        }),
        ('Временные рамки', {
            'fields': (
                'due_date', 'assigned_at', 'started_at',
                'completed_at', 'closed_at'
            )
        }),
        ('Стоимость', {
            'fields': ('estimated_cost', 'actual_cost'),
            'classes': ['collapse']
        }),
        ('Решение', {
            'fields': ('resolution_description', 'prevention_measures'),
            'classes': ['collapse']
        }),
        ('Дополнительно', {
            'fields': ('external_id',),
            'classes': ['collapse']
        }),
        ('Вычисляемые поля', {
            'fields': ('is_overdue', 'days_remaining', 'resolution_time'),
            'classes': ['collapse']
        }),
        ('Метаданные', {
            'fields': ('created_at', 'updated_at'),
            'classes': ['collapse']
        }),
    )
    
    # Действия
    actions = [
        'mark_as_in_progress', 'mark_as_closed', 'mark_as_cancelled',
        'set_high_priority', 'set_critical_priority'
    ]
    
    def get_queryset(self, request):
        """Оптимизируем запросы"""
        return super().get_queryset(request).select_related(
            'project', 'category', 'author', 'assignee', 'reviewer', 'stage'
        ).prefetch_related('files', 'comments')
    
    def category_display(self, obj):
        """Отображение категории с цветом"""
        return format_html(
            '<span style="display: inline-block; width: 10px; height: 10px; background-color: {}; border-radius: 50%; margin-right: 5px;"></span>{}',
            obj.category.color, obj.category.name
        )
    category_display.short_description = 'Категория'
    
    def status_display(self, obj):
        """Отображение статуса с цветом"""
        colors = {
            'new': 'orange',
            'in_progress': 'blue',
            'review': 'purple',
            'closed': 'green',
            'cancelled': 'red',
        }
        color = colors.get(obj.status, 'gray')
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            color, obj.get_status_display()
        )
    status_display.short_description = 'Статус'
    
    def priority_display(self, obj):
        """Отображение приоритета с цветом"""
        colors = {
            'low': 'gray',
            'medium': 'orange',
            'high': 'red',
            'critical': 'darkred',
        }
        color = colors.get(obj.priority, 'black')
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            color, obj.get_priority_display()
        )
    priority_display.short_description = 'Приоритет'
    
    def severity_display(self, obj):
        """Отображение серьёзности"""
        colors = {
            'cosmetic': 'lightgray',
            'minor': 'orange',
            'major': 'red',
            'critical': 'darkred',
            'blocking': 'purple',
        }
        color = colors.get(obj.severity, 'black')
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            color, obj.get_severity_display()
        )
    severity_display.short_description = 'Серьёзность'
    
    def due_date_display(self, obj):
        """Отображение срока выполнения с индикацией просрочки"""
        if not obj.due_date:
            return '-'
        
        if obj.is_overdue:
            return format_html(
                '<span style="color: red; font-weight: bold;">⚠️ {}</span>',
                obj.due_date.strftime('%d.%m.%Y')
            )
        
        days_remaining = obj.days_remaining
        if days_remaining is not None and days_remaining <= 3:
            return format_html(
                '<span style="color: orange; font-weight: bold;">⏰ {}</span>',
                obj.due_date.strftime('%d.%m.%Y')
            )
        
        return obj.due_date.strftime('%d.%m.%Y')
    due_date_display.short_description = 'Срок выполнения'
    
    # Массовые действия
    def mark_as_in_progress(self, request, queryset):
        """Отметить как в работе"""
        count = 0
        for defect in queryset:
            try:
                if defect.status == 'new':
                    defect.status = 'in_progress'
                    defect.started_at = timezone.now()
                    defect.save()
                    count += 1
            except Exception:
                pass
        
        self.message_user(request, f'Отмечено как в работе {count} дефектов.')
    mark_as_in_progress.short_description = 'Отметить как в работе'
    
    def mark_as_closed(self, request, queryset):
        """Отметить как закрытые"""
        count = 0
        for defect in queryset:
            try:
                if defect.status in ['review']:
                    defect.status = 'closed'
                    defect.closed_at = timezone.now()
                    defect.save()
                    count += 1
            except Exception:
                pass
        
        self.message_user(request, f'Закрыто {count} дефектов.')
    mark_as_closed.short_description = 'Закрыть дефекты'
    
    def mark_as_cancelled(self, request, queryset):
        """Отметить как отменённые"""
        count = queryset.update(status='cancelled')
        self.message_user(request, f'Отменено {count} дефектов.')
    mark_as_cancelled.short_description = 'Отменить дефекты'
    
    def set_high_priority(self, request, queryset):
        """Установить высокий приоритет"""
        count = queryset.update(priority='high')
        self.message_user(request, f'Установлен высокий приоритет для {count} дефектов.')
    set_high_priority.short_description = 'Установить высокий приоритет'
    
    def set_critical_priority(self, request, queryset):
        """Установить критический приоритет"""
        count = queryset.update(priority='critical')
        self.message_user(request, f'Установлен критический приоритет для {count} дефектов.')
    set_critical_priority.short_description = 'Установить критический приоритет'


@admin.register(DefectFile)
class DefectFileAdmin(admin.ModelAdmin):
    """
    Административный интерфейс для файлов дефектов
    """
    list_display = [
        'defect', 'filename', 'file_type', 'file_size_display',
        'is_main', 'uploaded_by', 'created_at'
    ]
    search_fields = ['defect__defect_number', 'filename', 'description']
    list_filter = ['file_type', 'is_main', 'created_at']
    readonly_fields = ['file_size', 'mime_type', 'created_at', 'updated_at']
    autocomplete_fields = ['defect', 'uploaded_by']
    ordering = ['-created_at']
    
    fieldsets = (
        ('Основная информация', {
            'fields': ('defect', 'file', 'filename', 'description')
        }),
        ('Технические данные', {
            'fields': ('file_type', 'file_size', 'mime_type', 'is_main')
        }),
        ('Метаданные', {
            'fields': ('uploaded_by', 'created_at', 'updated_at'),
            'classes': ['collapse']
        }),
    )
    
    def file_size_display(self, obj):
        """Отображение размера файла"""
        from apps.common.utils import format_file_size
        return format_file_size(obj.file_size)
    file_size_display.short_description = 'Размер файла'


@admin.register(DefectComment)
class DefectCommentAdmin(admin.ModelAdmin):
    """
    Административный интерфейс для комментариев дефектов
    """
    list_display = [
        'defect', 'author', 'comment_type_display', 'is_internal',
        'content_preview', 'created_at'
    ]
    search_fields = ['defect__defect_number', 'content', 'author__first_name', 'author__last_name']
    list_filter = ['comment_type', 'is_internal', 'created_at']
    readonly_fields = ['created_at', 'updated_at']
    autocomplete_fields = ['defect', 'author', 'reply_to']
    ordering = ['-created_at']
    
    fieldsets = (
        ('Основная информация', {
            'fields': ('defect', 'author', 'content')
        }),
        ('Настройки', {
            'fields': ('comment_type', 'is_internal', 'reply_to')
        }),
        ('Метаданные', {
            'fields': ('created_at', 'updated_at'),
            'classes': ['collapse']
        }),
    )
    
    def comment_type_display(self, obj):
        """Отображение типа комментария"""
        colors = {
            'comment': 'blue',
            'status_change': 'orange',
            'assignment': 'green',
            'resolution': 'purple',
            'rejection': 'red',
        }
        color = colors.get(obj.comment_type, 'black')
        return format_html(
            '<span style="color: {};">{}</span>',
            color, obj.get_comment_type_display()
        )
    comment_type_display.short_description = 'Тип'
    
    def content_preview(self, obj):
        """Превью содержимого комментария"""
        if len(obj.content) > 50:
            return obj.content[:47] + '...'
        return obj.content
    content_preview.short_description = 'Содержимое'


@admin.register(DefectHistory)
class DefectHistoryAdmin(admin.ModelAdmin):
    """
    Административный интерфейс для истории изменений дефектов
    """
    list_display = [
        'defect', 'user', 'action', 'field_name',
        'old_value_preview', 'new_value_preview', 'timestamp'
    ]
    search_fields = ['defect__defect_number', 'action', 'field_name']
    list_filter = ['action', 'timestamp']
    readonly_fields = ['timestamp']
    autocomplete_fields = ['defect', 'user']
    ordering = ['-timestamp']
    
    fieldsets = (
        ('Основная информация', {
            'fields': ('defect', 'user', 'action', 'field_name')
        }),
        ('Изменения', {
            'fields': ('old_value', 'new_value')
        }),
        ('Метаданные', {
            'fields': ('timestamp', 'ip_address')
        }),
    )
    
    def old_value_preview(self, obj):
        """Превью старого значения"""
        if obj.old_value and len(obj.old_value) > 30:
            return obj.old_value[:27] + '...'
        return obj.old_value or '-'
    old_value_preview.short_description = 'Старое значение'
    
    def new_value_preview(self, obj):
        """Превью нового значения"""
        if obj.new_value and len(obj.new_value) > 30:
            return obj.new_value[:27] + '...'
        return obj.new_value or '-'
    new_value_preview.short_description = 'Новое значение'
    
    def has_add_permission(self, request):
        """Запрещаем создание записей истории через админку"""
        return False
    
    def has_change_permission(self, request, obj=None):
        """Запрещаем изменение записей истории"""
        return False
    
    def has_delete_permission(self, request, obj=None):
        """Запрещаем удаление записей истории"""
        return False
