"""
Валидаторы для безопасности
"""

import re
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _


def validate_safe_string(value):
    """
    Валидатор для безопасных строк
    """
    # Проверяем на опасные символы
    dangerous_chars = ['<', '>', '"', "'", '&', ';', '(', ')', '|', '`', '$']
    
    for char in dangerous_chars:
        if char in value:
            raise ValidationError(
                _('Строка содержит недопустимые символы: %(char)s'),
                params={'char': char}
            )


def validate_file_extension(value):
    """
    Валидатор для расширений файлов
    """
    allowed_extensions = [
        'jpg', 'jpeg', 'png', 'gif', 'bmp', 'webp', 'svg',
        'pdf', 'doc', 'docx', 'xls', 'xlsx', 'ppt', 'pptx',
        'txt', 'rtf', 'odt', 'ods', 'odp', 'zip', 'rar'
    ]
    
    import os
    ext = os.path.splitext(value.name)[1][1:].lower()
    
    if ext not in allowed_extensions:
        raise ValidationError(
            _('Недопустимое расширение файла: %(ext)s'),
            params={'ext': ext}
        )


def validate_file_size(value):
    """
    Валидатор для размера файла
    """
    max_size = 10 * 1024 * 1024  # 10MB
    
    if value.size > max_size:
        raise ValidationError(
            _('Размер файла не должен превышать 10MB')
        )


def validate_password_strength(value):
    """
    Валидатор для силы пароля
    """
    if len(value) < 8:
        raise ValidationError(
            _('Пароль должен содержать минимум 8 символов')
        )
    
    if not re.search(r'[A-Z]', value):
        raise ValidationError(
            _('Пароль должен содержать хотя бы одну заглавную букву')
        )
    
    if not re.search(r'[a-z]', value):
        raise ValidationError(
            _('Пароль должен содержать хотя бы одну строчную букву')
        )
    
    if not re.search(r'\d', value):
        raise ValidationError(
            _('Пароль должен содержать хотя бы одну цифру')
        )
    
    if not re.search(r'[!@#$%^&*(),.?":{}|<>]', value):
        raise ValidationError(
            _('Пароль должен содержать хотя бы один специальный символ')
        )


def validate_phone_number(value):
    """
    Валидатор для номера телефона
    """
    # Российский формат телефона
    phone_pattern = r'^(\+7|7|8)?[\s\-]?\(?[489][0-9]{2}\)?[\s\-]?[0-9]{3}[\s\-]?[0-9]{2}[\s\-]?[0-9]{2}$'
    
    if not re.match(phone_pattern, value):
        raise ValidationError(
            _('Введите корректный номер телефона')
        )


def validate_email_domain(value):
    """
    Валидатор для домена email
    """
    # Список запрещенных доменов
    forbidden_domains = [
        'tempmail.com', '10minutemail.com', 'guerrillamail.com',
        'mailinator.com', 'yopmail.com', 'throwaway.email'
    ]
    
    domain = value.split('@')[1].lower()
    
    if domain in forbidden_domains:
        raise ValidationError(
            _('Использование временных email адресов запрещено')
        )


def validate_no_sql_injection(value):
    """
    Валидатор против SQL инъекций
    """
    sql_patterns = [
        r"(\b(SELECT|INSERT|UPDATE|DELETE|DROP|CREATE|ALTER|EXEC|UNION)\b)",
        r"(\b(OR|AND)\s+\d+\s*=\s*\d+)",
        r"(--|\#|\/\/|\/\*)",
        r"(\bUNION\b.*\bSELECT\b)",
    ]
    
    for pattern in sql_patterns:
        if re.search(pattern, value.upper()):
            raise ValidationError(
                _('Обнаружена попытка SQL инъекции')
            )


def validate_no_xss(value):
    """
    Валидатор против XSS атак
    """
    xss_patterns = [
        r"<script\b[^<]*(?:(?!<\/script>)<[^<]*)*<\/script>",
        r"<iframe\b[^>]*>.*?</iframe>",
        r"javascript:",
        r"vbscript:",
        r"onload\s*=",
        r"onerror\s*=",
        r"onclick\s*=",
    ]
    
    for pattern in xss_patterns:
        if re.search(pattern, value, re.IGNORECASE):
            raise ValidationError(
                _('Обнаружена попытка XSS атаки')
            )
