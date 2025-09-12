"""
Management команда для проверки безопасности
"""

import os
import subprocess
from django.core.management.base import BaseCommand, CommandError


class Command(BaseCommand):
    help = 'Проверяет безопасность системы'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Проверка безопасности...'))
        
        issues = []
        issues.extend(self.check_settings())
        issues.extend(self.check_dependencies())
        
        if issues:
            self.stdout.write(self.style.ERROR('Проблемы безопасности:'))
            for issue in issues:
                self.stdout.write(self.style.WARNING(f'  - {issue}'))
        else:
            self.stdout.write(self.style.SUCCESS('Проблем не обнаружено.'))

    def check_settings(self):
        """Проверяет настройки безопасности"""
        issues = []
        
        from django.conf import settings
        
        if settings.DEBUG:
            issues.append('DEBUG включен')
        
        if '*' in settings.ALLOWED_HOSTS:
            issues.append('ALLOWED_HOSTS содержит *')
        
        return issues

    def check_dependencies(self):
        """Проверяет зависимости"""
        issues = []
        
        try:
            result = subprocess.run(['safety', 'check'], 
                                  capture_output=True, text=True)
            if result.returncode != 0:
                issues.append('Уязвимости в зависимостях')
        except FileNotFoundError:
            issues.append('safety не установлен')
        
        return issues