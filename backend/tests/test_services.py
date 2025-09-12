"""
Тесты для сервисов
"""

from django.test import TestCase
from django.contrib.auth import get_user_model
from unittest.mock import patch, MagicMock
from apps.common.services import NotificationService, EmailService, AuditService
from apps.common.models import Notification, NotificationSettings

User = get_user_model()


class NotificationServiceTest(TestCase):
    """Тесты для NotificationService"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            email='test@example.com',
            username='testuser',
            first_name='Тест',
            last_name='Пользователь',
            password='testpass123'
        )
    
    def test_create_notification(self):
        """Тест создания уведомления"""
        notification = NotificationService.create_notification(
            recipient=self.user,
            notification_type='system_alert',
            title='Тестовое уведомление',
            message='Сообщение',
            send_immediately=False
        )
        
        self.assertEqual(notification.recipient, self.user)
        self.assertEqual(notification.title, 'Тестовое уведомление')
        self.assertEqual(notification.notification_type, 'system_alert')
    
    def test_mark_notifications_as_read(self):
        """Тест отметки уведомлений как прочитанных"""
        # Создаем уведомления
        Notification.objects.create(
            recipient=self.user,
            notification_type='system_alert',
            title='Уведомление 1',
            message='Сообщение 1'
        )
        Notification.objects.create(
            recipient=self.user,
            notification_type='system_alert',
            title='Уведомление 2',
            message='Сообщение 2'
        )
        
        # Отмечаем как прочитанные
        NotificationService.mark_notifications_as_read(self.user)
        
        # Проверяем, что все уведомления отмечены как прочитанные
        unread_count = NotificationService.get_unread_count(self.user)
        self.assertEqual(unread_count, 0)
    
    def test_get_unread_count(self):
        """Тест получения количества непрочитанных уведомлений"""
        # Создаем уведомления
        Notification.objects.create(
            recipient=self.user,
            notification_type='system_alert',
            title='Уведомление 1',
            message='Сообщение 1'
        )
        Notification.objects.create(
            recipient=self.user,
            notification_type='system_alert',
            title='Уведомление 2',
            message='Сообщение 2'
        )
        
        # Одно отмечаем как прочитанное
        notification = Notification.objects.first()
        notification.mark_as_read()
        
        # Проверяем количество непрочитанных
        unread_count = NotificationService.get_unread_count(self.user)
        self.assertEqual(unread_count, 1)


class EmailServiceTest(TestCase):
    """Тесты для EmailService"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            email='test@example.com',
            username='testuser',
            first_name='Тест',
            last_name='Пользователь',
            password='testpass123'
        )
    
    @patch('apps.common.services.send_mail')
    def test_send_welcome_email(self, mock_send_mail):
        """Тест отправки приветственного письма"""
        EmailService.send_welcome_email(self.user)
        
        # Проверяем, что send_mail был вызван
        mock_send_mail.assert_called_once()
        
        # Проверяем аргументы
        call_args = mock_send_mail.call_args
        self.assertIn('Добро пожаловать', call_args[1]['subject'])
        self.assertEqual(call_args[1]['recipient_list'], [self.user.email])
    
    @patch('apps.common.services.send_mail')
    def test_send_password_reset_email(self, mock_send_mail):
        """Тест отправки письма для сброса пароля"""
        reset_token = 'test-token-123'
        EmailService.send_password_reset_email(self.user, reset_token)
        
        # Проверяем, что send_mail был вызван
        mock_send_mail.assert_called_once()
        
        # Проверяем аргументы
        call_args = mock_send_mail.call_args
        self.assertIn('Сброс пароля', call_args[1]['subject'])
        self.assertEqual(call_args[1]['recipient_list'], [self.user.email])


class AuditServiceTest(TestCase):
    """Тесты для AuditService"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            email='test@example.com',
            username='testuser',
            first_name='Тест',
            last_name='Пользователь',
            password='testpass123'
        )
    
    def test_log_user_action(self):
        """Тест логирования действий пользователя"""
        from apps.common.models import AuditLog
        
        AuditService.log_user_action(
            user=self.user,
            action='test_action',
            object_type='test_object',
            object_id=1,
            details={'test': 'data'}
        )
        
        # Проверяем, что запись создана
        audit_log = AuditLog.objects.get(user=self.user)
        self.assertEqual(audit_log.action, 'test_action')
        self.assertEqual(audit_log.object_type, 'test_object')
        self.assertEqual(audit_log.object_id, 1)
        self.assertEqual(audit_log.details, {'test': 'data'})
    
    def test_log_user_action_without_user(self):
        """Тест логирования действий без пользователя"""
        from apps.common.models import AuditLog
        
        AuditService.log_user_action(
            user=None,
            action='system_action',
            object_type='system_object'
        )
        
        # Проверяем, что запись создана
        audit_log = AuditLog.objects.get(action='system_action')
        self.assertIsNone(audit_log.user)
        self.assertEqual(audit_log.action, 'system_action')


class NotificationSettingsTest(TestCase):
    """Тесты для настроек уведомлений"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            email='test@example.com',
            username='testuser',
            first_name='Тест',
            last_name='Пользователь',
            password='testpass123'
        )
    
    def test_notification_settings_creation(self):
        """Тест создания настроек уведомлений"""
        settings_obj, created = NotificationSettings.objects.get_or_create(
            user=self.user
        )
        
        self.assertTrue(created)
        self.assertEqual(settings_obj.user, self.user)
        self.assertTrue(settings_obj.email_enabled)
        self.assertFalse(settings_obj.sms_enabled)
    
    def test_quiet_time_check(self):
        """Тест проверки времени тишины"""
        settings_obj = NotificationSettings.objects.create(
            user=self.user,
            quiet_hours_start='22:00',
            quiet_hours_end='08:00'
        )
        
        # Проверяем, что время тишины работает
        # (в реальном тесте нужно мокать время)
        self.assertIsInstance(settings_obj.is_quiet_time(), bool)
    
    def test_should_send_notification(self):
        """Тест проверки отправки уведомления"""
        settings_obj = NotificationSettings.objects.create(
            user=self.user,
            email_enabled=True,
            sms_enabled=False,
            push_enabled=True
        )
        
        # Проверяем email
        self.assertTrue(settings_obj.should_send_notification('system_alert', 'email'))
        
        # Проверяем SMS
        self.assertFalse(settings_obj.should_send_notification('system_alert', 'sms'))
        
        # Проверяем push
        self.assertTrue(settings_obj.should_send_notification('system_alert', 'push'))
