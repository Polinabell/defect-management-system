"""
Команда для создания резервной копии базы данных
"""

import os
import gzip
import subprocess
from datetime import datetime
from django.core.management.base import BaseCommand, CommandError
from django.conf import settings
from django.db import connection


class Command(BaseCommand):
    help = 'Создание резервной копии базы данных'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--output-dir',
            type=str,
            default='backups',
            help='Директория для сохранения резервных копий'
        )
        parser.add_argument(
            '--compress',
            action='store_true',
            help='Сжать резервную копию с помощью gzip'
        )
        parser.add_argument(
            '--keep-days',
            type=int,
            default=30,
            help='Количество дней хранения старых резервных копий'
        )
    
    def handle(self, *args, **options):
        """Основная логика команды"""
        try:
            # Создаём директорию для резервных копий
            backup_dir = options['output_dir']
            os.makedirs(backup_dir, exist_ok=True)
            
            # Генерируем имя файла
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"backup_{timestamp}.sql"
            filepath = os.path.join(backup_dir, filename)
            
            # Создаём резервную копию
            self.stdout.write(f"Создание резервной копии: {filepath}")
            self._create_backup(filepath)
            
            # Сжимаем файл если нужно
            if options['compress']:
                compressed_filepath = f"{filepath}.gz"
                self._compress_file(filepath, compressed_filepath)
                os.remove(filepath)
                filepath = compressed_filepath
                self.stdout.write(f"Файл сжат: {compressed_filepath}")
            
            # Удаляем старые резервные копии
            self._cleanup_old_backups(backup_dir, options['keep_days'])
            
            # Проверяем размер файла
            file_size = os.path.getsize(filepath)
            self.stdout.write(
                self.style.SUCCESS(
                    f"Резервная копия создана успешно: {filepath} ({file_size} байт)"
                )
            )
            
        except Exception as e:
            raise CommandError(f"Ошибка создания резервной копии: {str(e)}")
    
    def _create_backup(self, filepath):
        """Создание резервной копии базы данных"""
        db_config = settings.DATABASES['default']
        
        if db_config['ENGINE'] == 'django.db.backends.postgresql':
            self._backup_postgresql(filepath, db_config)
        elif db_config['ENGINE'] == 'django.db.backends.mysql':
            self._backup_mysql(filepath, db_config)
        elif db_config['ENGINE'] == 'django.db.backends.sqlite3':
            self._backup_sqlite(filepath, db_config)
        else:
            raise CommandError(f"Неподдерживаемая СУБД: {db_config['ENGINE']}")
    
    def _backup_postgresql(self, filepath, db_config):
        """Резервная копия PostgreSQL"""
        cmd = [
            'pg_dump',
            f"--host={db_config['HOST']}",
            f"--port={db_config['PORT']}",
            f"--username={db_config['USER']}",
            f"--dbname={db_config['NAME']}",
            '--no-password',
            '--verbose',
            '--clean',
            '--no-acl',
            '--no-owner',
            f"--file={filepath}"
        ]
        
        env = os.environ.copy()
        env['PGPASSWORD'] = db_config['PASSWORD']
        
        result = subprocess.run(cmd, env=env, capture_output=True, text=True)
        
        if result.returncode != 0:
            raise CommandError(f"Ошибка pg_dump: {result.stderr}")
    
    def _backup_mysql(self, filepath, db_config):
        """Резервная копия MySQL"""
        cmd = [
            'mysqldump',
            f"--host={db_config['HOST']}",
            f"--port={db_config['PORT']}",
            f"--user={db_config['USER']}",
            f"--password={db_config['PASSWORD']}",
            '--single-transaction',
            '--routines',
            '--triggers',
            '--result-file=' + filepath,
            db_config['NAME']
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode != 0:
            raise CommandError(f"Ошибка mysqldump: {result.stderr}")
    
    def _backup_sqlite(self, filepath, db_config):
        """Резервная копия SQLite"""
        import shutil
        shutil.copy2(db_config['NAME'], filepath)
    
    def _compress_file(self, input_filepath, output_filepath):
        """Сжатие файла с помощью gzip"""
        with open(input_filepath, 'rb') as f_in:
            with gzip.open(output_filepath, 'wb') as f_out:
                f_out.writelines(f_in)
    
    def _cleanup_old_backups(self, backup_dir, keep_days):
        """Удаление старых резервных копий"""
        import time
        
        cutoff_time = time.time() - (keep_days * 24 * 60 * 60)
        removed_count = 0
        
        for filename in os.listdir(backup_dir):
            if filename.startswith('backup_'):
                filepath = os.path.join(backup_dir, filename)
                if os.path.getctime(filepath) < cutoff_time:
                    os.remove(filepath)
                    removed_count += 1
                    self.stdout.write(f"Удалён старый бэкап: {filename}")
        
        if removed_count > 0:
            self.stdout.write(f"Удалено старых резервных копий: {removed_count}")
        else:
            self.stdout.write("Старых резервных копий для удаления не найдено")
