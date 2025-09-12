"""
Middleware для сбора метрик Prometheus
"""

import time
from django.utils.deprecation import MiddlewareMixin
from django.http import HttpResponse
from prometheus_client import Counter, Histogram, Gauge
from .utils import get_client_ip

# Метрики
REQUEST_COUNT = Counter(
    'django_http_requests_total',
    'Total HTTP requests',
    ['method', 'endpoint', 'status']
)

REQUEST_DURATION = Histogram(
    'django_http_request_duration_seconds',
    'HTTP request duration in seconds',
    ['method', 'endpoint']
)

ACTIVE_USERS = Gauge(
    'active_users',
    'Number of active users'
)

DEFECTS_CREATED = Counter(
    'defects_created_total',
    'Total defects created'
)

DEFECTS_RESOLVED = Counter(
    'defects_resolved_total',
    'Total defects resolved'
)

API_ERRORS = Counter(
    'django_api_errors_total',
    'Total API errors',
    ['error_type', 'endpoint']
)


class PrometheusMiddleware(MiddlewareMixin):
    """
    Middleware для сбора метрик Prometheus
    """
    
    def process_request(self, request):
        """Начало обработки запроса"""
        request._start_time = time.time()
        return None
    
    def process_response(self, request, response):
        """Обработка ответа и сбор метрик"""
        if hasattr(request, '_start_time'):
            duration = time.time() - request._start_time
            
            # Определяем endpoint
            endpoint = self._get_endpoint(request)
            
            # Собираем метрики
            REQUEST_COUNT.labels(
                method=request.method,
                endpoint=endpoint,
                status=response.status_code
            ).inc()
            
            REQUEST_DURATION.labels(
                method=request.method,
                endpoint=endpoint
            ).observe(duration)
        
        return response
    
    def process_exception(self, request, exception):
        """Обработка исключений"""
        endpoint = self._get_endpoint(request)
        API_ERRORS.labels(
            error_type=type(exception).__name__,
            endpoint=endpoint
        ).inc()
        return None
    
    def _get_endpoint(self, request):
        """Получение endpoint из URL"""
        path = request.path
        
        # Упрощаем путь для группировки
        if path.startswith('/api/v1/'):
            # Убираем ID из URL для группировки
            parts = path.split('/')
            if len(parts) > 4 and parts[4].isdigit():
                parts[4] = '{id}'
            return '/'.join(parts[:5])  # Ограничиваем глубину
        
        return path


class ActiveUsersMiddleware(MiddlewareMixin):
    """
    Middleware для отслеживания активных пользователей
    """
    
    def process_request(self, request):
        """Обновление счетчика активных пользователей"""
        if hasattr(request, 'user') and request.user.is_authenticated:
            # Здесь можно добавить логику для более точного подсчета
            # активных пользователей (например, по сессиям)
            pass
        return None


def increment_defect_created():
    """Увеличение счетчика созданных дефектов"""
    DEFECTS_CREATED.inc()


def increment_defect_resolved():
    """Увеличение счетчика решенных дефектов"""
    DEFECTS_RESOLVED.inc()


def update_active_users(count):
    """Обновление количества активных пользователей"""
    ACTIVE_USERS.set(count)
