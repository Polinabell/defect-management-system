"""
Тесты для API endpoints
"""

from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from apps.projects.models import Project
from apps.defects.models import Defect, DefectCategory

User = get_user_model()


class AuthenticationAPITest(APITestCase):
    """Тесты для API аутентификации"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            email='test@example.com',
            username='testuser',
            first_name='Тест',
            last_name='Пользователь',
            password='testpass123'
        )
        self.login_url = reverse('auth:token_obtain_pair')
    
    def test_login_success(self):
        """Тест успешного входа"""
        data = {
            'email': 'test@example.com',
            'password': 'testpass123'
        }
        response = self.client.post(self.login_url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)
    
    def test_login_invalid_credentials(self):
        """Тест входа с неверными данными"""
        data = {
            'email': 'test@example.com',
            'password': 'wrongpassword'
        }
        response = self.client.post(self.login_url, data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_protected_endpoint_without_token(self):
        """Тест доступа к защищенному endpoint без токена"""
        url = reverse('users:user-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_protected_endpoint_with_token(self):
        """Тест доступа к защищенному endpoint с токеном"""
        refresh = RefreshToken.for_user(self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')
        
        url = reverse('users:user-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class DefectsAPITest(APITestCase):
    """Тесты для API дефектов"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            email='test@example.com',
            username='testuser',
            first_name='Тест',
            last_name='Пользователь',
            password='testpass123'
        )
        self.project = Project.objects.create(
            name='Тестовый проект',
            manager=self.user
        )
        self.category = DefectCategory.objects.create(
            name='Тестовая категория',
            color='#FF0000'
        )
        
        # Аутентификация
        refresh = RefreshToken.for_user(self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')
    
    def test_create_defect(self):
        """Тест создания дефекта"""
        url = reverse('defects:defect-list-create')
        data = {
            'title': 'Новый дефект',
            'description': 'Описание дефекта',
            'project': self.project.id,
            'category': self.category.id
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Defect.objects.count(), 1)
    
    def test_list_defects(self):
        """Тест получения списка дефектов"""
        Defect.objects.create(
            title='Тестовый дефект',
            description='Описание',
            project=self.project,
            category=self.category,
            author=self.user
        )
        
        url = reverse('defects:defect-list-create')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
    
    def test_defect_detail(self):
        """Тест получения деталей дефекта"""
        defect = Defect.objects.create(
            title='Тестовый дефект',
            description='Описание',
            project=self.project,
            category=self.category,
            author=self.user
        )
        
        url = reverse('defects:defect-detail', kwargs={'pk': defect.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], 'Тестовый дефект')


class ProjectsAPITest(APITestCase):
    """Тесты для API проектов"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            email='test@example.com',
            username='testuser',
            first_name='Тест',
            last_name='Пользователь',
            password='testpass123'
        )
        
        # Аутентификация
        refresh = RefreshToken.for_user(self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')
    
    def test_create_project(self):
        """Тест создания проекта"""
        url = reverse('projects:project-list-create')
        data = {
            'name': 'Новый проект',
            'description': 'Описание проекта'
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Project.objects.count(), 1)
    
    def test_list_projects(self):
        """Тест получения списка проектов"""
        Project.objects.create(
            name='Тестовый проект',
            manager=self.user
        )
        
        url = reverse('projects:project-list-create')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)


class SecurityAPITest(APITestCase):
    """Тесты для безопасности API"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            email='test@example.com',
            username='testuser',
            first_name='Тест',
            last_name='Пользователь',
            password='testpass123'
        )
    
    def test_sql_injection_protection(self):
        """Тест защиты от SQL инъекций"""
        url = reverse('defects:defect-list-create')
        malicious_data = {
            'title': "'; DROP TABLE defects; --",
            'description': 'Описание'
        }
        response = self.client.post(url, malicious_data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_xss_protection(self):
        """Тест защиты от XSS"""
        url = reverse('defects:defect-list-create')
        malicious_data = {
            'title': '<script>alert("XSS")</script>',
            'description': 'Описание'
        }
        response = self.client.post(url, malicious_data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_rate_limiting(self):
        """Тест ограничения частоты запросов"""
        url = reverse('defects:defect-list-create')
        
        # Делаем много запросов подряд
        for i in range(150):  # Превышаем лимит в 100 запросов
            response = self.client.get(url)
            if response.status_code == status.HTTP_429_TOO_MANY_REQUESTS:
                break
        
        # Проверяем, что получили ошибку ограничения
        self.assertEqual(response.status_code, status.HTTP_429_TOO_MANY_REQUESTS)
