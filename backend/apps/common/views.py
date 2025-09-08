"""
Общие views и error handlers
"""

import logging
from django.http import JsonResponse
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import exception_handler

logger = logging.getLogger(__name__)


def custom_exception_handler(exc, context):
    """
    Кастомный обработчик исключений для DRF
    """
    response = exception_handler(exc, context)
    
    if response is not None:
        custom_response_data = {
            'error': True,
            'message': 'Произошла ошибка при обработке запроса',
            'details': response.data,
            'status_code': response.status_code
        }
        
        # Логируем ошибку
        logger.error(
            f"API Error: {exc.__class__.__name__} - {str(exc)}",
            extra={
                'request': context.get('request'),
                'view': context.get('view'),
                'exc_info': exc
            }
        )
        
        response.data = custom_response_data
    
    return response


def bad_request(request, exception):
    """
    400 Bad Request error handler
    """
    logger.warning(f"Bad Request: {request.path} - {str(exception)}")
    return JsonResponse({
        'error': True,
        'message': 'Некорректный запрос',
        'status_code': 400
    }, status=400)


def permission_denied(request, exception):
    """
    403 Permission Denied error handler
    """
    logger.warning(f"Permission Denied: {request.path} - {str(exception)}")
    return JsonResponse({
        'error': True,
        'message': 'Доступ запрещён',
        'status_code': 403
    }, status=403)


def not_found(request, exception):
    """
    404 Not Found error handler
    """
    logger.info(f"Not Found: {request.path}")
    return JsonResponse({
        'error': True,
        'message': 'Ресурс не найден',
        'status_code': 404
    }, status=404)


def server_error(request):
    """
    500 Internal Server Error handler
    """
    logger.error(f"Server Error: {request.path}")
    return JsonResponse({
        'error': True,
        'message': 'Внутренняя ошибка сервера',
        'status_code': 500
    }, status=500)
