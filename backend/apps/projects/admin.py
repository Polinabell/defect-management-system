"""
Административный интерфейс для управления проектами
"""

from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.db.models import Count
from .models import Project, ProjectMember, ProjectStage, ProjectTemplate, ProjectStageTemplate


class ProjectMemberInline(admin.TabularInline):
    """
    Inline редактор участников проекта
    """
    model = ProjectMember
    extra = 0
    fields = ['user', 'role', 'is_active', 'joined_at']
    readonly_fields = ['joined_at']
    autocomplete_fields = ['user']


class ProjectStageInline(admin.TabularInline):
    """
    Inline редактор этапов проекта
    """
    model = ProjectStage
    extra = 0
    fields = ['name', 'order', 'start_date', 'end_date', 'responsible', 'status', 'completion_percentage']
    readonly_fields = []
    autocomplete_fields = ['responsible']
    ordering = ['order', 'start_date']


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    """
    Административный интерфейс для проектов
    """
    inlines = [ProjectMemberInline, ProjectStageInline]
    
    # Поля для отображения в списке
    list_display = [
        'name', 'manager', 'customer', 'status_display', 'priority_display',
        'start_date', 'end_date', 'progress_display', 'is_overdue_display',
        'members_count', 'defects_count'
    ]
    
    # Поля для поиска
    search_fields = ['name', 'description', 'customer', 'address', 'contract_number']
    
    # Фильтры
    list_filter = [
        'status', 'priority', 'building_type', 'manager',
        'start_date', 'end_date', 'created_at'
    ]
    
    # Поля только для чтения
    readonly_fields = [
        'slug', 'created_at', 'updated_at', 'progress_percentage',
        'duration_planned', 'duration_actual', 'is_overdue', 'days_remaining'
    ]
    
    # Сортировка по умолчанию
    ordering = ['-created_at']
    
    # Поля для автодополнения
    autocomplete_fields = ['manager']
    
    # Поля для редактирования
    fieldsets = (
        ('Основная информация', {
            'fields': ('name', 'slug', 'description', 'status', 'priority')
        }),
        ('Местоположение', {
            'fields': ('address', 'coordinates_lat', 'coordinates_lng')
        }),
        ('Заказчик и договор', {
            'fields': (
                'customer', 'customer_contact', 'customer_phone', 'customer_email',
                'contract_number', 'contract_date', 'contract_amount'
            ),
            'classes': ['collapse']
        }),
        ('Управление проектом', {
            'fields': ('manager',)
        }),
        ('Временные рамки', {
            'fields': (
                ('start_date', 'end_date'),
                ('actual_start_date', 'actual_end_date'),
                ('duration_planned', 'duration_actual'),
                ('is_overdue', 'days_remaining')
            )
        }),
        ('Характеристики объекта', {
            'fields': ('total_area', 'building_type', 'floors_count'),
            'classes': ['collapse']
        }),
        ('Настройки уведомлений', {
            'fields': ('notify_on_defect_creation', 'notify_on_status_change'),
            'classes': ['collapse']
        }),
        ('Статистика', {
            'fields': ('progress_percentage',),
            'classes': ['collapse']
        }),
        ('Метаданные', {
            'fields': ('created_at', 'updated_at'),
            'classes': ['collapse']
        }),
    )
    
    # Действия
    actions = ['mark_as_completed', 'mark_as_in_progress', 'mark_as_on_hold']
    
    def get_queryset(self, request):
        """Оптимизируем запросы"""
        return super().get_queryset(request).select_related(
            'manager'
        ).prefetch_related(
            'members', 'defects'
        ).annotate(
            members_count=Count('members', distinct=True),
            defects_count=Count('defects', distinct=True)
        )
    
    def status_display(self, obj):
        """Отображение статуса с цветом"""
        colors = {
            'planning': 'orange',
            'in_progress': 'blue',
            'on_hold': 'red',
            'completed': 'green',
            'cancelled': 'gray',
        }
        color = colors.get(obj.status, 'black')
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
    
    def progress_display(self, obj):
        """Отображение прогресса с полосой"""
        progress = obj.progress_percentage
        color = 'green' if progress >= 80 else 'orange' if progress >= 50 else 'red'
        return format_html(
            '<div style="width: 100px; background-color: #f0f0f0; border-radius: 3px;">'
            '<div style="width: {}%; background-color: {}; height: 20px; border-radius: 3px; text-align: center; color: white; font-size: 12px; line-height: 20px;">'
            '{}%</div></div>',
            progress, color, progress
        )
    progress_display.short_description = 'Прогресс'
    
    def is_overdue_display(self, obj):
        """Отображение просрочки"""
        if obj.is_overdue:
            return format_html(
                '<span style="color: red; font-weight: bold;">⚠️ Просрочен</span>'
            )
        return format_html(
            '<span style="color: green;">✓ В срок</span>'
        )
    is_overdue_display.short_description = 'Сроки'
    
    def members_count(self, obj):
        """Количество участников"""
        count = obj.members_count
        url = reverse('admin:projects_projectmember_changelist')
        return format_html(
            '<a href="{}?project__id__exact={}">{} участн.</a>',
            url, obj.id, count
        )
    members_count.short_description = 'Участники'
    
    def defects_count(self, obj):
        """Количество дефектов"""
        count = obj.defects_count
        if count > 0:
            # URL будет создан когда добавим модуль дефектов
            return format_html('<strong>{} дефектов</strong>', count)
        return '0 дефектов'
    defects_count.short_description = 'Дефекты'
    
    # Массовые действия
    def mark_as_completed(self, request, queryset):
        """Отметить как завершённые"""
        count = queryset.update(status=Project.Status.COMPLETED)
        self.message_user(request, f'Отмечено как завершённые {count} проектов.')
    mark_as_completed.short_description = 'Отметить как завершённые'
    
    def mark_as_in_progress(self, request, queryset):
        """Отметить как в работе"""
        count = queryset.update(status=Project.Status.IN_PROGRESS)
        self.message_user(request, f'Отмечено как в работе {count} проектов.')
    mark_as_in_progress.short_description = 'Отметить как в работе'
    
    def mark_as_on_hold(self, request, queryset):
        """Отметить как приостановленные"""
        count = queryset.update(status=Project.Status.ON_HOLD)
        self.message_user(request, f'Отмечено как приостановленные {count} проектов.')
    mark_as_on_hold.short_description = 'Отметить как приостановленные'


@admin.register(ProjectMember)
class ProjectMemberAdmin(admin.ModelAdmin):
    """
    Административный интерфейс для участников проектов
    """
    list_display = ['project', 'user', 'get_user_role', 'role', 'joined_at', 'is_active']
    search_fields = ['project__name', 'user__first_name', 'user__last_name', 'user__email']
    list_filter = ['role', 'is_active', 'joined_at', 'project__status']
    autocomplete_fields = ['project', 'user']
    readonly_fields = ['joined_at']
    ordering = ['-joined_at']
    
    def get_user_role(self, obj):
        """Роль пользователя в системе"""
        return obj.user.get_role_display()
    get_user_role.short_description = 'Роль в системе'


@admin.register(ProjectStage)
class ProjectStageAdmin(admin.ModelAdmin):
    """
    Административный интерфейс для этапов проектов
    """
    list_display = [
        'project', 'name', 'order', 'responsible', 'status_display',
        'start_date', 'end_date', 'completion_display', 'is_overdue_display'
    ]
    search_fields = ['project__name', 'name', 'description']
    list_filter = ['status', 'project', 'responsible', 'start_date']
    autocomplete_fields = ['project', 'responsible']
    readonly_fields = [
        'created_at', 'updated_at', 'duration_planned', 'duration_actual',
        'is_overdue', 'days_remaining'
    ]
    ordering = ['project', 'order', 'start_date']
    
    fieldsets = (
        ('Основная информация', {
            'fields': ('project', 'name', 'description', 'order')
        }),
        ('Временные рамки', {
            'fields': (
                ('start_date', 'end_date'),
                ('actual_start_date', 'actual_end_date'),
                ('duration_planned', 'duration_actual'),
                ('is_overdue', 'days_remaining')
            )
        }),
        ('Ответственность и выполнение', {
            'fields': ('responsible', 'status', 'completion_percentage')
        }),
        ('Трудозатраты', {
            'fields': ('estimated_hours', 'actual_hours'),
            'classes': ['collapse']
        }),
        ('Метаданные', {
            'fields': ('created_at', 'updated_at'),
            'classes': ['collapse']
        }),
    )
    
    def status_display(self, obj):
        """Отображение статуса этапа"""
        colors = {
            'not_started': 'gray',
            'in_progress': 'blue',
            'completed': 'green',
            'on_hold': 'orange',
            'cancelled': 'red',
        }
        color = colors.get(obj.status, 'black')
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            color, obj.get_status_display()
        )
    status_display.short_description = 'Статус'
    
    def completion_display(self, obj):
        """Отображение процента выполнения"""
        progress = obj.completion_percentage
        color = 'green' if progress >= 80 else 'orange' if progress >= 50 else 'red'
        return format_html(
            '<div style="width: 80px; background-color: #f0f0f0; border-radius: 3px;">'
            '<div style="width: {}%; background-color: {}; height: 18px; border-radius: 3px; text-align: center; color: white; font-size: 11px; line-height: 18px;">'
            '{}%</div></div>',
            progress, color, progress
        )
    completion_display.short_description = 'Выполнение'
    
    def is_overdue_display(self, obj):
        """Отображение просрочки этапа"""
        if obj.is_overdue:
            return format_html(
                '<span style="color: red; font-weight: bold;">⚠️</span>'
            )
        return format_html(
            '<span style="color: green;">✓</span>'
        )
    is_overdue_display.short_description = 'Срок'


class ProjectStageTemplateInline(admin.TabularInline):
    """
    Inline редактор шаблонов этапов
    """
    model = ProjectStageTemplate
    extra = 1
    fields = ['name', 'order', 'estimated_days', 'estimated_hours', 'description']
    ordering = ['order']


@admin.register(ProjectTemplate)
class ProjectTemplateAdmin(admin.ModelAdmin):
    """
    Административный интерфейс для шаблонов проектов
    """
    inlines = [ProjectStageTemplateInline]
    
    list_display = ['name', 'building_type_display', 'stages_count', 'is_active', 'created_by', 'created_at']
    search_fields = ['name', 'description']
    list_filter = ['building_type', 'is_active', 'created_at']
    readonly_fields = ['created_at', 'updated_at', 'stages_count']
    autocomplete_fields = ['created_by']
    
    fieldsets = (
        ('Основная информация', {
            'fields': ('name', 'description', 'building_type')
        }),
        ('Настройки', {
            'fields': ('is_active', 'created_by')
        }),
        ('Статистика', {
            'fields': ('stages_count',),
            'classes': ['collapse']
        }),
        ('Метаданные', {
            'fields': ('created_at', 'updated_at'),
            'classes': ['collapse']
        }),
    )
    
    def building_type_display(self, obj):
        """Отображение типа здания"""
        return obj.get_building_type_display()
    building_type_display.short_description = 'Тип здания'
    
    def stages_count(self, obj):
        """Количество этапов в шаблоне"""
        return obj.stage_templates.count()
    stages_count.short_description = 'Количество этапов'


@admin.register(ProjectStageTemplate)
class ProjectStageTemplateAdmin(admin.ModelAdmin):
    """
    Административный интерфейс для шаблонов этапов
    """
    list_display = ['template', 'name', 'order', 'estimated_days', 'estimated_hours']
    search_fields = ['template__name', 'name', 'description']
    list_filter = ['template', 'estimated_days']
    autocomplete_fields = ['template']
    ordering = ['template', 'order']
    
    fieldsets = (
        ('Основная информация', {
            'fields': ('template', 'name', 'description', 'order')
        }),
        ('Планирование', {
            'fields': ('estimated_days', 'estimated_hours')
        }),
    )
