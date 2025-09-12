"""
Middleware для дополнительной безопасности
"""

import logging
from django.utils.deprecation import MiddlewareMixin
from django.http import HttpResponseForbidden, JsonResponse
from django.conf import settings
from .utils import get_client_ip, is_internal_ip, log_security_event

logger = logging.getLogger(__name__)


class SecurityHeadersMiddleware(MiddlewareMixin):
    """
    Middleware для добавления заголовков безопасности
    """
    
    def process_response(self, request, response):
        """Добавляет заголовки безопасности к ответу"""
        # Защита от XSS
        response['X-Content-Type-Options'] = 'nosniff'
        response['X-Frame-Options'] = 'DENY'
        response['X-XSS-Protection'] = '1; mode=block'
        
        # Строгая политика транспорта
        if not settings.DEBUG:
            response['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
        
        # Политика реферера
        response['Referrer-Policy'] = 'strict-origin-when-cross-origin'
        
        # Политика CSP (Content Security Policy)
        csp = (
            "default-src 'self'; "
            "script-src 'self' 'unsafe-inline' 'unsafe-eval'; "
            "style-src 'self' 'unsafe-inline'; "
            "img-src 'self' data: https:; "
            "font-src 'self' data:; "
            "connect-src 'self'; "
            "frame-ancestors 'none';"
        )
        response['Content-Security-Policy'] = csp
        
        return response


class RateLimitMiddleware(MiddlewareMixin):
    """
    Middleware для ограничения частоты запросов
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
        super().__init__(get_response)
        # Словарь для хранения запросов по IP
        self.request_counts = {}
        
    def process_request(self, request):
        """Проверяет лимит запросов"""
        ip = get_client_ip(request)
        
        import time
        current_time = time.time()
        window = 60  # Окно в 60 секунд
        max_requests = 100  # Максимум 100 запросов в минуту
        
        # Очищаем старые записи
        self.request_counts = {
            k: v for k, v in self.request_counts.items() 
            if current_time - v['last_reset'] < window
        }
        
        # Проверяем лимит для текущего IP
        if ip not in self.request_counts:
            self.request_counts[ip] = {'count': 1, 'last_reset': current_time}
        else:
            if current_time - self.request_counts[ip]['last_reset'] >= window:
                self.request_counts[ip] = {'count': 1, 'last_reset': current_time}
            else:
                self.request_counts[ip]['count'] += 1
                
                if self.request_counts[ip]['count'] > max_requests:
                    log_security_event(
                        'rate_limit_exceeded',
                        {'ip': ip, 'count': self.request_counts[ip]['count']},
                        request
                    )
                    return HttpResponseForbidden("Слишком много запросов")
        
        return None


class SQLInjectionProtectionMiddleware(MiddlewareMixin):
    """
    Middleware для защиты от SQL инъекций
    """
    
    # Опасные паттерны SQL инъекций
    SQL_INJECTION_PATTERNS = [
        r"(\b(SELECT|INSERT|UPDATE|DELETE|DROP|CREATE|ALTER|EXEC|UNION)\b)",
        r"(\b(OR|AND)\s+\d+\s*=\s*\d+)",
        r"(\b(OR|AND)\s+['\"]?\w+['\"]?\s*=\s*['\"]?\w+['\"]?)",
        r"(--|\#|\/\/|\/\*)",
        r"(\bUNION\b.*\bSELECT\b)",
        r"(\bEXEC\b|\bEXECUTE\b)",
        r"(\bSCRIPT\b)",
        r"(\bVBSCRIPT\b)",
        r"(\bJAVASCRIPT\b)",
    ]
    
    def process_request(self, request):
        """Проверяет запрос на SQL инъекции"""
        import re
        
        # Проверяем GET параметры
        for key, value in request.GET.items():
            if self._check_sql_injection(str(value)):
                log_security_event(
                    'sql_injection_attempt',
                    {'parameter': key, 'value': value, 'type': 'GET'},
                    request
                )
                return HttpResponseForbidden("Подозрительный запрос")
        
        # Проверяем POST параметры
        if request.method == 'POST':
            for key, value in request.POST.items():
                if self._check_sql_injection(str(value)):
                    log_security_event(
                        'sql_injection_attempt',
                        {'parameter': key, 'value': value, 'type': 'POST'},
                        request
                    )
                    return HttpResponseForbidden("Подозрительный запрос")
        
        return None
    
    def _check_sql_injection(self, value):
        """Проверяет значение на SQL инъекции"""
        import re
        
        for pattern in self.SQL_INJECTION_PATTERNS:
            if re.search(pattern, value.upper()):
                return True
        return False


class XSSProtectionMiddleware(MiddlewareMixin):
    """
    Middleware для защиты от XSS атак
    """
    
    # Опасные паттерны XSS
    XSS_PATTERNS = [
        r"<script\b[^<]*(?:(?!<\/script>)<[^<]*)*<\/script>",
        r"<iframe\b[^>]*>.*?</iframe>",
        r"javascript:",
        r"vbscript:",
        r"onload\s*=",
        r"onerror\s*=",
        r"onclick\s*=",
        r"onmouseover\s*=",
        r"<object\b[^>]*>.*?</object>",
        r"<embed\b[^>]*>",
        r"<form\b[^>]*>.*?</form>",
        r"<input\b[^>]*>",
        r"<link\b[^>]*>",
        r"<meta\b[^>]*>",
    ]
    
    def process_request(self, request):
        """Проверяет запрос на XSS атаки"""
        import re
        
        # Проверяем GET параметры
        for key, value in request.GET.items():
            if self._check_xss(str(value)):
                log_security_event(
                    'xss_attempt',
                    {'parameter': key, 'value': value, 'type': 'GET'},
                    request
                )
                return HttpResponseForbidden("Подозрительный запрос")
        
        # Проверяем POST параметры
        if request.method == 'POST':
            for key, value in request.POST.items():
                if self._check_xss(str(value)):
                    log_security_event(
                        'xss_attempt',
                        {'parameter': key, 'value': value, 'type': 'POST'},
                        request
                    )
                    return HttpResponseForbidden("Подозрительный запрос")
        
        return None
    
    def _check_xss(self, value):
        """Проверяет значение на XSS атаки"""
        import re
        
        for pattern in self.XSS_PATTERNS:
            if re.search(pattern, value, re.IGNORECASE):
                return True
        return False
