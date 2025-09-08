"""
Общие утилиты для всех приложений
"""

import os
import uuid
import mimetypes
from datetime import datetime
from typing import Dict, Any, Optional
from django.core.exceptions import ValidationError
from django.utils.text import slugify
from django.conf import settings


def generate_file_path(instance, filename: str, subfolder: str = '') -> str:
    """
    Генерация пути для загружаемых файлов
    """
    # Получаем расширение файла
    ext = filename.split('.')[-1].lower() if '.' in filename else ''
    
    # Генерируем уникальное имя файла
    unique_filename = f"{uuid.uuid4().hex}.{ext}" if ext else str(uuid.uuid4().hex)
    
    # Создаём путь с учётом даты
    date_path = datetime.now().strftime('%Y/%m/%d')
    
    if subfolder:
        return f"{subfolder}/{date_path}/{unique_filename}"
    else:
        return f"uploads/{date_path}/{unique_filename}"


def format_file_size(size_bytes: int) -> str:
    """
    Форматирование размера файла в человекочитаемый вид
    """
    if size_bytes == 0:
        return "0 B"
    
    size_names = ["B", "KB", "MB", "GB", "TB"]
    i = 0
    
    while size_bytes >= 1024 and i < len(size_names) - 1:
        size_bytes /= 1024.0
        i += 1
    
    return f"{size_bytes:.1f} {size_names[i]}"


def get_client_ip(request) -> Optional[str]:
    """
    Получение IP адреса клиента
    """
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


def create_slug(text: str, max_length: int = 50) -> str:
    """
    Создание slug из текста
    """
    slug = slugify(text, allow_unicode=True)
    if len(slug) > max_length:
        slug = slug[:max_length].rstrip('-')
    return slug


class FileUploadHandler:
    """
    Класс для обработки загрузки файлов
    """
    
    # Максимальные размеры файлов (в байтах)
    MAX_IMAGE_SIZE = 10 * 1024 * 1024  # 10MB
    MAX_DOCUMENT_SIZE = 50 * 1024 * 1024  # 50MB
    MAX_VIDEO_SIZE = 100 * 1024 * 1024  # 100MB
    
    # Разрешённые типы файлов
    ALLOWED_IMAGE_TYPES = [
        'image/jpeg', 'image/jpg', 'image/png', 'image/gif', 'image/webp'
    ]
    
    ALLOWED_DOCUMENT_TYPES = [
        'application/pdf',
        'application/msword',
        'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
        'application/vnd.ms-excel',
        'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        'text/plain',
        'text/csv'
    ]
    
    ALLOWED_VIDEO_TYPES = [
        'video/mp4', 'video/avi', 'video/mov', 'video/wmv'
    ]
    
    @classmethod
    def validate_file(cls, file, file_type: str = 'image') -> Dict[str, Any]:
        """
        Валидация загружаемого файла
        """
        result = {
            'valid': True,
            'errors': [],
            'file_info': {}
        }
        
        # Проверяем размер файла
        if file_type == 'image':
            max_size = cls.MAX_IMAGE_SIZE
            allowed_types = cls.ALLOWED_IMAGE_TYPES
        elif file_type == 'document':
            max_size = cls.MAX_DOCUMENT_SIZE
            allowed_types = cls.ALLOWED_DOCUMENT_TYPES
        elif file_type == 'video':
            max_size = cls.MAX_VIDEO_SIZE
            allowed_types = cls.ALLOWED_VIDEO_TYPES
        else:
            result['valid'] = False
            result['errors'].append("Неподдерживаемый тип файла")
            return result
        
        # Проверка размера
        if file.size > max_size:
            result['valid'] = False
            result['errors'].append(
                f"Размер файла превышает максимально допустимый ({format_file_size(max_size)})"
            )
        
        # Проверка MIME типа
        mime_type, _ = mimetypes.guess_type(file.name)
        if mime_type not in allowed_types:
            result['valid'] = False
            result['errors'].append(f"Недопустимый тип файла: {mime_type}")
        
        # Информация о файле
        result['file_info'] = {
            'name': file.name,
            'size': file.size,
            'mime_type': mime_type,
            'formatted_size': format_file_size(file.size)
        }
        
        return result
    
    @classmethod
    def validate_image(cls, file) -> Dict[str, Any]:
        """Валидация изображения"""
        return cls.validate_file(file, 'image')
    
    @classmethod
    def validate_document(cls, file) -> Dict[str, Any]:
        """Валидация документа"""
        return cls.validate_file(file, 'document')
    
    @classmethod
    def validate_video(cls, file) -> Dict[str, Any]:
        """Валидация видео"""
        return cls.validate_file(file, 'video')


def send_notification_email(subject: str, message: str, recipient_list: list,
                          template_name: Optional[str] = None, 
                          context: Optional[Dict[str, Any]] = None) -> bool:
    """
    Отправка email уведомления
    """
    try:
        from django.core.mail import send_mail
        from django.template.loader import render_to_string
        
        if template_name and context:
            # Используем шаблон
            html_message = render_to_string(template_name, context)
            send_mail(
                subject=subject,
                message=message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=recipient_list,
                html_message=html_message,
                fail_silently=False
            )
        else:
            # Простое текстовое сообщение
            send_mail(
                subject=subject,
                message=message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=recipient_list,
                fail_silently=False
            )
        
        return True
        
    except Exception as e:
        # Логируем ошибку
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"Ошибка отправки email: {str(e)}")
        return False


def generate_unique_code(length: int = 8, prefix: str = '') -> str:
    """
    Генерация уникального кода
    """
    import random
    import string
    
    characters = string.ascii_uppercase + string.digits
    code = ''.join(random.choice(characters) for _ in range(length))
    
    return f"{prefix}{code}" if prefix else code


def validate_phone_number(phone: str) -> bool:
    """
    Валидация номера телефона
    """
    import re
    
    # Удаляем все символы кроме цифр и +
    cleaned_phone = re.sub(r'[^\d+]', '', phone)
    
    # Проверяем российские номера
    patterns = [
        r'^\+7\d{10}$',  # +7XXXXXXXXXX
        r'^8\d{10}$',    # 8XXXXXXXXXX
        r'^7\d{10}$',    # 7XXXXXXXXXX
    ]
    
    for pattern in patterns:
        if re.match(pattern, cleaned_phone):
            return True
    
    return False


def truncate_text(text: str, max_length: int = 100, suffix: str = '...') -> str:
    """
    Обрезка текста с добавлением суффикса
    """
    if len(text) <= max_length:
        return text
    
    return text[:max_length - len(suffix)].rstrip() + suffix


class CacheKeyBuilder:
    """
    Класс для построения ключей кэша
    """
    
    @staticmethod
    def user_key(user_id: int, suffix: str = '') -> str:
        """Ключ кэша для пользователя"""
        base_key = f"user:{user_id}"
        return f"{base_key}:{suffix}" if suffix else base_key
    
    @staticmethod
    def project_key(project_id: int, suffix: str = '') -> str:
        """Ключ кэша для проекта"""
        base_key = f"project:{project_id}"
        return f"{base_key}:{suffix}" if suffix else base_key
    
    @staticmethod
    def defect_key(defect_id: int, suffix: str = '') -> str:
        """Ключ кэша для дефекта"""
        base_key = f"defect:{defect_id}"
        return f"{base_key}:{suffix}" if suffix else base_key
    
    @staticmethod
    def analytics_key(key_type: str, identifier: str = '', suffix: str = '') -> str:
        """Ключ кэша для аналитики"""
        base_key = f"analytics:{key_type}"
        if identifier:
            base_key += f":{identifier}"
        return f"{base_key}:{suffix}" if suffix else base_key


def clean_html(text: str) -> str:
    """
    Очистка HTML тегов из текста
    """
    import re
    
    # Удаляем HTML теги
    clean_text = re.sub(r'<[^>]+>', '', text)
    
    # Декодируем HTML entities
    import html
    clean_text = html.unescape(clean_text)
    
    return clean_text.strip()


def get_model_changes(instance, original_data: Dict[str, Any]) -> Dict[str, Dict[str, Any]]:
    """
    Получение изменений модели для логирования
    """
    changes = {}
    
    for field_name, original_value in original_data.items():
        current_value = getattr(instance, field_name, None)
        
        if current_value != original_value:
            changes[field_name] = {
                'old': original_value,
                'new': current_value
            }
    
    return changes