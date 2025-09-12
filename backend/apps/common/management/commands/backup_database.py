"""
Management команда для резервного копирования базы данных
"""

import os
import shutil
import zipfile
from datetime import datetime, timedelta
from django.core.management.base import BaseCommand, CommandError
from django.conf import settings
from django.db import connection
import logging

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Создает резервную копию базы данных'

    def add_arguments(self, parser):
        parser.add_argument(
            '--output-dir',
            type=str,
            default=getattr(settings, 'BACKUP_DIR', 'backups'),
            help='Директория для сохранения резервных копий'
        )
        parser.add_argument(
            '--keep-days',
            type=int,
            default=30,
            help='Количество дней для хранения резервных копий'
        )
        parser.add_argument(
            '--compress',
            action='store_true',
            help='Сжимать резервные копии'
        )

    def handle(self, *args, **options):
        output_dir = options['output_dir']
        keep_days = options['keep_days']
        compress = options['compress']

        try:
            # Создаем директорию для резервных копий
            os.makedirs(output_dir, exist_ok=True)

            # Получаем информацию о базе данных
            db_info = self.get_database_info()
            
            # Создаем резервную копию
            backup_file = self.create_backup(output_dir, db_info, compress)
            
            # Очищаем старые резервные копии
            self.cleanup_old_backups(output_dir, keep_days)
            
            self.stdout.write(
                self.style.SUCCESS(
                    f'Резервная копия успешно создана: {backup_file}'
                )
            )
            
            logger.info(f'Резервная копия создана: {backup_file}')
            
        except Exception as e:
            error_msg = f'Ошибка создания резервной копии: {str(e)}'
            self.stdout.write(self.style.ERROR(error_msg))
            logger.error(error_msg)
            raise CommandError(error_msg)

    def get_database_info(self):
        """Получает информацию о базе данных"""
        db_settings = settings.DATABASES['default']
        
        return {
            'engine': db_settings['ENGINE'],
            'name': db_settings['NAME'],
            'user': db_settings.get('USER', ''),
            'host': db_settings.get('HOST', ''),
            'port': db_settings.get('PORT', ''),
        }

    def create_backup(self, output_dir, db_info, compress):
        """Создает резервную копию базы данных"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        if 'sqlite' in db_info['engine']:
            return self.backup_sqlite(db_info, output_dir, timestamp, compress)
        elif 'postgresql' in db_info['engine']:
            return self.backup_postgresql(db_info, output_dir, timestamp, compress)
        elif 'mysql' in db_info['engine']:
            return self.backup_mysql(db_info, output_dir, timestamp, compress)
        else:
            raise CommandError(f'Неподдерживаемый тип базы данных: {db_info["engine"]}')

    def backup_sqlite(self, db_info, output_dir, timestamp, compress):
        """Создает резервную копию SQLite базы данных"""
        db_path = db_info['name']
        
        if not os.path.exists(db_path):
            raise CommandError(f'Файл базы данных не найден: {db_path}')
        
        backup_filename = f'sqlite_backup_{timestamp}.db'
        backup_path = os.path.join(output_dir, backup_filename)
        
        # Копируем файл базы данных
        shutil.copy2(db_path, backup_path)
        
        if compress:
            # Сжимаем резервную копию
            compressed_path = f'{backup_path}.zip'
            with zipfile.ZipFile(compressed_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                zipf.write(backup_path, backup_filename)
            
            # Удаляем несжатую копию
            os.remove(backup_path)
            return compressed_path
        
        return backup_path

    def backup_postgresql(self, db_info, output_dir, timestamp, compress):
        """Создает резервную копию PostgreSQL базы данных"""
        import subprocess
        
        backup_filename = f'postgresql_backup_{timestamp}.sql'
        backup_path = os.path.join(output_dir, backup_filename)
        
        # Формируем команду pg_dump
        cmd = ['pg_dump']
        
        if db_info['host']:
            cmd.extend(['-h', db_info['host']])
        if db_info['port']:
            cmd.extend(['-p', str(db_info['port'])])
        if db_info['user']:
            cmd.extend(['-U', db_info['user']])
        
        cmd.extend(['-d', db_info['name']])
        
        # Выполняем резервное копирование
        with open(backup_path, 'w') as f:
            result = subprocess.run(cmd, stdout=f, stderr=subprocess.PIPE, text=True)
            
            if result.returncode != 0:
                raise CommandError(f'Ошибка pg_dump: {result.stderr}')
        
        if compress:
            # Сжимаем резервную копию
            compressed_path = f'{backup_path}.gz'
            import gzip
            
            with open(backup_path, 'rb') as f_in:
                with gzip.open(compressed_path, 'wb') as f_out:
                    shutil.copyfileobj(f_in, f_out)
            
            # Удаляем несжатую копию
            os.remove(backup_path)
            return compressed_path
        
        return backup_path

    def backup_mysql(self, db_info, output_dir, timestamp, compress):
        """Создает резервную копию MySQL базы данных"""
        import subprocess
        
        backup_filename = f'mysql_backup_{timestamp}.sql'
        backup_path = os.path.join(output_dir, backup_filename)
        
        # Формируем команду mysqldump
        cmd = ['mysqldump']
        
        if db_info['host']:
            cmd.extend(['-h', db_info['host']])
        if db_info['port']:
            cmd.extend(['-P', str(db_info['port'])])
        if db_info['user']:
            cmd.extend(['-u', db_info['user']])
        
        # Добавляем пароль если есть
        password = settings.DATABASES['default'].get('PASSWORD', '')
        if password:
            cmd.extend([f'-p{password}'])
        
        cmd.append(db_info['name'])
        
        # Выполняем резервное копирование
        with open(backup_path, 'w') as f:
            result = subprocess.run(cmd, stdout=f, stderr=subprocess.PIPE, text=True)
            
            if result.returncode != 0:
                raise CommandError(f'Ошибка mysqldump: {result.stderr}')
        
        if compress:
            # Сжимаем резервную копию
            compressed_path = f'{backup_path}.gz'
            import gzip
            
            with open(backup_path, 'rb') as f_in:
                with gzip.open(compressed_path, 'wb') as f_out:
                    shutil.copyfileobj(f_in, f_out)
            
            # Удаляем несжатую копию
            os.remove(backup_path)
            return compressed_path
        
        return backup_path

    def cleanup_old_backups(self, output_dir, keep_days):
        """Удаляет старые резервные копии"""
        cutoff_date = datetime.now() - timedelta(days=keep_days)
        deleted_count = 0
        
        for filename in os.listdir(output_dir):
            file_path = os.path.join(output_dir, filename)
            
            if os.path.isfile(file_path):
                # Получаем время создания файла
                file_time = datetime.fromtimestamp(os.path.getctime(file_path))
                
                if file_time < cutoff_date:
                    try:
                        os.remove(file_path)
                        deleted_count += 1
                        logger.info(f'Удалена старая резервная копия: {filename}')
                    except OSError as e:
                        logger.error(f'Ошибка удаления файла {filename}: {str(e)}')
        
        if deleted_count > 0:
            self.stdout.write(
                self.style.WARNING(
                    f'Удалено {deleted_count} старых резервных копий'
                )
            )