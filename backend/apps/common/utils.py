"""
Общие утилиты и хелперы
"""

import os
import uuid
import hashlib
from typing import Any, Dict, List, Optional
from django.core.files.storage import default_storage
from django.core.files.uploadedfile import UploadedFile
from django.utils.text import slugify
from django.utils import timezone


def generate_file_path(instance, filename: str, subfolder: str = '') -> str:
    """
    Генерирует уникальный путь для загружаемого файла
    
    Args:
        instance: Экземпляр модели
        filename: Оригинальное имя файла
        subfolder: Подпапка для организации файлов
    
    Returns:
        str: Уникальный путь к файлу
    """
    # Получаем расширение файла
    ext = filename.split('.')[-1].lower()
    
    # Генерируем уникальное имя
    unique_filename = f"{uuid.uuid4().hex}.{ext}"
    
    # Определяем путь
    year = timezone.now().year
    month = timezone.now().month
    
    if subfolder:
        return f"{subfolder}/{year}/{month:02d}/{unique_filename}"
    else:
        return f"uploads/{year}/{month:02d}/{unique_filename}"


def get_file_hash(file: UploadedFile) -> str:
    """
    Вычисляет MD5 хеш файла
    
    Args:
        file: Загружаемый файл
    
    Returns:
        str: MD5 хеш файла
    """
    hash_md5 = hashlib.md5()
    for chunk in file.chunks():
        hash_md5.update(chunk)
    return hash_md5.hexdigest()


def validate_file_type(file: UploadedFile, allowed_types: List[str]) -> bool:
    """
    Проверяет тип файла
    
    Args:
        file: Загружаемый файл
        allowed_types: Список разрешённых MIME типов
    
    Returns:
        bool: True если тип разрешён
    """
    if file.content_type in allowed_types:
        return True
    
    # Дополнительная проверка по расширению
    ext = file.name.lower().split('.')[-1]
    allowed_extensions = {
        'image/jpeg': ['jpg', 'jpeg'],
        'image/png': ['png'],
        'image/gif': ['gif'],
        'application/pdf': ['pdf'],
        'application/msword': ['doc'],
        'application/vnd.openxmlformats-officedocument.wordprocessingml.document': ['docx'],
    }
    
    for mime_type, extensions in allowed_extensions.items():
        if mime_type in allowed_types and ext in extensions:
            return True
    
    return False


def get_client_ip(request) -> str:
    """
    Получает IP адрес клиента с учётом прокси
    
    Args:
        request: HTTP запрос
    
    Returns:
        str: IP адрес клиента
    """
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


def create_slug(text: str, max_length: int = 50) -> str:
    """
    Создаёт slug из текста
    
    Args:
        text: Исходный текст
        max_length: Максимальная длина slug
    
    Returns:
        str: Slug
    """
    slug = slugify(text)
    if len(slug) > max_length:
        slug = slug[:max_length]
    return slug


def paginate_queryset(queryset, page: int, page_size: int = 20) -> Dict[str, Any]:
    """
    Пагинирует queryset
    
    Args:
        queryset: Django QuerySet
        page: Номер страницы (начиная с 1)
        page_size: Размер страницы
    
    Returns:
        Dict: Данные пагинации
    """
    from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
    
    paginator = Paginator(queryset, page_size)
    
    try:
        page_obj = paginator.page(page)
    except PageNotAnInteger:
        page_obj = paginator.page(1)
    except EmptyPage:
        page_obj = paginator.page(paginator.num_pages)
    
    return {
        'results': list(page_obj),
        'pagination': {
            'page': page_obj.number,
            'pages': paginator.num_pages,
            'per_page': page_size,
            'total': paginator.count,
            'has_next': page_obj.has_next(),
            'has_previous': page_obj.has_previous(),
            'next_page': page_obj.next_page_number() if page_obj.has_next() else None,
            'previous_page': page_obj.previous_page_number() if page_obj.has_previous() else None,
        }
    }


def format_file_size(size_bytes: int) -> str:
    """
    Форматирует размер файла в человекочитаемый вид
    
    Args:
        size_bytes: Размер в байтах
    
    Returns:
        str: Отформатированный размер
    """
    if size_bytes == 0:
        return "0 Б"
    
    size_names = ["Б", "КБ", "МБ", "ГБ", "ТБ"]
    i = 0
    
    while size_bytes >= 1024 and i < len(size_names) - 1:
        size_bytes /= 1024.0
        i += 1
    
    return f"{size_bytes:.1f} {size_names[i]}"


class FileUploadHandler:
    """
    Класс для обработки загружаемых файлов
    """
    
    ALLOWED_IMAGE_TYPES = [
        'image/jpeg',
        'image/png',
        'image/gif',
    ]
    
    ALLOWED_DOCUMENT_TYPES = [
        'application/pdf',
        'application/msword',
        'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
    ]
    
    MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB
    
    @classmethod
    def validate_image(cls, file: UploadedFile) -> Dict[str, Any]:
        """
        Валидирует изображение
        """
        return cls._validate_file(file, cls.ALLOWED_IMAGE_TYPES, 'изображение')
    
    @classmethod
    def validate_document(cls, file: UploadedFile) -> Dict[str, Any]:
        """
        Валидирует документ
        """
        return cls._validate_file(file, cls.ALLOWED_DOCUMENT_TYPES, 'документ')
    
    @classmethod
    def _validate_file(cls, file: UploadedFile, allowed_types: List[str], file_type_name: str) -> Dict[str, Any]:
        """
        Базовая валидация файла
        """
        errors = []
        
        # Проверка размера
        if file.size > cls.MAX_FILE_SIZE:
            errors.append(f"Размер файла превышает {format_file_size(cls.MAX_FILE_SIZE)}")
        
        # Проверка типа
        if not validate_file_type(file, allowed_types):
            errors.append(f"Недопустимый тип файла. Разрешены только {file_type_name}")
        
        return {
            'valid': len(errors) == 0,
            'errors': errors,
            'file_info': {
                'name': file.name,
                'size': file.size,
                'content_type': file.content_type,
                'formatted_size': format_file_size(file.size),
            }
        }
