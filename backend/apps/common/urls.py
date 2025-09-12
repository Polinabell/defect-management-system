"""
URL маршруты для общих функций
"""

from django.urls import path
from . import views
from . import metrics_views

app_name = 'common'

urlpatterns = [
    # Уведомления
    path('notifications/', views.NotificationListView.as_view(), name='notification-list'),
    path('notifications/<int:pk>/', views.NotificationDetailView.as_view(), name='notification-detail'),
    path('notifications/mark-all-read/', views.MarkAllNotificationsReadView.as_view(), name='mark-all-notifications-read'),
    path('notifications/stats/', views.NotificationStatsView.as_view(), name='notification-stats'),
    path('notifications/unread-count/', views.notification_unread_count, name='notification-unread-count'),
    path('notifications/test/', views.test_notification, name='test-notification'),
    path('notifications/cleanup/', views.cleanup_notifications, name='cleanup-notifications'),
    
    # Настройки уведомлений
    path('notification-settings/', views.NotificationSettingsView.as_view(), name='notification-settings'),
    
    # Аудит
    path('audit-logs/', views.AuditLogListView.as_view(), name='audit-log-list'),
    
    # Метрики и мониторинг
    path('metrics/', metrics_views.metrics_view, name='metrics'),
    path('health/', metrics_views.health_check_view, name='health-check'),
]
