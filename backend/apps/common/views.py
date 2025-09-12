"""
Views для общих функций
"""

from rest_framework import generics, status, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.views import APIView
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from django.db.models import Q
from django.http import JsonResponse

from .models import Notification, NotificationSettings, AuditLog
from .serializers import (
    NotificationSerializer, NotificationSettingsSerializer,
    AuditLogSerializer
)
from .services import NotificationService, AuditService
from .utils import get_client_ip


class NotificationListView(generics.ListAPIView):
    """
    Список уведомлений пользователя
    """
    serializer_class = NotificationSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['notification_type', 'status', 'priority']
    search_fields = ['title', 'message']
    ordering_fields = ['created_at', 'priority']
    ordering = ['-created_at']
    
    def get_queryset(self):
        """Возвращает уведомления текущего пользователя"""
        return Notification.objects.filter(
            recipient=self.request.user
        ).select_related('recipient')


class NotificationDetailView(generics.RetrieveUpdateAPIView):
    """
    Детали уведомления и отметка как прочитанное
    """
    serializer_class = NotificationSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """Возвращает уведомления текущего пользователя"""
        return Notification.objects.filter(recipient=self.request.user)
    
    def update(self, request, *args, **kwargs):
        """Отмечает уведомление как прочитанное"""
        notification = self.get_object()
        notification.mark_as_read()
        
        return Response(
            {"message": "Уведомление отмечено как прочитанное"},
            status=status.HTTP_200_OK
        )


class NotificationSettingsView(generics.RetrieveUpdateAPIView):
    """
    Настройки уведомлений пользователя
    """
    serializer_class = NotificationSettingsSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_object(self):
        """Получает или создает настройки пользователя"""
        settings_obj, created = NotificationSettings.objects.get_or_create(
            user=self.request.user
        )
        return settings_obj


class MarkAllNotificationsReadView(APIView):
    """
    Отметить все уведомления как прочитанные
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request):
        """Отмечает все уведомления пользователя как прочитанные"""
        NotificationService.mark_notifications_as_read(request.user)
        
        return Response(
            {"message": "Все уведомления отмечены как прочитанные"},
            status=status.HTTP_200_OK
        )


class NotificationStatsView(APIView):
    """
    Статистика уведомлений пользователя
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        """Возвращает статистику уведомлений"""
        user = request.user
        
        stats = {
            'total': Notification.objects.filter(recipient=user).count(),
            'unread': NotificationService.get_unread_count(user),
            'by_type': {},
            'by_status': {},
            'by_priority': {}
        }
        
        # Статистика по типам
        for notification_type, _ in Notification.NotificationType.choices:
            count = Notification.objects.filter(
                recipient=user,
                notification_type=notification_type
            ).count()
            stats['by_type'][notification_type] = count
        
        # Статистика по статусам
        for status, _ in Notification.Status.choices:
            count = Notification.objects.filter(
                recipient=user,
                status=status
            ).count()
            stats['by_status'][status] = count
        
        # Статистика по приоритетам
        for priority, _ in Notification.Priority.choices:
            count = Notification.objects.filter(
                recipient=user,
                priority=priority
            ).count()
            stats['by_priority'][priority] = count
        
        return Response(stats)


class AuditLogListView(generics.ListAPIView):
    """
    Список записей аудита (только для администраторов)
    """
    serializer_class = AuditLogSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['action', 'object_type', 'user']
    search_fields = ['object_repr', 'details']
    ordering_fields = ['created_at', 'action']
    ordering = ['-created_at']
    
    def get_queryset(self):
        """Возвращает записи аудита"""
        # Только администраторы могут видеть все записи
        if not (self.request.user.is_staff or getattr(self.request.user, 'is_admin', False)):
            # Обычные пользователи видят только свои записи
            return AuditLog.objects.filter(user=self.request.user)
        
        return AuditLog.objects.all().select_related('user')


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def notification_unread_count(request):
    """
    Количество непрочитанных уведомлений
    """
    count = NotificationService.get_unread_count(request.user)
    return Response({'unread_count': count})


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def test_notification(request):
    """
    Отправка тестового уведомления (для разработки)
    """
    if not (request.user.is_staff or getattr(request.user, 'is_admin', False)):
        return Response(
            {"error": "Недостаточно прав"},
            status=status.HTTP_403_FORBIDDEN
        )
    
    notification_type = request.data.get('type', 'system_alert')
    title = request.data.get('title', 'Тестовое уведомление')
    message = request.data.get('message', 'Это тестовое уведомление')
    priority = request.data.get('priority', 'normal')
    
    notification = NotificationService.create_notification(
        recipient=request.user,
        notification_type=notification_type,
        title=title,
        message=message,
        priority=priority
    )
    
    return Response(
        {"message": "Тестовое уведомление создано", "notification_id": notification.id},
        status=status.HTTP_201_CREATED
    )


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def cleanup_notifications(request):
    """
    Очистка старых уведомлений (только для администраторов)
    """
    if not (request.user.is_staff or getattr(request.user, 'is_admin', False)):
        return Response(
            {"error": "Недостаточно прав"},
            status=status.HTTP_403_FORBIDDEN
        )
    
    days = request.data.get('days', 30)
    deleted_count = NotificationService.cleanup_old_notifications(days)
    
    return Response(
        {"message": f"Удалено {deleted_count} старых уведомлений"},
        status=status.HTTP_200_OK
    )


# Обработчики ошибок
def bad_request(request, exception=None):
    """Обработчик ошибки 400"""
    return JsonResponse({
        'error': 'Bad Request',
        'message': 'Некорректный запрос'
    }, status=400)


def permission_denied(request, exception=None):
    """Обработчик ошибки 403"""
    return JsonResponse({
        'error': 'Permission Denied',
        'message': 'Доступ запрещен'
    }, status=403)


def not_found(request, exception=None):
    """Обработчик ошибки 404"""
        return JsonResponse({
        'error': 'Not Found',
        'message': 'Ресурс не найден'
    }, status=404)


def server_error(request):
    """Обработчик ошибки 500"""
        return JsonResponse({
            'error': 'Internal Server Error',
        'message': 'Внутренняя ошибка сервера'
        }, status=500)