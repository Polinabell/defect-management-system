"""
Middleware для приложения
"""

import json
import time
import logging
from typing import Any

from django.http import HttpRequest, HttpResponse, JsonResponse
from django.utils.deprecation import MiddlewareMixin
from django.conf import settings
from django.core.cache import cache
from django.utils import timezone


logger = logging.getLogger(__name__)


class RequestLoggingMiddleware(MiddlewareMixin):
    """
    Middleware для логирования API запросов
    """

    def process_request(self, request: HttpRequest) -> None:
        """Обработка входящего запроса"""
        request.start_time = time.time()

        # Логируем только API запросы
        if request.path.startswith('/api/'):
            logger.info(
                f"API Request: {request.method} {request.path} "
                f"from {self._get_client_ip(request)}"
            )

    def process_response(self, request: HttpRequest, response: HttpResponse) -> HttpResponse:
        """Обработка ответа"""
        if hasattr(request, 'start_time') and request.path.startswith('/api/'):
            duration = time.time() - request.start_time

            logger.info(
                f"API Response: {request.method} {request.path} "
                f"-> {response.status_code} in {duration:.3f}s"
            )

            # Добавляем заголовок с временем ответа
            response['X-Response-Time'] = f"{duration:.3f}s"

        return response

    def _get_client_ip(self, request: HttpRequest) -> str:
        """Получение IP адреса клиента"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip


class RateLimitMiddleware(MiddlewareMixin):
    """
    Middleware для ограничения частоты запросов
    """

    def __init__(self, get_response):
        super().__init__(get_response)
        self.rate_limit = getattr(settings, 'API_RATE_LIMIT', {
            'requests': 100,  # количество запросов
            'window': 3600,   # окно времени в секундах (1 час)
        })

    def process_request(self, request: HttpRequest) -> HttpResponse | None:
        """Проверка лимита запросов"""
        if not request.path.startswith('/api/'):
            return None

        client_ip = self._get_client_ip(request)
        cache_key = f"rate_limit:{client_ip}"

        # Получаем текущее количество запросов
        current_requests = cache.get(cache_key, 0)

        if current_requests >= self.rate_limit['requests']:
            return JsonResponse(
                {
                    'error': 'Rate limit exceeded',
                    'detail': f"Too many requests. Limit: {self.rate_limit['requests']} per {self.rate_limit['window']} seconds"
                },
                status=429
            )

        # Увеличиваем счётчик
        cache.set(cache_key, current_requests + 1, self.rate_limit['window'])

        return None

    def _get_client_ip(self, request: HttpRequest) -> str:
        """Получение IP адреса клиента"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0].strip()
        else:
            ip = request.META.get('REMOTE_ADDR', '127.0.0.1')
        return ip


class SecurityHeadersMiddleware(MiddlewareMixin):
    """
    Middleware для добавления заголовков безопасности
    """

    def process_response(self, request: HttpRequest, response: HttpResponse) -> HttpResponse:
        """Добавление заголовков безопасности"""

        # Защита от XSS
        response['X-XSS-Protection'] = '1; mode=block'

        # Защита от MIME-type sniffing
        response['X-Content-Type-Options'] = 'nosniff'

        # Защита от clickjacking
        response['X-Frame-Options'] = 'DENY'

        # Строгий контроль транспорта (только для HTTPS)
        if request.is_secure():
            response['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'

        # Политика контента (Content Security Policy)
        if not settings.DEBUG:
            response['Content-Security-Policy'] = (
                "default-src 'self'; "
                "script-src 'self' 'unsafe-inline'; "
                "style-src 'self' 'unsafe-inline' fonts.googleapis.com; "
                "font-src 'self' fonts.gstatic.com; "
                "img-src 'self' data: blob:; "
                "connect-src 'self';"
            )

        return response


class CacheControlMiddleware(MiddlewareMixin):
    """
    Middleware для управления кэшированием
    """

    def process_response(self, request: HttpRequest, response: HttpResponse) -> HttpResponse:
        """Установка заголовков кэширования"""

        # API запросы - не кэшируем по умолчанию
        if request.path.startswith('/api/'):
            response['Cache-Control'] = 'no-cache, no-store, must-revalidate'
            response['Pragma'] = 'no-cache'
            response['Expires'] = '0'

        # Статические файлы - кэшируем на длительное время
        elif request.path.startswith('/static/') or request.path.startswith('/media/'):
            response['Cache-Control'] = 'public, max-age=31536000'  # 1 год

        return response


class JSONResponseMiddleware(MiddlewareMixin):
    """
    Middleware для обработки JSON ответов и ошибок
    """

    def process_exception(self, request: HttpRequest, exception: Exception) -> HttpResponse | None:
        """Обработка исключений для API запросов"""
        if not request.path.startswith('/api/'):
            return None

        logger.exception(f"API Exception: {request.method} {request.path}")

        if settings.DEBUG:
            error_detail = str(exception)
        else:
            error_detail = "Internal server error"

        return JsonResponse(
            {
                'error': 'Internal Server Error',
                'detail': error_detail,
                'timestamp': timezone.now().isoformat(),
            },
            status=500
        )


class HealthCheckMiddleware(MiddlewareMixin):
    """
    Middleware для проверки состояния приложения
    """

    def process_request(self, request: HttpRequest) -> HttpResponse | None:
        """Обработка запросов проверки здоровья"""
        if request.path == '/health/' or request.path == '/api/health/':
            return self._health_check_response()

        return None

    def _health_check_response(self) -> JsonResponse:
        """Генерация ответа проверки здоровья"""
        from django.db import connection
        from django.core.cache import cache

        status = 'healthy'
        checks = {}

        # Проверка базы данных
        try:
            with connection.cursor() as cursor:
                cursor.execute("SELECT 1")
                checks['database'] = 'ok'
        except Exception as e:
            checks['database'] = f'error: {str(e)}'
            status = 'unhealthy'

        # Проверка Redis/кэша
        try:
            cache.set('health_check', 'ok', 10)
            cache_value = cache.get('health_check')
            if cache_value == 'ok':
                checks['cache'] = 'ok'
            else:
                checks['cache'] = 'error: cache not working'
                status = 'unhealthy'
        except Exception as e:
            checks['cache'] = f'error: {str(e)}'
            status = 'unhealthy'

        response_data = {
            'status': status,
            'timestamp': timezone.now().isoformat(),
            'checks': checks,
            'version': getattr(settings, 'VERSION', '1.0.0'),
        }

        status_code = 200 if status == 'healthy' else 503
        return JsonResponse(response_data, status=status_code)


class RequestIDMiddleware(MiddlewareMixin):
    """
    Middleware для добавления уникального ID к каждому запросу
    """

    def process_request(self, request: HttpRequest) -> None:
        """Добавление ID запроса"""
        import uuid
        request.request_id = str(uuid.uuid4())

    def process_response(self, request: HttpRequest, response: HttpResponse) -> HttpResponse:
        """Добавление ID запроса в заголовки ответа"""
        if hasattr(request, 'request_id'):
            response['X-Request-ID'] = request.request_id

        return response