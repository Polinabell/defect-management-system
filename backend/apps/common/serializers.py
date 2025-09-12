"""
Сериализаторы для общих моделей
"""

from rest_framework import serializers
from .models import Notification, NotificationSettings, AuditLog


class NotificationSerializer(serializers.ModelSerializer):
    """
    Сериализатор уведомления
    """
    recipient_name = serializers.ReadOnlyField(source='recipient.get_full_name')
    notification_type_display = serializers.ReadOnlyField(source='get_notification_type_display')
    priority_display = serializers.ReadOnlyField(source='get_priority_display')
    status_display = serializers.ReadOnlyField(source='get_status_display')
    is_read = serializers.ReadOnlyField()
    is_sent = serializers.ReadOnlyField()
    
    class Meta:
        model = Notification
        fields = [
            'id', 'recipient', 'recipient_name', 'notification_type',
            'notification_type_display', 'title', 'message', 'priority',
            'priority_display', 'status', 'status_display', 'related_object_type',
            'related_object_id', 'send_email', 'send_sms', 'send_push',
            'sent_at', 'read_at', 'is_read', 'is_sent', 'metadata', 'created_at'
        ]
        read_only_fields = [
            'id', 'recipient', 'sent_at', 'read_at', 'is_read', 'is_sent', 'created_at'
        ]


class NotificationSettingsSerializer(serializers.ModelSerializer):
    """
    Сериализатор настроек уведомлений
    """
    user_name = serializers.ReadOnlyField(source='user.get_full_name')
    
    class Meta:
        model = NotificationSettings
        fields = [
            'id', 'user', 'user_name', 'email_enabled', 'email_frequency',
            'sms_enabled', 'sms_phone', 'push_enabled', 'notification_preferences',
            'quiet_hours_start', 'quiet_hours_end', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'user', 'created_at', 'updated_at']


class AuditLogSerializer(serializers.ModelSerializer):
    """
    Сериализатор записи аудита
    """
    user_name = serializers.ReadOnlyField(source='user.get_full_name')
    action_display = serializers.ReadOnlyField(source='get_action_display')
    created_by_name = serializers.ReadOnlyField(source='created_by.get_full_name')
    
    class Meta:
        model = AuditLog
        fields = [
            'id', 'user', 'user_name', 'action', 'action_display',
            'object_type', 'object_id', 'object_repr', 'details',
            'ip_address', 'user_agent', 'created_at', 'created_by',
            'created_by_name'
        ]
        read_only_fields = [
            'id', 'created_at', 'created_by'
        ]
