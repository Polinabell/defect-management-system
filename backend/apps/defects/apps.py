"""
Defects app configuration
"""

from django.apps import AppConfig


class DefectsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.defects'
    verbose_name = 'Управление дефектами'
    
    def ready(self):
        """
        Импортируем signals при готовности приложения
        """
        try:
            import apps.defects.signals  # noqa
        except ImportError:
            pass
