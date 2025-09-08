"""
Users app configuration
"""

from django.apps import AppConfig


class UsersConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.users'
    verbose_name = 'Пользователи и аутентификация'
    
    def ready(self):
        """
        Импортируем signals при готовности приложения
        """
        try:
            import apps.users.signals  # noqa
        except ImportError:
            pass
