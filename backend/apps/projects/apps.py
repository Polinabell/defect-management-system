"""
Projects app configuration
"""

from django.apps import AppConfig


class ProjectsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.projects'
    verbose_name = 'Управление проектами'
    
    def ready(self):
        """
        Импортируем signals при готовности приложения
        """
        try:
            import apps.projects.signals  # noqa
        except ImportError:
            pass
