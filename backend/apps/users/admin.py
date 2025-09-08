"""
Административный интерфейс для пользователей
"""

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.html import format_html
from django.urls import reverse
from django.utils.safestring import mark_safe
from .models import User, UserProfile, UserSession


class UserProfileInline(admin.StackedInline):
    """
    Inline редактор профиля пользователя
    """
    model = UserProfile
    can_delete = False
    verbose_name = 'Профиль'
    verbose_name_plural = 'Профиль'
    extra = 0
    fields = [
        ('avatar', 'bio'),
        ('birth_date', 'department'),
        ('hire_date', 'supervisor'),
        ('email_notifications', 'sms_notifications'),
        ('theme', 'language'),
    ]


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """
    Административный интерфейс для пользователей
    """
    inlines = [UserProfileInline]
    
    # Поля для отображения в списке
    list_display = [
        'email', 'get_full_name', 'role', 'position',
        'is_active', 'is_locked_display', 'last_login', 'date_joined'
    ]
    
    # Поля для поиска
    search_fields = ['email', 'first_name', 'last_name', 'position']
    
    # Фильтры
    list_filter = [
        'role', 'is_active', 'is_staff', 'is_superuser',
        'must_change_password', 'date_joined', 'last_login'
    ]
    
    # Сортировка по умолчанию
    ordering = ['last_name', 'first_name']
    
    # Поля только для чтения
    readonly_fields = [
        'date_joined', 'last_login', 'created_at', 'updated_at',
        'password_changed_at', 'last_login_ip', 'failed_login_attempts',
        'get_full_name', 'get_sessions_count'
    ]
    
    # Поля для редактирования
    fieldsets = (
        ('Основная информация', {
            'fields': ('email', 'username', 'password')
        }),
        ('Личная информация', {
            'fields': ('first_name', 'last_name', 'middle_name', 'phone', 'position')
        }),
        ('Роль и права', {
            'fields': ('role', 'is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')
        }),
        ('Безопасность', {
            'fields': (
                'is_email_verified', 'must_change_password', 'password_changed_at',
                'last_login_ip', 'failed_login_attempts', 'locked_until'
            ),
            'classes': ['collapse']
        }),
        ('Метаданные', {
            'fields': ('date_joined', 'last_login', 'created_at', 'updated_at'),
            'classes': ['collapse']
        }),
        ('Дополнительно', {
            'fields': ('get_full_name', 'get_sessions_count'),
            'classes': ['collapse']
        }),
    )
    
    # Поля для создания пользователя
    add_fieldsets = (
        ('Создание пользователя', {
            'classes': ['wide'],
            'fields': (
                'email', 'username', 'password1', 'password2',
                'first_name', 'last_name', 'role', 'is_active'
            ),
        }),
    )
    
    # Действия
    actions = ['activate_users', 'deactivate_users', 'unlock_users', 'reset_passwords']
    
    def get_full_name(self, obj):
        """Полное имя пользователя"""
        return obj.get_full_name()
    get_full_name.short_description = 'Полное имя'
    
    def is_locked_display(self, obj):
        """Отображение статуса блокировки"""
        if obj.is_locked:
            return format_html(
                '<span style="color: red;">🔒 Заблокирован</span>'
            )
        return format_html(
            '<span style="color: green;">✓ Активен</span>'
        )
    is_locked_display.short_description = 'Статус'
    
    def get_sessions_count(self, obj):
        """Количество активных сессий"""
        count = obj.sessions.filter(is_active=True).count()
        if count > 0:
            url = reverse('admin:users_usersession_changelist')
            return format_html(
                '<a href="{}?user__id__exact={}">{} активных</a>',
                url, obj.id, count
            )
        return '0 активных'
    get_sessions_count.short_description = 'Активные сессии'
    
    # Массовые действия
    def activate_users(self, request, queryset):
        """Активация пользователей"""
        count = queryset.update(is_active=True)
        self.message_user(request, f'Активировано {count} пользователей.')
    activate_users.short_description = 'Активировать выбранных пользователей'
    
    def deactivate_users(self, request, queryset):
        """Деактивация пользователей"""
        count = queryset.update(is_active=False)
        self.message_user(request, f'Деактивировано {count} пользователей.')
    deactivate_users.short_description = 'Деактивировать выбранных пользователей'
    
    def unlock_users(self, request, queryset):
        """Разблокировка пользователей"""
        count = 0
        for user in queryset:
            if user.is_locked:
                user.unlock_account()
                count += 1
        self.message_user(request, f'Разблокировано {count} пользователей.')
    unlock_users.short_description = 'Разблокировать выбранных пользователей'
    
    def reset_passwords(self, request, queryset):
        """Сброс паролей пользователей"""
        count = queryset.update(must_change_password=True)
        self.message_user(
            request,
            f'Для {count} пользователей установлен флаг смены пароля.'
        )
    reset_passwords.short_description = 'Требовать смену пароля'


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    """
    Административный интерфейс для профилей пользователей
    """
    list_display = [
        'user', 'get_user_role', 'department', 'hire_date',
        'email_notifications', 'theme'
    ]
    
    search_fields = ['user__email', 'user__first_name', 'user__last_name', 'department']
    
    list_filter = [
        'department', 'email_notifications', 'sms_notifications',
        'theme', 'language', 'hire_date'
    ]
    
    readonly_fields = ['created_at', 'updated_at', 'deleted_at']
    
    fieldsets = (
        ('Основная информация', {
            'fields': ('user', 'avatar', 'bio', 'birth_date')
        }),
        ('Рабочая информация', {
            'fields': ('department', 'hire_date', 'supervisor')
        }),
        ('Настройки уведомлений', {
            'fields': ('email_notifications', 'sms_notifications')
        }),
        ('Настройки интерфейса', {
            'fields': ('theme', 'language')
        }),
        ('Метаданные', {
            'fields': ('created_at', 'updated_at', 'deleted_at'),
            'classes': ['collapse']
        }),
    )
    
    def get_user_role(self, obj):
        """Роль пользователя"""
        return obj.user.get_role_display()
    get_user_role.short_description = 'Роль'


@admin.register(UserSession)
class UserSessionAdmin(admin.ModelAdmin):
    """
    Административный интерфейс для сессий пользователей
    """
    list_display = [
        'user', 'get_browser_info', 'ip_address',
        'created_at', 'last_activity', 'is_active'
    ]
    
    search_fields = ['user__email', 'user__first_name', 'user__last_name', 'ip_address']
    
    list_filter = ['is_active', 'created_at', 'last_activity']
    
    readonly_fields = [
        'session_key', 'created_at', 'last_activity',
        'get_browser_info', 'duration'
    ]
    
    ordering = ['-last_activity']
    
    fieldsets = (
        ('Информация о сессии', {
            'fields': ('user', 'session_key', 'is_active')
        }),
        ('Техническая информация', {
            'fields': ('ip_address', 'user_agent', 'get_browser_info')
        }),
        ('Временные метки', {
            'fields': ('created_at', 'last_activity', 'duration')
        }),
    )
    
    actions = ['terminate_sessions']
    
    def terminate_sessions(self, request, queryset):
        """Завершение сессий"""
        count = queryset.update(is_active=False)
        self.message_user(request, f'Завершено {count} сессий.')
    terminate_sessions.short_description = 'Завершить выбранные сессии'
    
    def get_browser_info(self, obj):
        """Информация о браузере"""
        return obj.get_browser_info()
    get_browser_info.short_description = 'Браузер'
    
    def duration(self, obj):
        """Продолжительность сессии"""
        return obj.duration
    duration.short_description = 'Длительность'


# Настройки административного интерфейса
admin.site.site_header = 'Система управления дефектами'
admin.site.site_title = 'Админ-панель'
admin.site.index_title = 'Добро пожаловать в административную панель'
