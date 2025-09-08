"""
Административный интерфейс для отчётов и аналитики
"""

from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.db.models import Count
from .models import ReportTemplate, GeneratedReport, Dashboard, AnalyticsQuery


@admin.register(ReportTemplate)
class ReportTemplateAdmin(admin.ModelAdmin):
    """
    Административный интерфейс для шаблонов отчётов
    """
    list_display = [
        'name', 'report_type_display', 'output_format_display',
        'is_public', 'is_active', 'reports_count', 'created_by', 'created_at'
    ]
    search_fields = ['name', 'description']
    list_filter = ['report_type', 'output_format', 'is_public', 'is_active', 'created_at']
    readonly_fields = ['created_at', 'updated_at', 'reports_count']
    autocomplete_fields = ['created_by']
    ordering = ['report_type', 'name']
    
    fieldsets = (
        ('Основная информация', {
            'fields': ('name', 'description', 'report_type', 'output_format')
        }),
        ('Конфигурация', {
            'fields': ('filter_config', 'display_config'),
            'classes': ['collapse']
        }),
        ('Настройки доступа', {
            'fields': ('is_public', 'is_active', 'created_by')
        }),
        ('Статистика', {
            'fields': ('reports_count',),
            'classes': ['collapse']
        }),
        ('Метаданные', {
            'fields': ('created_at', 'updated_at'),
            'classes': ['collapse']
        }),
    )
    
    actions = ['make_public', 'make_private', 'activate', 'deactivate']
    
    def get_queryset(self, request):
        """Оптимизируем запросы"""
        return super().get_queryset(request).select_related(
            'created_by'
        ).annotate(
            reports_count=Count('generated_reports')
        )
    
    def report_type_display(self, obj):
        """Отображение типа отчёта"""
        colors = {
            'project_summary': 'blue',
            'defects_analysis': 'red',
            'performance_report': 'green',
            'timeline_report': 'orange',
            'custom': 'purple',
        }
        color = colors.get(obj.report_type, 'black')
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            color, obj.get_report_type_display()
        )
    report_type_display.short_description = 'Тип отчёта'
    
    def output_format_display(self, obj):
        """Отображение формата вывода"""
        icons = {
            'pdf': '📄',
            'excel': '📊',
            'csv': '📝',
            'json': '🔧',
        }
        icon = icons.get(obj.output_format, '📄')
        return format_html(
            '{} {}',
            icon, obj.get_output_format_display()
        )
    output_format_display.short_description = 'Формат'
    
    def reports_count(self, obj):
        """Количество сгенерированных отчётов"""
        count = obj.reports_count
        if count > 0:
            url = reverse('admin:reports_generatedreport_changelist')
            return format_html(
                '<a href="{}?template__id__exact={}">{} отчётов</a>',
                url, obj.id, count
            )
        return '0 отчётов'
    reports_count.short_description = 'Отчёты'
    
    # Массовые действия
    def make_public(self, request, queryset):
        """Сделать публичными"""
        count = queryset.update(is_public=True)
        self.message_user(request, f'Сделано публичными {count} шаблонов.')
    make_public.short_description = 'Сделать публичными'
    
    def make_private(self, request, queryset):
        """Сделать приватными"""
        count = queryset.update(is_public=False)
        self.message_user(request, f'Сделано приватными {count} шаблонов.')
    make_private.short_description = 'Сделать приватными'
    
    def activate(self, request, queryset):
        """Активировать"""
        count = queryset.update(is_active=True)
        self.message_user(request, f'Активировано {count} шаблонов.')
    activate.short_description = 'Активировать'
    
    def deactivate(self, request, queryset):
        """Деактивировать"""
        count = queryset.update(is_active=False)
        self.message_user(request, f'Деактивировано {count} шаблонов.')
    deactivate.short_description = 'Деактивировать'


@admin.register(GeneratedReport)
class GeneratedReportAdmin(admin.ModelAdmin):
    """
    Административный интерфейс для сгенерированных отчётов
    """
    list_display = [
        'name', 'template', 'project', 'status_display',
        'generated_by', 'file_size_display', 'download_count',
        'is_expired_display', 'created_at'
    ]
    search_fields = ['name', 'description', 'template__name']
    list_filter = ['status', 'template', 'project', 'generated_at', 'expires_at']
    readonly_fields = [
        'status', 'file', 'file_size', 'generated_at', 'processing_time',
        'error_message', 'download_count', 'created_at', 'updated_at',
        'is_expired', 'formatted_file_size'
    ]
    autocomplete_fields = ['template', 'project', 'generated_by']
    ordering = ['-created_at']
    
    fieldsets = (
        ('Основная информация', {
            'fields': ('name', 'description', 'template', 'project')
        }),
        ('Параметры генерации', {
            'fields': ('date_from', 'date_to', 'filter_params'),
            'classes': ['collapse']
        }),
        ('Результат', {
            'fields': (
                'status', 'file', 'file_size', 'formatted_file_size',
                'error_message'
            )
        }),
        ('Статистика', {
            'fields': (
                'generated_by', 'generated_at', 'processing_time',
                'expires_at', 'is_expired', 'download_count'
            )
        }),
        ('Метаданные', {
            'fields': ('created_at', 'updated_at'),
            'classes': ['collapse']
        }),
    )
    
    actions = ['delete_expired', 'extend_expiration']
    
    def get_queryset(self, request):
        """Оптимизируем запросы"""
        return super().get_queryset(request).select_related(
            'template', 'project', 'generated_by'
        )
    
    def status_display(self, obj):
        """Отображение статуса с цветом"""
        colors = {
            'pending': 'orange',
            'processing': 'blue',
            'completed': 'green',
            'failed': 'red',
            'expired': 'gray',
        }
        color = colors.get(obj.status, 'black')
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            color, obj.get_status_display()
        )
    status_display.short_description = 'Статус'
    
    def file_size_display(self, obj):
        """Отображение размера файла"""
        if obj.file_size:
            from apps.common.utils import format_file_size
            return format_file_size(obj.file_size)
        return '-'
    file_size_display.short_description = 'Размер файла'
    
    def is_expired_display(self, obj):
        """Отображение истечения срока"""
        if obj.is_expired:
            return format_html(
                '<span style="color: red; font-weight: bold;">⚠️ Истёк</span>'
            )
        elif obj.expires_at:
            return format_html(
                '<span style="color: green;">✓ Действует</span>'
            )
        return '-'
    is_expired_display.short_description = 'Срок действия'
    
    # Массовые действия
    def delete_expired(self, request, queryset):
        """Удалить истёкшие отчёты"""
        expired_reports = queryset.filter(expires_at__lt=timezone.now())
        count = expired_reports.count()
        expired_reports.delete()
        self.message_user(request, f'Удалено {count} истёкших отчётов.')
    delete_expired.short_description = 'Удалить истёкшие отчёты'
    
    def extend_expiration(self, request, queryset):
        """Продлить срок действия на 30 дней"""
        from django.utils import timezone
        from datetime import timedelta
        
        new_expiration = timezone.now() + timedelta(days=30)
        count = queryset.update(expires_at=new_expiration)
        self.message_user(request, f'Продлён срок действия для {count} отчётов.')
    extend_expiration.short_description = 'Продлить срок действия'


@admin.register(Dashboard)
class DashboardAdmin(admin.ModelAdmin):
    """
    Административный интерфейс для дашбордов
    """
    list_display = [
        'name', 'dashboard_type_display', 'is_default',
        'is_public', 'widgets_count', 'created_by', 'created_at'
    ]
    search_fields = ['name', 'description']
    list_filter = ['dashboard_type', 'is_default', 'is_public', 'created_at']
    readonly_fields = ['created_at', 'updated_at', 'widgets_count']
    autocomplete_fields = ['created_by']
    ordering = ['dashboard_type', 'name']
    
    fieldsets = (
        ('Основная информация', {
            'fields': ('name', 'description', 'dashboard_type')
        }),
        ('Конфигурация виджетов', {
            'fields': ('widgets_config',),
            'classes': ['collapse']
        }),
        ('Настройки доступа', {
            'fields': ('is_default', 'is_public', 'allowed_roles', 'created_by')
        }),
        ('Статистика', {
            'fields': ('widgets_count',),
            'classes': ['collapse']
        }),
        ('Метаданные', {
            'fields': ('created_at', 'updated_at'),
            'classes': ['collapse']
        }),
    )
    
    actions = ['make_default', 'make_public', 'make_private']
    
    def dashboard_type_display(self, obj):
        """Отображение типа дашборда"""
        icons = {
            'executive': '👔',
            'project_manager': '📋',
            'engineer': '🔧',
            'custom': '⚙️',
        }
        icon = icons.get(obj.dashboard_type, '📊')
        return format_html(
            '{} {}',
            icon, obj.get_dashboard_type_display()
        )
    dashboard_type_display.short_description = 'Тип дашборда'
    
    def widgets_count(self, obj):
        """Количество виджетов"""
        if isinstance(obj.widgets_config, list):
            return len(obj.widgets_config)
        return 0
    widgets_count.short_description = 'Виджетов'
    
    # Массовые действия
    def make_default(self, request, queryset):
        """Сделать дашбордом по умолчанию"""
        for dashboard in queryset:
            # Сначала убираем флаг default у других дашбордов того же типа
            Dashboard.objects.filter(
                dashboard_type=dashboard.dashboard_type
            ).update(is_default=False)
            
            # Устанавливаем флаг для выбранного дашборда
            dashboard.is_default = True
            dashboard.save()
        
        count = queryset.count()
        self.message_user(request, f'Установлено как дашборд по умолчанию для {count} типов.')
    make_default.short_description = 'Сделать дашбордом по умолчанию'
    
    def make_public(self, request, queryset):
        """Сделать публичными"""
        count = queryset.update(is_public=True)
        self.message_user(request, f'Сделано публичными {count} дашбордов.')
    make_public.short_description = 'Сделать публичными'
    
    def make_private(self, request, queryset):
        """Сделать приватными"""
        count = queryset.update(is_public=False)
        self.message_user(request, f'Сделано приватными {count} дашбордов.')
    make_private.short_description = 'Сделать приватными'


@admin.register(AnalyticsQuery)
class AnalyticsQueryAdmin(admin.ModelAdmin):
    """
    Административный интерфейс для аналитических запросов
    """
    list_display = [
        'name', 'query_type_display', 'is_public', 'is_cached',
        'usage_count', 'last_used_at', 'created_by', 'created_at'
    ]
    search_fields = ['name', 'description']
    list_filter = ['query_type', 'is_public', 'is_cached', 'created_at', 'last_used_at']
    readonly_fields = ['usage_count', 'last_used_at', 'created_at', 'updated_at']
    autocomplete_fields = ['created_by']
    ordering = ['query_type', 'name']
    
    fieldsets = (
        ('Основная информация', {
            'fields': ('name', 'description', 'query_type')
        }),
        ('SQL запрос', {
            'fields': ('sql_query',),
            'classes': ['collapse']
        }),
        ('Конфигурация', {
            'fields': ('query_config',),
            'classes': ['collapse']
        }),
        ('Настройки', {
            'fields': ('is_public', 'is_cached', 'cache_duration', 'created_by')
        }),
        ('Статистика использования', {
            'fields': ('usage_count', 'last_used_at')
        }),
        ('Метаданные', {
            'fields': ('created_at', 'updated_at'),
            'classes': ['collapse']
        }),
    )
    
    actions = ['make_public', 'make_private', 'enable_cache', 'disable_cache']
    
    def query_type_display(self, obj):
        """Отображение типа запроса"""
        colors = {
            'defects': 'red',
            'projects': 'blue',
            'users': 'green',
            'performance': 'orange',
            'custom': 'purple',
        }
        color = colors.get(obj.query_type, 'black')
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            color, obj.get_query_type_display()
        )
    query_type_display.short_description = 'Тип запроса'
    
    # Массовые действия
    def make_public(self, request, queryset):
        """Сделать публичными"""
        count = queryset.update(is_public=True)
        self.message_user(request, f'Сделано публичными {count} запросов.')
    make_public.short_description = 'Сделать публичными'
    
    def make_private(self, request, queryset):
        """Сделать приватными"""
        count = queryset.update(is_public=False)
        self.message_user(request, f'Сделано приватными {count} запросов.')
    make_private.short_description = 'Сделать приватными'
    
    def enable_cache(self, request, queryset):
        """Включить кэширование"""
        count = queryset.update(is_cached=True)
        self.message_user(request, f'Включено кэширование для {count} запросов.')
    enable_cache.short_description = 'Включить кэширование'
    
    def disable_cache(self, request, queryset):
        """Отключить кэширование"""
        count = queryset.update(is_cached=False)
        self.message_user(request, f'Отключено кэширование для {count} запросов.')
    disable_cache.short_description = 'Отключить кэширование'
