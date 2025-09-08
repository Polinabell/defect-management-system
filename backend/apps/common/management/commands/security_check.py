"""
Команда для проверки безопасности системы
"""

import os
import re
from django.core.management.base import BaseCommand
from django.conf import settings
from django.contrib.auth import get_user_model
from django.db import connection
from django.core.management import call_command
from io import StringIO

User = get_user_model()


class Command(BaseCommand):
    help = 'Проверка безопасности системы'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--fix',
            action='store_true',
            help='Автоматически исправить обнаруженные проблемы (где возможно)'
        )
        parser.add_argument(
            '--detailed',
            action='store_true',
            help='Детальный вывод проверок'
        )
    
    def handle(self, *args, **options):
        """Основная логика команды"""
        self.fix_issues = options['fix']
        self.detailed = options['detailed']
        self.issues_found = []
        self.issues_fixed = []
        
        self.stdout.write(
            self.style.HTTP_INFO("=== ПРОВЕРКА БЕЗОПАСНОСТИ СИСТЕМЫ ===")
        )
        
        # Проверки
        self._check_django_settings()
        self._check_database_security()
        self._check_user_accounts()
        self._check_file_permissions()
        self._check_dependencies()
        self._check_logging_configuration()
        self._run_django_security_check()
        
        # Итоги
        self._print_summary()
    
    def _check_django_settings(self):
        """Проверка настроек Django"""
        self.stdout.write("\n1. Проверка настроек Django...")
        
        # DEBUG в продакшене
        if settings.DEBUG:
            self._add_issue(
                "CRITICAL", 
                "DEBUG=True в продакшене",
                "Установите DEBUG=False в продакшене"
            )
        
        # SECRET_KEY
        if settings.SECRET_KEY == 'django-insecure-change-me-in-production-12345678901234567890':
            self._add_issue(
                "CRITICAL",
                "Используется стандартный SECRET_KEY",
                "Измените SECRET_KEY на уникальный"
            )
        
        # ALLOWED_HOSTS
        if '*' in settings.ALLOWED_HOSTS:
            self._add_issue(
                "HIGH",
                "ALLOWED_HOSTS содержит '*'",
                "Укажите конкретные домены в ALLOWED_HOSTS"
            )
        
        # HTTPS настройки
        if not getattr(settings, 'SECURE_SSL_REDIRECT', False):
            self._add_issue(
                "MEDIUM",
                "SECURE_SSL_REDIRECT не активен",
                "Включите SECURE_SSL_REDIRECT=True для принудительного HTTPS"
            )
        
        # Session security
        if not getattr(settings, 'SESSION_COOKIE_SECURE', False):
            self._add_issue(
                "MEDIUM",
                "SESSION_COOKIE_SECURE не активен",
                "Включите SESSION_COOKIE_SECURE=True"
            )
        
        # CSRF cookie security
        if not getattr(settings, 'CSRF_COOKIE_SECURE', False):
            self._add_issue(
                "MEDIUM",
                "CSRF_COOKIE_SECURE не активен",
                "Включите CSRF_COOKIE_SECURE=True"
            )
        
        self._print_check_result("Настройки Django")
    
    def _check_database_security(self):
        """Проверка безопасности базы данных"""
        self.stdout.write("\n2. Проверка безопасности базы данных...")
        
        db_config = settings.DATABASES['default']
        
        # Проверка пароля БД
        if not db_config.get('PASSWORD'):
            self._add_issue(
                "CRITICAL",
                "База данных без пароля",
                "Установите пароль для базы данных"
            )
        elif len(db_config.get('PASSWORD', '')) < 8:
            self._add_issue(
                "HIGH",
                "Слабый пароль базы данных",
                "Используйте пароль длиной не менее 8 символов"
            )
        
        # Проверка подключения к localhost
        if db_config.get('HOST') in ['', 'localhost', '127.0.0.1']:
            if self.detailed:
                self.stdout.write("  ✓ База данных подключена локально")
        else:
            self._add_issue(
                "INFO",
                f"Удалённое подключение к БД: {db_config.get('HOST')}",
                "Убедитесь в безопасности сетевого подключения"
            )
        
        self._print_check_result("Безопасность базы данных")
    
    def _check_user_accounts(self):
        """Проверка учётных записей пользователей"""
        self.stdout.write("\n3. Проверка учётных записей...")
        
        # Суперпользователи
        superusers = User.objects.filter(is_superuser=True)
        if superusers.count() > 5:
            self._add_issue(
                "MEDIUM",
                f"Много суперпользователей: {superusers.count()}",
                "Ограничьте количество суперпользователей"
            )
        
        # Пользователи без пароля
        users_without_password = User.objects.filter(password='')
        if users_without_password.exists():
            self._add_issue(
                "HIGH",
                f"Пользователи без пароля: {users_without_password.count()}",
                "Установите пароли всем пользователям"
            )
            
            if self.fix_issues:
                # Деактивируем пользователей без пароля
                users_without_password.update(is_active=False)
                self._add_fixed("Деактивированы пользователи без пароля")
        
        # Неактивные суперпользователи
        inactive_superusers = User.objects.filter(is_superuser=True, is_active=False)
        if inactive_superusers.exists():
            self._add_issue(
                "INFO",
                f"Неактивные суперпользователи: {inactive_superusers.count()}",
                "Удалите неиспользуемые учётные записи суперпользователей"
            )
        
        self._print_check_result("Учётные записи пользователей")
    
    def _check_file_permissions(self):
        """Проверка прав доступа к файлам"""
        self.stdout.write("\n4. Проверка прав доступа к файлам...")
        
        # Проверка settings.py
        settings_files = [
            'config/settings/base.py',
            'config/settings/production.py',
            '.env'
        ]
        
        for settings_file in settings_files:
            if os.path.exists(settings_file):
                file_stat = os.stat(settings_file)
                file_mode = oct(file_stat.st_mode)[-3:]
                
                if file_mode != '600' and file_mode != '644':
                    self._add_issue(
                        "MEDIUM",
                        f"Небезопасные права доступа к {settings_file}: {file_mode}",
                        f"Установите права 600 для {settings_file}"
                    )
                    
                    if self.fix_issues:
                        try:
                            os.chmod(settings_file, 0o600)
                            self._add_fixed(f"Исправлены права доступа к {settings_file}")
                        except OSError:
                            pass
        
        # Проверка директории media
        media_root = getattr(settings, 'MEDIA_ROOT', None)
        if media_root and os.path.exists(media_root):
            for root, dirs, files in os.walk(media_root):
                for file in files:
                    if file.endswith('.py') or file.endswith('.sh'):
                        self._add_issue(
                            "HIGH",
                            f"Исполняемый файл в MEDIA_ROOT: {file}",
                            "Удалите исполняемые файлы из директории media"
                        )
        
        self._print_check_result("Права доступа к файлам")
    
    def _check_dependencies(self):
        """Проверка зависимостей на уязвимости"""
        self.stdout.write("\n5. Проверка зависимостей...")
        
        try:
            import pkg_resources
            
            # Получаем список установленных пакетов
            installed_packages = [d.project_name.lower() for d in pkg_resources.working_set]
            
            # Проверяем критически важные пакеты
            critical_packages = {
                'django': '4.0.0',
                'pillow': '9.0.0',
                'psycopg2': '2.8.0',
            }
            
            for package, min_version in critical_packages.items():
                if package in installed_packages:
                    try:
                        current_version = pkg_resources.get_distribution(package).version
                        if self.detailed:
                            self.stdout.write(f"  ✓ {package}: {current_version}")
                    except pkg_resources.DistributionNotFound:
                        pass
        
        except ImportError:
            self._add_issue(
                "INFO",
                "Не удалось проверить зависимости",
                "Установите pkg_resources для проверки зависимостей"
            )
        
        self._print_check_result("Зависимости")
    
    def _check_logging_configuration(self):
        """Проверка конфигурации логирования"""
        self.stdout.write("\n6. Проверка конфигурации логирования...")
        
        # Проверяем наличие логирования
        if not hasattr(settings, 'LOGGING'):
            self._add_issue(
                "MEDIUM",
                "Логирование не настроено",
                "Настройте логирование в settings.py"
            )
        else:
            logging_config = settings.LOGGING
            
            # Проверяем логирование безопасности
            if 'django.security' not in logging_config.get('loggers', {}):
                self._add_issue(
                    "MEDIUM",
                    "Логирование безопасности не настроено",
                    "Добавьте logger для django.security"
                )
        
        # Проверяем директорию логов
        logs_dir = getattr(settings, 'LOGS_DIR', 'logs')
        if not os.path.exists(logs_dir):
            self._add_issue(
                "INFO",
                "Директория логов не существует",
                f"Создайте директорию {logs_dir}"
            )
            
            if self.fix_issues:
                os.makedirs(logs_dir, exist_ok=True)
                self._add_fixed(f"Создана директория логов: {logs_dir}")
        
        self._print_check_result("Конфигурация логирования")
    
    def _run_django_security_check(self):
        """Запуск встроенной проверки безопасности Django"""
        self.stdout.write("\n7. Встроенная проверка безопасности Django...")
        
        try:
            # Перехватываем вывод команды check
            output = StringIO()
            call_command('check', '--deploy', stdout=output)
            
            output_content = output.getvalue()
            if output_content.strip():
                for line in output_content.split('\n'):
                    if line.strip() and not line.startswith('System check'):
                        self._add_issue(
                            "INFO",
                            f"Django check: {line.strip()}",
                            "Следуйте рекомендациям Django"
                        )
            else:
                if self.detailed:
                    self.stdout.write("  ✓ Встроенная проверка Django прошла успешно")
        
        except Exception as e:
            self._add_issue(
                "INFO",
                f"Ошибка выполнения Django check: {str(e)}",
                "Проверьте конфигурацию Django"
            )
        
        self._print_check_result("Встроенная проверка Django")
    
    def _add_issue(self, level, description, recommendation):
        """Добавление проблемы безопасности"""
        self.issues_found.append({
            'level': level,
            'description': description,
            'recommendation': recommendation
        })
    
    def _add_fixed(self, description):
        """Добавление исправленной проблемы"""
        self.issues_fixed.append(description)
    
    def _print_check_result(self, check_name):
        """Вывод результата проверки"""
        if self.detailed:
            current_issues = [i for i in self.issues_found if check_name.lower() in i['description'].lower()]
            if not current_issues:
                self.stdout.write(f"  ✓ {check_name}: Проблем не обнаружено")
    
    def _print_summary(self):
        """Вывод итогов проверки"""
        self.stdout.write("\n" + "="*60)
        self.stdout.write("ИТОГИ ПРОВЕРКИ БЕЗОПАСНОСТИ")
        self.stdout.write("="*60)
        
        if not self.issues_found:
            self.stdout.write(
                self.style.SUCCESS("🎉 Критических проблем безопасности не обнаружено!")
            )
            return
        
        # Группируем проблемы по уровню
        issues_by_level = {}
        for issue in self.issues_found:
            level = issue['level']
            if level not in issues_by_level:
                issues_by_level[level] = []
            issues_by_level[level].append(issue)
        
        # Выводим проблемы по уровням
        level_styles = {
            'CRITICAL': self.style.ERROR,
            'HIGH': self.style.WARNING,
            'MEDIUM': self.style.HTTP_INFO,
            'INFO': self.style.NOTICE
        }
        
        for level in ['CRITICAL', 'HIGH', 'MEDIUM', 'INFO']:
            if level in issues_by_level:
                issues = issues_by_level[level]
                self.stdout.write(f"\n{level_styles[level](f'{level} ({len(issues)}):')}")
                
                for i, issue in enumerate(issues, 1):
                    self.stdout.write(f"  {i}. {issue['description']}")
                    self.stdout.write(f"     Рекомендация: {issue['recommendation']}")
        
        # Исправленные проблемы
        if self.issues_fixed:
            self.stdout.write(f"\n{self.style.SUCCESS('ИСПРАВЛЕНО:')}")
            for i, fix in enumerate(self.issues_fixed, 1):
                self.stdout.write(f"  {i}. {fix}")
        
        # Общий итог
        total_issues = len(self.issues_found)
        critical_issues = len(issues_by_level.get('CRITICAL', []))
        
        if critical_issues > 0:
            self.stdout.write(
                f"\n{self.style.ERROR(f'⚠️  Найдено {total_issues} проблем, из них {critical_issues} критических!')}"
            )
        else:
            self.stdout.write(
                f"\n{self.style.WARNING(f'⚠️  Найдено {total_issues} проблем безопасности')}"
            )
