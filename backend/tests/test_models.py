"""
Юнит-тесты для моделей
"""

from django.test import TestCase
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from apps.users.models import User, UserProfile
from apps.projects.models import Project, ProjectStage
from apps.defects.models import Defect, DefectCategory, DefectFile
from apps.common.models import Notification, AuditLog

User = get_user_model()


class UserModelTest(TestCase):
    """Тесты для модели User"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            email='test@example.com',
            username='testuser',
            first_name='Тест',
            last_name='Пользователь',
            password='testpass123'
        )
    
    def test_user_creation(self):
        """Тест создания пользователя"""
        self.assertEqual(self.user.email, 'test@example.com')
        self.assertEqual(self.user.get_full_name(), 'Пользователь Тест')
        self.assertTrue(self.user.check_password('testpass123'))
    
    def test_user_roles(self):
        """Тест ролей пользователя"""
        self.user.role = User.Role.ADMIN
        self.assertTrue(self.user.is_admin)
        
        self.user.role = User.Role.MANAGER
        self.assertTrue(self.user.is_manager)
        
        self.user.role = User.Role.ENGINEER
        self.assertTrue(self.user.is_engineer)
    
    def test_account_locking(self):
        """Тест блокировки аккаунта"""
        self.assertFalse(self.user.is_locked)
        
        self.user.lock_account()
        self.assertTrue(self.user.is_locked)
        
        self.user.unlock_account()
        self.assertFalse(self.user.is_locked)


class ProjectModelTest(TestCase):
    """Тесты для модели Project"""
    
    def setUp(self):
        self.manager = User.objects.create_user(
            email='manager@example.com',
            username='manager',
            first_name='Менеджер',
            last_name='Проекта'
        )
        self.project = Project.objects.create(
            name='Тестовый проект',
            description='Описание проекта',
            manager=self.manager
        )
    
    def test_project_creation(self):
        """Тест создания проекта"""
        self.assertEqual(self.project.name, 'Тестовый проект')
        self.assertEqual(self.project.manager, self.manager)
        self.assertEqual(str(self.project), 'Тестовый проект')
    
    def test_project_stages(self):
        """Тест этапов проекта"""
        stage = ProjectStage.objects.create(
            project=self.project,
            name='Первый этап',
            description='Описание этапа'
        )
        self.assertEqual(stage.project, self.project)
        self.assertIn(stage, self.project.stages.all())


class DefectModelTest(TestCase):
    """Тесты для модели Defect"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            email='user@example.com',
            username='user',
            first_name='Пользователь',
            last_name='Тест'
        )
        self.project = Project.objects.create(
            name='Тестовый проект',
            manager=self.user
        )
        self.category = DefectCategory.objects.create(
            name='Тестовая категория',
            color='#FF0000'
        )
        self.defect = Defect.objects.create(
            title='Тестовый дефект',
            description='Описание дефекта',
            project=self.project,
            category=self.category,
            author=self.user
        )
    
    def test_defect_creation(self):
        """Тест создания дефекта"""
        self.assertEqual(self.defect.title, 'Тестовый дефект')
        self.assertEqual(self.defect.status, Defect.Status.NEW)
        self.assertEqual(self.defect.author, self.user)
    
    def test_defect_status_transitions(self):
        """Тест переходов статусов дефекта"""
        # Новый -> В работе
        self.defect.status = Defect.Status.IN_PROGRESS
        self.defect.save()
        self.assertEqual(self.defect.status, Defect.Status.IN_PROGRESS)
        
        # В работе -> На проверке
        self.defect.status = Defect.Status.REVIEW
        self.defect.save()
        self.assertEqual(self.defect.status, Defect.Status.REVIEW)
        
        # На проверке -> Закрыт
        self.defect.status = Defect.Status.CLOSED
        self.defect.save()
        self.assertEqual(self.defect.status, Defect.Status.CLOSED)


class NotificationModelTest(TestCase):
    """Тесты для модели Notification"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            email='user@example.com',
            username='user',
            first_name='Пользователь',
            last_name='Тест'
        )
        self.notification = Notification.objects.create(
            recipient=self.user,
            notification_type=Notification.NotificationType.SYSTEM_ALERT,
            title='Тестовое уведомление',
            message='Сообщение уведомления'
        )
    
    def test_notification_creation(self):
        """Тест создания уведомления"""
        self.assertEqual(self.notification.recipient, self.user)
        self.assertEqual(self.notification.title, 'Тестовое уведомление')
        self.assertFalse(self.notification.is_read)
    
    def test_notification_mark_as_read(self):
        """Тест отметки уведомления как прочитанного"""
        self.notification.mark_as_read()
        self.assertTrue(self.notification.is_read)
        self.assertEqual(self.notification.status, Notification.Status.READ)


class AuditLogModelTest(TestCase):
    """Тесты для модели AuditLog"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            email='user@example.com',
            username='user',
            first_name='Пользователь',
            last_name='Тест'
        )
        self.audit_log = AuditLog.objects.create(
            user=self.user,
            action=AuditLog.ActionType.CREATE,
            object_type='defect',
            object_id=1,
            object_repr='Тестовый дефект'
        )
    
    def test_audit_log_creation(self):
        """Тест создания записи аудита"""
        self.assertEqual(self.audit_log.user, self.user)
        self.assertEqual(self.audit_log.action, AuditLog.ActionType.CREATE)
        self.assertEqual(self.audit_log.object_type, 'defect')
        self.assertEqual(str(self.audit_log), 'Пользователь Тест - Создание')
