"""
Кастомные middleware для безопасности и логирования
"""

import logging
import time
from datetime import datetime
from django.utils.deprecation import MiddlewareMixin
from django.http import HttpResponseForbidden, JsonResponse
from django.core.cache import cache
from django.conf import settings
from django.contrib.auth.models import AnonymousUser
from .utils import get_client_ip

logger = logging.getLogger(__name__)
security_logger = logging.getLogger('django.security')


class SecurityHeadersMiddleware(MiddlewareMixin):
    """
    Middleware для добавления заголовков безопасности
    """
    
    def process_response(self, request, response):
        """Добавляем заголовки безопасности"""
        
        # Защита от clickjacking
        response['X-Frame-Options'] = 'DENY'
        
        # Защита от MIME type sniffing
        response['X-Content-Type-Options'] = 'nosniff'
        
        # XSS защита
        response['X-XSS-Protection'] = '1; mode=block'
        
        # Referrer Policy
        response['Referrer-Policy'] = 'strict-origin-when-cross-origin'
        
        # Content Security Policy
        csp_directives = [
            "default-src 'self'",
            "script-src 'self' 'unsafe-inline' 'unsafe-eval'",
            "style-src 'self' 'unsafe-inline' fonts.googleapis.com",
            "font-src 'self' fonts.gstatic.com",
            "img-src 'self' data: blob:",
            "connect-src 'self'",
            "frame-ancestors 'none'",
            "base-uri 'self'",
            "form-action 'self'",
        ]
        response['Content-Security-Policy'] = '; '.join(csp_directives)
        
        # Permissions Policy
        permissions_directives = [
            "camera=()",
            "microphone=()",
            "geolocation=()",
            "payment=()",
            "usb=()",
        ]
        response['Permissions-Policy'] = ', '.join(permissions_directives)
        
        # HSTS (если HTTPS)
        if request.is_secure():
            response['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains; preload'
        
        return response


class RateLimitMiddleware(MiddlewareMixin):
    """
    Middleware для ограничения частоты запросов (Rate Limiting)
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
        # Настройки лимитов
        self.limits = {
            'login': {'requests': 5, 'window': 300},  # 5 попыток в 5 минут
            'register': {'requests': 3, 'window': 600},  # 3 попытки в 10 минут
            'api': {'requests': 1000, 'window': 3600},  # 1000 запросов в час
            'upload': {'requests': 50, 'window': 3600},  # 50 загрузок в час
        }
    
    def __call__(self, request):
        # Проверяем rate limit
        if not self._check_rate_limit(request):
            return JsonResponse({
                'error': 'Превышен лимит запросов',
                'detail': 'Слишком много запросов. Попробуйте позже.'
            }, status=429)
        
        response = self.get_response(request)
        return response
    
    def _check_rate_limit(self, request):
        """Проверка лимита запросов"""
        client_ip = get_client_ip(request)
        path = request.path
        
        # Определяем тип запроса
        limit_type = self._get_limit_type(path, request.method)
        if not limit_type:
            return True
        
        # Создаём ключ кэша
        cache_key = f"rate_limit:{limit_type}:{client_ip}"
        
        # Получаем текущее количество запросов
        current_requests = cache.get(cache_key, 0)
        limit_config = self.limits[limit_type]
        
        if current_requests >= limit_config['requests']:
            # Логируем превышение лимита
            security_logger.warning(
                f"Rate limit exceeded for {client_ip} on {path}",
                extra={
                    'ip': client_ip,
                    'path': path,
                    'requests': current_requests,
                    'limit': limit_config['requests'],
                    'window': limit_config['window']
                }
            )
            return False
        
        # Увеличиваем счётчик
        cache.set(cache_key, current_requests + 1, limit_config['window'])
        return True
    
    def _get_limit_type(self, path, method):
        """Определение типа лимита по пути"""
        if '/api/v1/auth/login/' in path:
            return 'login'
        elif '/api/v1/auth/register/' in path:
            return 'register'
        elif path.startswith('/api/v1/') and method == 'POST' and 'files' in path:
            return 'upload'
        elif path.startswith('/api/v1/'):
            return 'api'
        return None


class AuditLoggingMiddleware(MiddlewareMixin):
    """
    Middleware для аудита действий пользователей
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
        self.audit_logger = logging.getLogger('audit')
    
    def __call__(self, request):
        start_time = time.time()
        
        # Получаем информацию о запросе
        request_info = self._get_request_info(request)
        
        response = self.get_response(request)
        
        # Вычисляем время выполнения
        execution_time = time.time() - start_time
        
        # Логируем только важные действия
        if self._should_audit(request, response):
            self._log_action(request, response, request_info, execution_time)
        
        return response
    
    def _get_request_info(self, request):
        """Получение информации о запросе"""
        return {
            'ip': get_client_ip(request),
            'user_agent': request.META.get('HTTP_USER_AGENT', ''),
            'method': request.method,
            'path': request.path,
            'user_id': request.user.id if hasattr(request, 'user') and not isinstance(request.user, AnonymousUser) else None,
            'timestamp': datetime.now().isoformat(),
        }
    
    def _should_audit(self, request, response):
        """Определение необходимости аудита"""
        # Аудируем важные действия
        audit_paths = [
            '/api/v1/auth/',
            '/api/v1/defects/',
            '/api/v1/projects/',
            '/api/v1/reports/',
            '/admin/',
        ]
        
        # Аудируем изменяющие запросы
        if request.method in ['POST', 'PUT', 'PATCH', 'DELETE']:
            return any(request.path.startswith(path) for path in audit_paths)
        
        # Аудируем ошибки безопасности
        if response.status_code in [401, 403, 429]:
            return True
        
        return False
    
    def _log_action(self, request, response, request_info, execution_time):
        """Логирование действия"""
        log_data = {
            **request_info,
            'status_code': response.status_code,
            'execution_time': round(execution_time, 3),
            'content_length': len(response.content) if hasattr(response, 'content') else 0,
        }
        
        # Добавляем дополнительную информацию для POST запросов
        if request.method == 'POST' and hasattr(request, 'POST'):
            # Не логируем пароли и другие чувствительные данные
            sensitive_fields = ['password', 'token', 'secret']
            post_data = {}
            for key, value in request.POST.items():
                if not any(field in key.lower() for field in sensitive_fields):
                    post_data[key] = str(value)[:100]  # Ограничиваем длину
            log_data['post_data'] = post_data
        
        self.audit_logger.info(
            f"User action: {request.method} {request.path}",
            extra=log_data
        )


class IPWhitelistMiddleware(MiddlewareMixin):
    """
    Middleware для ограничения доступа по IP адресам
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
        # Получаем список разрешённых IP из настроек
        self.whitelist = getattr(settings, 'IP_WHITELIST', [])
        self.admin_whitelist = getattr(settings, 'ADMIN_IP_WHITELIST', [])
        self.enabled = getattr(settings, 'IP_WHITELIST_ENABLED', False)
    
    def __call__(self, request):
        if self.enabled:
            client_ip = get_client_ip(request)
            
            # Проверяем доступ к админке
            if request.path.startswith('/admin/'):
                if self.admin_whitelist and client_ip not in self.admin_whitelist:
                    security_logger.warning(
                        f"Admin access denied for IP {client_ip}",
                        extra={'ip': client_ip, 'path': request.path}
                    )
                    return HttpResponseForbidden('Доступ запрещён')
            
            # Проверяем общий доступ
            elif self.whitelist and client_ip not in self.whitelist:
                security_logger.warning(
                    f"Access denied for IP {client_ip}",
                    extra={'ip': client_ip, 'path': request.path}
                )
                return HttpResponseForbidden('Доступ запрещён')
        
        response = self.get_response(request)
        return response


class SessionSecurityMiddleware(MiddlewareMixin):
    """
    Middleware для дополнительной безопасности сессий
    """
    
    def process_request(self, request):
        """Проверка безопасности сессии"""
        if not hasattr(request, 'user') or not request.user.is_authenticated:
            return None
        
        # Проверяем IP адрес сессии
        session_ip = request.session.get('ip_address')
        current_ip = get_client_ip(request)
        
        if session_ip and session_ip != current_ip:
            # IP изменился - принудительный выход
            security_logger.warning(
                f"Session IP mismatch for user {request.user.id}: {session_ip} -> {current_ip}",
                extra={
                    'user_id': request.user.id,
                    'session_ip': session_ip,
                    'current_ip': current_ip
                }
            )
            request.session.flush()
            return JsonResponse({
                'error': 'Сессия недействительна',
                'detail': 'Необходимо войти в систему заново'
            }, status=401)
        
        # Сохраняем IP в сессии
        if not session_ip:
            request.session['ip_address'] = current_ip
        
        # Обновляем время последней активности
        request.session['last_activity'] = time.time()
        
        return None


class SQLInjectionProtectionMiddleware(MiddlewareMixin):
    """
    Middleware для базовой защиты от SQL инъекций
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
        # Список подозрительных паттернов
        self.sql_patterns = [
            'union', 'select', 'insert', 'update', 'delete', 'drop',
            'create', 'alter', 'exec', 'execute', 'sp_', 'xp_',
            'script', 'javascript', 'vbscript', 'onload', 'onerror'
        ]
    
    def __call__(self, request):
        # Проверяем параметры запроса
        if self._check_for_sql_injection(request):
            security_logger.error(
                f"Potential SQL injection attempt from {get_client_ip(request)}",
                extra={
                    'ip': get_client_ip(request),
                    'path': request.path,
                    'method': request.method,
                    'query_string': request.META.get('QUERY_STRING', ''),
                }
            )
            return JsonResponse({
                'error': 'Недопустимый запрос',
                'detail': 'Запрос содержит подозрительные данные'
            }, status=400)
        
        response = self.get_response(request)
        return response
    
    def _check_for_sql_injection(self, request):
        """Проверка на SQL инъекции"""
        # Проверяем GET параметры
        for key, value in request.GET.items():
            if self._contains_sql_pattern(value.lower()):
                return True
        
        # Проверяем POST данные
        if hasattr(request, 'POST'):
            for key, value in request.POST.items():
                if self._contains_sql_pattern(str(value).lower()):
                    return True
        
        return False
    
    def _contains_sql_pattern(self, text):
        """Проверка наличия SQL паттернов"""
        return any(pattern in text for pattern in self.sql_patterns)
