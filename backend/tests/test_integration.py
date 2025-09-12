"""
Интеграционные тесты
"""

from django.test import TestCase, TransactionTestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from apps.projects.models import Project, ProjectStage
from apps.defects.models import Defect, DefectCategory, DefectComment
from apps.common.models import Notification, AuditLog
from apps.common.services import NotificationService

User = get_user_model()


class DefectWorkflowIntegrationTest(APITestCase):
    """
    Интеграционный тест полного жизненного цикла дефекта
    """
    
    def setUp(self):
        # Создаем пользователей
        self.manager = User.objects.create_user(
            email='manager@example.com',
            username='manager',
            first_name='Менеджер',
            last_name='Проекта',
            role=User.Role.MANAGER
        )
        
        self.engineer = User.objects.create_user(
            email='engineer@example.com',
            username='engineer',
            first_name='Инженер',
            last_name='Исполнитель',
            role=User.Role.ENGINEER
        )
        
        # Создаем проект
        self.project = Project.objects.create(
            name='Тестовый проект',
            description='Описание проекта',
            manager=self.manager
        )
        
        # Создаем категорию дефекта
        self.category = DefectCategory.objects.create(
            name='Критический дефект',
            color='#FF0000'
        )
        
        # Аутентификация менеджера
        refresh = RefreshToken.for_user(self.manager)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')
    
    def test_complete_defect_workflow(self):
        """Тест полного жизненного цикла дефекта"""
        
        # 1. Создание дефекта менеджером
        create_url = reverse('defects:defect-list-create')
        defect_data = {
            'title': 'Критический дефект в системе',
            'description': 'Подробное описание дефекта',
            'project': self.project.id,
            'category': self.category.id,
            'priority': 'high',
            'severity': 'critical'
        }
        
        response = self.client.post(create_url, defect_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        defect_id = response.data['id']
        
        # Проверяем, что дефект создан
        defect = Defect.objects.get(id=defect_id)
        self.assertEqual(defect.status, Defect.Status.NEW)
        self.assertEqual(defect.author, self.manager)
        
        # 2. Назначение исполнителя
        assign_url = reverse('defects:defect-assignment', kwargs={'defect_id': defect_id})
        assign_data = {
            'assignee': self.engineer.id
        }
        
        response = self.client.post(assign_url, assign_data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Проверяем назначение
        defect.refresh_from_db()
        self.assertEqual(defect.assignee, self.engineer)
        
        # 3. Переход в работу (исполнитель)
        refresh = RefreshToken.for_user(self.engineer)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')
        
        status_url = reverse('defects:defect-status-change', kwargs={'defect_id': defect_id})
        status_data = {
            'status': 'in_progress'
        }
        
        response = self.client.post(status_url, status_data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Проверяем изменение статуса
        defect.refresh_from_db()
        self.assertEqual(defect.status, Defect.Status.IN_PROGRESS)
        
        # 4. Добавление комментария
        comment_url = reverse('defects:defect-comments', kwargs={'defect_pk': defect_id})
        comment_data = {
            'text': 'Начал работу над исправлением дефекта'
        }
        
        response = self.client.post(comment_url, comment_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        # Проверяем комментарий
        comment = DefectComment.objects.filter(defect=defect).first()
        self.assertEqual(comment.text, 'Начал работу над исправлением дефекта')
        self.assertEqual(comment.author, self.engineer)
        
        # 5. Переход на проверку
        status_data = {
            'status': 'review'
        }
        
        response = self.client.post(status_url, status_data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Проверяем статус
        defect.refresh_from_db()
        self.assertEqual(defect.status, Defect.Status.REVIEW)
        
        # 6. Закрытие дефекта менеджером
        refresh = RefreshToken.for_user(self.manager)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')
        
        status_data = {
            'status': 'closed',
            'resolution_description': 'Дефект исправлен и протестирован'
        }
        
        response = self.client.post(status_url, status_data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Проверяем закрытие
        defect.refresh_from_db()
        self.assertEqual(defect.status, Defect.Status.CLOSED)
        self.assertEqual(defect.resolution_description, 'Дефект исправлен и протестирован')
        
        # 7. Проверяем историю изменений
        history_url = reverse('defects:defect-history', kwargs={'defect_pk': defect_id})
        response = self.client.get(history_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Должно быть несколько записей в истории
        self.assertGreater(len(response.data), 0)


class NotificationIntegrationTest(APITestCase):
    """
    Интеграционный тест системы уведомлений
    """
    
    def setUp(self):
        # Создаем пользователей
        self.manager = User.objects.create_user(
            email='manager@example.com',
            username='manager',
            first_name='Менеджер',
            last_name='Проекта',
            role=User.Role.MANAGER
        )
        
        self.engineer = User.objects.create_user(
            email='engineer@example.com',
            username='engineer',
            first_name='Инженер',
            last_name='Исполнитель',
            role=User.Role.ENGINEER
        )
        
        # Создаем проект
        self.project = Project.objects.create(
            name='Тестовый проект',
            manager=self.manager
        )
        
        # Создаем категорию дефекта
        self.category = DefectCategory.objects.create(
            name='Тестовая категория',
            color='#FF0000'
        )
        
        # Аутентификация менеджера
        refresh = RefreshToken.for_user(self.manager)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')
    
    def test_notification_workflow(self):
        """Тест полного цикла уведомлений"""
        
        # 1. Создание дефекта (должно создать уведомление)
        create_url = reverse('defects:defect-list-create')
        defect_data = {
            'title': 'Дефект для тестирования уведомлений',
            'description': 'Описание дефекта',
            'project': self.project.id,
            'category': self.category.id
        }
        
        response = self.client.post(create_url, defect_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        defect_id = response.data['id']
        
        # Проверяем, что уведомление создано
        notifications = Notification.objects.filter(recipient=self.manager)
        self.assertGreater(notifications.count(), 0)
        
        # 2. Назначение исполнителя (должно создать уведомление исполнителю)
        assign_url = reverse('defects:defect-assignment', kwargs={'defect_id': defect_id})
        assign_data = {
            'assignee': self.engineer.id
        }
        
        response = self.client.post(assign_url, assign_data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Проверяем уведомление исполнителю
        engineer_notifications = Notification.objects.filter(recipient=self.engineer)
        self.assertGreater(engineer_notifications.count(), 0)
        
        # 3. Получение списка уведомлений
        notifications_url = reverse('common:notification-list')
        response = self.client.get(notifications_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # 4. Отметка уведомления как прочитанного
        notification = engineer_notifications.first()
        mark_read_url = reverse('common:notification-detail', kwargs={'pk': notification.id})
        response = self.client.patch(mark_read_url, {})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Проверяем, что уведомление отмечено как прочитанное
        notification.refresh_from_db()
        self.assertTrue(notification.is_read)
        
        # 5. Получение статистики уведомлений
        stats_url = reverse('common:notification-stats')
        response = self.client.get(stats_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Проверяем статистику
        self.assertIn('total', response.data)
        self.assertIn('unread', response.data)
        self.assertIn('by_type', response.data)


class AuditIntegrationTest(APITestCase):
    """
    Интеграционный тест системы аудита
    """
    
    def setUp(self):
        self.user = User.objects.create_user(
            email='test@example.com',
            username='testuser',
            first_name='Тест',
            last_name='Пользователь',
            role=User.Role.MANAGER
        )
        
        # Аутентификация
        refresh = RefreshToken.for_user(self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')
    
    def test_audit_logging_workflow(self):
        """Тест полного цикла аудита"""
        
        # 1. Создание проекта (должно создать запись аудита)
        project_url = reverse('projects:project-list-create')
        project_data = {
            'name': 'Проект для аудита',
            'description': 'Описание проекта'
        }
        
        response = self.client.post(project_url, project_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        # Проверяем запись аудита
        audit_logs = AuditLog.objects.filter(user=self.user)
        self.assertGreater(audit_logs.count(), 0)
        
        # 2. Получение списка записей аудита
        audit_url = reverse('common:audit-log-list')
        response = self.client.get(audit_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Проверяем, что записи возвращаются
        self.assertGreater(len(response.data['results']), 0)
        
        # 3. Проверяем детали записи аудита
        audit_log = audit_logs.first()
        self.assertEqual(audit_log.user, self.user)
        self.assertEqual(audit_log.action, AuditLog.ActionType.CREATE)
        self.assertEqual(audit_log.object_type, 'project')