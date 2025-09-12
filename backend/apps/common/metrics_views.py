"""
Views для экспорта метрик Prometheus
"""

from django.http import HttpResponse
from prometheus_client import generate_latest, CONTENT_TYPE_LATEST
from django.views.decorators.cache import never_cache
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required


@never_cache
@require_http_methods(["GET"])
@staff_member_required
def metrics_view(request):
    """
    Экспорт метрик в формате Prometheus
    Доступно только для администраторов
    """
    metrics_data = generate_latest()
    return HttpResponse(
        metrics_data,
        content_type=CONTENT_TYPE_LATEST
    )


@never_cache
@require_http_methods(["GET"])
@login_required
def health_check_view(request):
    """
    Проверка здоровья приложения
    """
    from django.db import connection
    from django.core.cache import cache
    import redis
    
    health_status = {
        'status': 'healthy',
        'checks': {}
    }
    
    # Проверка базы данных
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
        health_status['checks']['database'] = 'ok'
    except Exception as e:
        health_status['checks']['database'] = f'error: {str(e)}'
        health_status['status'] = 'unhealthy'
    
    # Проверка кэша
    try:
        cache.set('health_check', 'ok', 10)
        if cache.get('health_check') == 'ok':
            health_status['checks']['cache'] = 'ok'
        else:
            health_status['checks']['cache'] = 'error: cache not working'
            health_status['status'] = 'unhealthy'
    except Exception as e:
        health_status['checks']['cache'] = f'error: {str(e)}'
        health_status['status'] = 'unhealthy'
    
    # Проверка Redis
    try:
        from django.conf import settings
        import redis
        r = redis.from_url(settings.REDIS_URL)
        r.ping()
        health_status['checks']['redis'] = 'ok'
    except Exception as e:
        health_status['checks']['redis'] = f'error: {str(e)}'
        health_status['status'] = 'unhealthy'
    
    # Проверка Celery
    try:
        from celery import current_app
        inspect = current_app.control.inspect()
        stats = inspect.stats()
        if stats:
            health_status['checks']['celery'] = 'ok'
        else:
            health_status['checks']['celery'] = 'error: no workers'
            health_status['status'] = 'unhealthy'
    except Exception as e:
        health_status['checks']['celery'] = f'error: {str(e)}'
        health_status['status'] = 'unhealthy'
    
    return HttpResponse(
        f"Health Status: {health_status['status']}\n" +
        "\n".join([f"{k}: {v}" for k, v in health_status['checks'].items()]),
        content_type='text/plain',
        status=200 if health_status['status'] == 'healthy' else 503
    )
