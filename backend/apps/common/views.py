"""
Общие views для приложения
"""

from django.http import JsonResponse
from django.template import loader
from django.views.decorators.csrf import requires_csrf_token
from django.views.decorators.cache import never_cache
from rest_framework import status
import logging

logger = logging.getLogger(__name__)


@never_cache
@requires_csrf_token
def bad_request(request, exception=None):
    """
    Обработчик ошибки 400 - Неправильный запрос
    """
    logger.warning(
        f"Bad request (400) for path: {request.path}",
        extra={
            'request': request,
            'status_code': 400,
            'exception': str(exception) if exception else None
        }
    )
    
    if request.path.startswith('/api/'):
        return JsonResponse({
            'error': 'Неправильный запрос',
            'status_code': 400,
            'detail': 'Запрос содержит неверные данные'
        }, status=400)
    
    try:
        template = loader.get_template('errors/400.html')
        return JsonResponse({
            'error': 'Bad Request',
            'status_code': 400
        }, status=400)
    except:
        return JsonResponse({
            'error': 'Bad Request',
            'status_code': 400
        }, status=400)


@never_cache
@requires_csrf_token
def permission_denied(request, exception=None):
    """
    Обработчик ошибки 403 - Доступ запрещён
    """
    logger.warning(
        f"Permission denied (403) for path: {request.path}",
        extra={
            'request': request,
            'status_code': 403,
            'user': request.user.id if hasattr(request, 'user') and request.user.is_authenticated else None,
            'exception': str(exception) if exception else None
        }
    )
    
    if request.path.startswith('/api/'):
        return JsonResponse({
            'error': 'Доступ запрещён',
            'status_code': 403,
            'detail': 'У вас недостаточно прав для выполнения этого действия'
        }, status=403)
    
    try:
        template = loader.get_template('errors/403.html')
        return JsonResponse({
            'error': 'Permission Denied',
            'status_code': 403
        }, status=403)
    except:
        return JsonResponse({
            'error': 'Permission Denied',
            'status_code': 403
        }, status=403)


@never_cache
@requires_csrf_token
def not_found(request, exception=None):
    """
    Обработчик ошибки 404 - Страница не найдена
    """
    logger.info(
        f"Page not found (404) for path: {request.path}",
        extra={
            'request': request,
            'status_code': 404,
            'exception': str(exception) if exception else None
        }
    )
    
    if request.path.startswith('/api/'):
        return JsonResponse({
            'error': 'Ресурс не найден',
            'status_code': 404,
            'detail': 'Запрашиваемый ресурс не существует'
        }, status=404)
    
    try:
        template = loader.get_template('errors/404.html')
        return JsonResponse({
            'error': 'Not Found',
            'status_code': 404
        }, status=404)
    except:
        return JsonResponse({
            'error': 'Not Found',
            'status_code': 404
        }, status=404)


@never_cache
@requires_csrf_token
def server_error(request):
    """
    Обработчик ошибки 500 - Внутренняя ошибка сервера
    """
    logger.error(
        f"Internal server error (500) for path: {request.path}",
        extra={
            'request': request,
            'status_code': 500
        },
        exc_info=True
    )
    
    if request.path.startswith('/api/'):
        return JsonResponse({
            'error': 'Внутренняя ошибка сервера',
            'status_code': 500,
            'detail': 'Произошла внутренняя ошибка сервера. Пожалуйста, попробуйте позже.'
        }, status=500)
    
    try:
        template = loader.get_template('errors/500.html')
        return JsonResponse({
            'error': 'Internal Server Error',
            'status_code': 500
        }, status=500)
    except:
        return JsonResponse({
            'error': 'Internal Server Error',
            'status_code': 500
        }, status=500)