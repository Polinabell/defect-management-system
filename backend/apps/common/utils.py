"""
Утилиты для общих функций
"""

import ipaddress
from django.http import HttpRequest
from django.conf import settings
from django.utils import timezone


def get_client_ip(request: HttpRequest) -> str:
    """
    Получает IP адрес клиента из запроса
    """
    # Проверяем заголовки прокси
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        # Берем первый IP из списка
        ip = x_forwarded_for.split(',')[0].strip()
    else:
        ip = request.META.get('REMOTE_ADDR')
    
    # Проверяем, что IP валидный
    try:
        ipaddress.ip_address(ip)
        return ip
    except ValueError:
        return '127.0.0.1'


def is_internal_ip(ip: str) -> bool:
    """
    Проверяет, является ли IP внутренним
    """
    try:
        ip_obj = ipaddress.ip_address(ip)
        return ip_obj.is_private or ip_obj.is_loopback
    except ValueError:
        return False


def get_user_agent_info(user_agent: str) -> dict:
    """
    Парсит информацию о браузере из User-Agent
    """
    user_agent_lower = user_agent.lower()
    
    # Определяем браузер
    if 'chrome' in user_agent_lower and 'edge' not in user_agent_lower:
        browser = 'Chrome'
    elif 'firefox' in user_agent_lower:
        browser = 'Firefox'
    elif 'safari' in user_agent_lower and 'chrome' not in user_agent_lower:
        browser = 'Safari'
    elif 'edge' in user_agent_lower:
        browser = 'Edge'
    elif 'opera' in user_agent_lower:
        browser = 'Opera'
    else:
        browser = 'Неизвестный'
    
    # Определяем операционную систему
    if 'windows' in user_agent_lower:
        os = 'Windows'
    elif 'mac' in user_agent_lower:
        os = 'macOS'
    elif 'linux' in user_agent_lower:
        os = 'Linux'
    elif 'android' in user_agent_lower:
        os = 'Android'
    elif 'iphone' in user_agent_lower or 'ipad' in user_agent_lower:
        os = 'iOS'
    else:
        os = 'Неизвестная'
    
    # Определяем устройство
    if 'mobile' in user_agent_lower or 'android' in user_agent_lower or 'iphone' in user_agent_lower:
        device = 'Мобильное'
    elif 'tablet' in user_agent_lower or 'ipad' in user_agent_lower:
        device = 'Планшет'
    else:
        device = 'Десктоп'
    
    return {
        'browser': browser,
        'os': os,
        'device': device,
        'user_agent': user_agent
    }


def format_file_size(size_bytes: int) -> str:
    """
    Форматирует размер файла в читаемый вид
    """
    if size_bytes == 0:
        return "0 Bytes"
    
    size_names = ["Bytes", "KB", "MB", "GB", "TB"]
    i = 0
    while size_bytes >= 1024 and i < len(size_names) - 1:
        size_bytes /= 1024.0
        i += 1
    
    return f"{size_bytes:.2f} {size_names[i]}"


def get_file_extension(filename: str) -> str:
    """
    Получает расширение файла
    """
    if '.' in filename:
        return filename.rsplit('.', 1)[1].lower()
    return ''


def is_image_file(filename: str) -> bool:
    """
    Проверяет, является ли файл изображением
    """
    image_extensions = {'jpg', 'jpeg', 'png', 'gif', 'bmp', 'webp', 'svg', 'tiff'}
    return get_file_extension(filename) in image_extensions


def is_document_file(filename: str) -> bool:
    """
    Проверяет, является ли файл документом
    """
    document_extensions = {
        'pdf', 'doc', 'docx', 'xls', 'xlsx', 'ppt', 'pptx',
        'txt', 'rtf', 'odt', 'ods', 'odp'
    }
    return get_file_extension(filename) in document_extensions


def sanitize_filename(filename: str) -> str:
    """
    Очищает имя файла от небезопасных символов
    """
    import re
    # Удаляем небезопасные символы
    filename = re.sub(r'[<>:"/\\|?*]', '_', filename)
    # Удаляем множественные подчеркивания
    filename = re.sub(r'_+', '_', filename)
    # Удаляем подчеркивания в начале и конце
    filename = filename.strip('_')
    return filename


def generate_unique_filename(original_filename: str, prefix: str = '') -> str:
    """
    Генерирует уникальное имя файла
    """
    import uuid
    import os
    
    # Очищаем имя файла
    safe_filename = sanitize_filename(original_filename)
    
    # Получаем расширение
    name, ext = os.path.splitext(safe_filename)
    
    # Генерируем уникальный идентификатор
    unique_id = str(uuid.uuid4())[:8]
    
    # Формируем новое имя
    if prefix:
        new_name = f"{prefix}_{unique_id}_{name}{ext}"
    else:
        new_name = f"{unique_id}_{name}{ext}"
    
    return new_name


def get_mime_type(filename: str) -> str:
    """
    Определяет MIME тип файла по расширению
    """
    import mimetypes
    
    mime_type, _ = mimetypes.guess_type(filename)
    return mime_type or 'application/octet-stream'


def validate_file_size(file, max_size_mb: int = 10) -> bool:
    """
    Проверяет размер файла
    """
    max_size_bytes = max_size_mb * 1024 * 1024
    return file.size <= max_size_bytes


def validate_file_type(filename: str, allowed_extensions: list) -> bool:
    """
    Проверяет тип файла по расширению
    """
    file_extension = get_file_extension(filename)
    return file_extension.lower() in [ext.lower() for ext in allowed_extensions]


def get_setting(key: str, default=None):
    """
    Получает настройку из Django settings
    """
    return getattr(settings, key, default)


def log_security_event(event_type: str, details: dict, request: HttpRequest = None):
    """
    Логирует событие безопасности
    """
    import logging
    
    security_logger = logging.getLogger('security')
    
    log_data = {
        'event_type': event_type,
        'details': details,
        'timestamp': timezone.now().isoformat(),
    }
    
    if request:
        log_data.update({
            'ip_address': get_client_ip(request),
            'user_agent': request.META.get('HTTP_USER_AGENT', ''),
            'user_id': getattr(request.user, 'id', None) if hasattr(request, 'user') and request.user.is_authenticated else None,
        })
    
    security_logger.warning(f"Security event: {log_data}")


def is_ajax_request(request: HttpRequest) -> bool:
    """
    Проверяет, является ли запрос AJAX
    """
    return request.META.get('HTTP_X_REQUESTED_WITH') == 'XMLHttpRequest'


def get_pagination_info(page_obj):
    """
    Получает информацию о пагинации
    """
    return {
        'current_page': page_obj.number,
        'total_pages': page_obj.paginator.num_pages,
        'total_items': page_obj.paginator.count,
        'has_previous': page_obj.has_previous(),
        'has_next': page_obj.has_next(),
        'previous_page': page_obj.previous_page_number() if page_obj.has_previous() else None,
        'next_page': page_obj.next_page_number() if page_obj.has_next() else None,
    }