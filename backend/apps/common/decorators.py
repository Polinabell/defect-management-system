"""
Декораторы для безопасности
"""

import functools
import logging
from django.http import JsonResponse
from django.core.cache import cache
from django.conf import settings
from .utils import get_client_ip, log_security_event

logger = logging.getLogger(__name__)


def rate_limit(max_requests=100, window=60):
    """
    Декоратор для ограничения частоты запросов
    """
    def decorator(view_func):
        @functools.wraps(view_func)
        def wrapper(request, *args, **kwargs):
            ip = get_client_ip(request)
            cache_key = f"rate_limit_{ip}"
            
            # Получаем текущее количество запросов
            current_requests = cache.get(cache_key, 0)
            
            if current_requests >= max_requests:
                log_security_event(
                    'rate_limit_exceeded',
                    {'ip': ip, 'requests': current_requests},
                    request
                )
                return JsonResponse(
                    {'error': 'Слишком много запросов'}, 
                    status=429
                )
            
            # Увеличиваем счетчик
            cache.set(cache_key, current_requests + 1, window)
            
            return view_func(request, *args, **kwargs)
        return wrapper
    return decorator


def require_https(view_func):
    """
    Декоратор для принуждения HTTPS
    """
    @functools.wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not settings.DEBUG and not request.is_secure():
            return JsonResponse(
                {'error': 'HTTPS required'}, 
                status=400
            )
        return view_func(request, *args, **kwargs)
    return wrapper


def log_user_activity(action_name):
    """
    Декоратор для логирования активности пользователя
    """
    def decorator(view_func):
        @functools.wraps(view_func)
        def wrapper(request, *args, **kwargs):
            # Логируем активность
            if hasattr(request, 'user') and request.user.is_authenticated:
                from .services import AuditService
                AuditService.log_user_action(
                    user=request.user,
                    action=action_name,
                    ip_address=get_client_ip(request)
                )
            
            return view_func(request, *args, **kwargs)
        return wrapper
    return decorator


def check_permissions(required_permissions):
    """
    Декоратор для проверки прав доступа
    """
    def decorator(view_func):
        @functools.wraps(view_func)
        def wrapper(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return JsonResponse(
                    {'error': 'Требуется аутентификация'}, 
                    status=401
                )
            
            # Проверяем права
            for permission in required_permissions:
                if not request.user.has_perm(permission):
                    log_security_event(
                        'permission_denied',
                        {'user': request.user.id, 'permission': permission},
                        request
                    )
                    return JsonResponse(
                        {'error': 'Недостаточно прав'}, 
                        status=403
                    )
            
            return view_func(request, *args, **kwargs)
        return wrapper
    return decorator


def validate_input(required_fields=None, max_length=None):
    """
    Декоратор для валидации входных данных
    """
    def decorator(view_func):
        @functools.wraps(view_func)
        def wrapper(request, *args, **kwargs):
            # Проверяем обязательные поля
            if required_fields:
                for field in required_fields:
                    if field not in request.data:
                        return JsonResponse(
                            {'error': f'Отсутствует обязательное поле: {field}'}, 
                            status=400
                        )
            
            # Проверяем максимальную длину
            if max_length:
                for key, value in request.data.items():
                    if isinstance(value, str) and len(value) > max_length:
                        return JsonResponse(
                            {'error': f'Поле {key} слишком длинное'}, 
                            status=400
                        )
            
            return view_func(request, *args, **kwargs)
        return wrapper
    return decorator


def prevent_brute_force(max_attempts=5, lockout_duration=300):
    """
    Декоратор для предотвращения брутфорс атак
    """
    def decorator(view_func):
        @functools.wraps(view_func)
        def wrapper(request, *args, **kwargs):
            ip = get_client_ip(request)
            cache_key = f"brute_force_{ip}"
            
            # Проверяем количество попыток
            attempts = cache.get(cache_key, 0)
            
            if attempts >= max_attempts:
                log_security_event(
                    'brute_force_detected',
                    {'ip': ip, 'attempts': attempts},
                    request
                )
                return JsonResponse(
                    {'error': 'Слишком много неудачных попыток'}, 
                    status=429
                )
            
            # Выполняем функцию
            response = view_func(request, *args, **kwargs)
            
            # Если неудачная попытка, увеличиваем счетчик
            if response.status_code >= 400:
                cache.set(cache_key, attempts + 1, lockout_duration)
            else:
                # Успешная попытка, сбрасываем счетчик
                cache.delete(cache_key)
            
            return response
        return wrapper
    return decorator
