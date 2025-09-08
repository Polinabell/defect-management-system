"""
Команда для очистки логов
"""

import os
import gzip
from datetime import datetime, timedelta
from django.core.management.base import BaseCommand
from django.conf import settings


class Command(BaseCommand):
    help = 'Очистка и архивирование логов'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--days',
            type=int,
            default=30,
            help='Количество дней для хранения логов (по умолчанию 30)'
        )
        parser.add_argument(
            '--compress',
            action='store_true',
            help='Сжимать старые логи вместо удаления'
        )
        parser.add_argument(
            '--logs-dir',
            type=str,
            default='logs',
            help='Директория с логами'
        )
    
    def handle(self, *args, **options):
        """Основная логика команды"""
        logs_dir = options['logs_dir']
        days_to_keep = options['days']
        compress_old = options['compress']
        
        if not os.path.exists(logs_dir):
            self.stdout.write(
                self.style.WARNING(f"Директория логов не найдена: {logs_dir}")
            )
            return
        
        cutoff_date = datetime.now() - timedelta(days=days_to_keep)
        processed_files = 0
        total_size_freed = 0
        
        self.stdout.write(f"Обработка логов старше {cutoff_date.strftime('%Y-%m-%d %H:%M:%S')}")
        
        for filename in os.listdir(logs_dir):
            filepath = os.path.join(logs_dir, filename)
            
            if not os.path.isfile(filepath):
                continue
            
            # Пропускаем уже сжатые файлы
            if filename.endswith('.gz'):
                continue
            
            # Проверяем дату модификации файла
            file_modified = datetime.fromtimestamp(os.path.getmtime(filepath))
            
            if file_modified < cutoff_date:
                file_size = os.path.getsize(filepath)
                
                if compress_old:
                    # Сжимаем файл
                    compressed_filepath = f"{filepath}.gz"
                    self._compress_log_file(filepath, compressed_filepath)
                    
                    compressed_size = os.path.getsize(compressed_filepath)
                    compression_ratio = (1 - compressed_size / file_size) * 100
                    
                    self.stdout.write(
                        f"Сжат: {filename} "
                        f"({self._format_size(file_size)} -> {self._format_size(compressed_size)}, "
                        f"сжатие {compression_ratio:.1f}%)"
                    )
                    
                    # Удаляем оригинальный файл
                    os.remove(filepath)
                    total_size_freed += file_size - compressed_size
                else:
                    # Удаляем файл
                    os.remove(filepath)
                    self.stdout.write(f"Удалён: {filename} ({self._format_size(file_size)})")
                    total_size_freed += file_size
                
                processed_files += 1
        
        # Очищаем старые сжатые логи (старше удвоенного срока)
        if compress_old:
            old_compressed_cutoff = datetime.now() - timedelta(days=days_to_keep * 2)
            self._cleanup_old_compressed_logs(logs_dir, old_compressed_cutoff)
        
        if processed_files > 0:
            self.stdout.write(
                self.style.SUCCESS(
                    f"Обработано файлов: {processed_files}, "
                    f"освобождено места: {self._format_size(total_size_freed)}"
                )
            )
        else:
            self.stdout.write("Логов для очистки не найдено")
    
    def _compress_log_file(self, input_filepath, output_filepath):
        """Сжатие лог файла"""
        with open(input_filepath, 'rb') as f_in:
            with gzip.open(output_filepath, 'wb') as f_out:
                f_out.writelines(f_in)
    
    def _cleanup_old_compressed_logs(self, logs_dir, cutoff_date):
        """Удаление старых сжатых логов"""
        removed_count = 0
        removed_size = 0
        
        for filename in os.listdir(logs_dir):
            if not filename.endswith('.gz'):
                continue
            
            filepath = os.path.join(logs_dir, filename)
            file_modified = datetime.fromtimestamp(os.path.getmtime(filepath))
            
            if file_modified < cutoff_date:
                file_size = os.path.getsize(filepath)
                os.remove(filepath)
                
                self.stdout.write(f"Удалён старый сжатый лог: {filename}")
                removed_count += 1
                removed_size += file_size
        
        if removed_count > 0:
            self.stdout.write(
                f"Удалено старых сжатых логов: {removed_count} "
                f"({self._format_size(removed_size)})"
            )
    
    def _format_size(self, size_bytes):
        """Форматирование размера файла"""
        if size_bytes == 0:
            return "0 B"
        
        size_names = ["B", "KB", "MB", "GB"]
        i = 0
        
        while size_bytes >= 1024 and i < len(size_names) - 1:
            size_bytes /= 1024.0
            i += 1
        
        return f"{size_bytes:.1f} {size_names[i]}"
