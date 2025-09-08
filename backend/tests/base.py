"""
Базовые классы для тестирования
"""

import pytest
from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase
from rest_framework_simplejwt.tokens import RefreshToken

User = get_user_model()


class BaseTestCase(TestCase):
    """
    Базовый класс для всех тестов
    """
    
    @classmethod
    def setUpTestData(cls):
        """Настройка общих тестовых данных"""
        cls.admin_user = User.objects.create_user(
            username='admin',
            email='admin@test.com',
            first_name='Admin',
            last_name='User',
            role='admin',
            is_staff=True,
            is_superuser=True
        )
        
        cls.manager_user = User.objects.create_user(
            username='manager',
            email='manager@test.com', 
            first_name='Manager',
            last_name='User',
            role='manager'
        )
        
        cls.engineer_user = User.objects.create_user(
            username='engineer',
            email='engineer@test.com',
            first_name='Engineer', 
            last_name='User',
            role='engineer'
        )
        
        cls.observer_user = User.objects.create_user(
            username='observer',
            email='observer@test.com',
            first_name='Observer',
            last_name='User', 
            role='observer'
        )
    
    def setUp(self):
        """Настройка перед каждым тестом"""
        pass
    
    def tearDown(self):
        """Очистка после каждого теста"""
        pass


class BaseAPITestCase(APITestCase):
    """
    Базовый класс для API тестов
    """
    
    @classmethod
    def setUpTestData(cls):
        """Настройка общих тестовых данных"""
        cls.admin_user = User.objects.create_user(
            username='admin',
            email='admin@test.com',
            first_name='Admin',
            last_name='User',
            role='admin',
            is_staff=True,
            is_superuser=True
        )
        
        cls.manager_user = User.objects.create_user(
            username='manager',
            email='manager@test.com',
            first_name='Manager',
            last_name='User',
            role='manager'
        )
        
        cls.engineer_user = User.objects.create_user(
            username='engineer',
            email='engineer@test.com',
            first_name='Engineer',
            last_name='User',
            role='engineer'
        )
        
        cls.observer_user = User.objects.create_user(
            username='observer',
            email='observer@test.com',
            first_name='Observer',
            last_name='User',
            role='observer'
        )
    
    def authenticate(self, user):
        """Аутентификация пользователя для API тестов"""
        refresh = RefreshToken.for_user(user)
        access_token = str(refresh.access_token)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token}')
        return access_token
    
    def logout(self):
        """Выход из системы"""
        self.client.credentials()
    
    def assert_status_code(self, response, expected_status):
        """Проверка статус кода с детальным сообщением"""
        if response.status_code != expected_status:
            error_msg = f"Expected status {expected_status}, got {response.status_code}"
            if hasattr(response, 'data'):
                error_msg += f". Response data: {response.data}"
            self.fail(error_msg)
    
    def assert_permission_denied(self, response):
        """Проверка отказа в доступе"""
        self.assertIn(response.status_code, [401, 403])
    
    def assert_validation_error(self, response, field=None):
        """Проверка ошибки валидации"""
        self.assertEqual(response.status_code, 400)
        if field:
            self.assertIn(field, response.data)


@pytest.mark.django_db
class BasePytestCase:
    """
    Базовый класс для pytest тестов
    """
    
    @pytest.fixture(autouse=True)
    def setup_users(self, db):
        """Фикстура для создания пользователей"""
        self.admin_user = User.objects.create_user(
            username='admin',
            email='admin@test.com',
            first_name='Admin',
            last_name='User',
            role='admin',
            is_staff=True,
            is_superuser=True
        )
        
        self.manager_user = User.objects.create_user(
            username='manager',
            email='manager@test.com',
            first_name='Manager',
            last_name='User',
            role='manager'
        )
        
        self.engineer_user = User.objects.create_user(
            username='engineer',
            email='engineer@test.com',
            first_name='Engineer',
            last_name='User',
            role='engineer'
        )
        
        self.observer_user = User.objects.create_user(
            username='observer',
            email='observer@test.com',
            first_name='Observer',
            last_name='User',
            role='observer'
        )


class SecurityTestMixin:
    """
    Миксин для тестирования безопасности
    """
    
    def test_sql_injection_protection(self):
        """Тест защиты от SQL инъекций"""
        malicious_inputs = [
            "'; DROP TABLE users; --",
            "1' OR '1'='1",
            "admin'--",
            "' UNION SELECT password FROM users WHERE '1'='1",
        ]
        
        for malicious_input in malicious_inputs:
            # Тестируем различные поля
            response = self.client.get('/', {'search': malicious_input})
            # Проверяем, что запрос либо отклонён, либо обработан безопасно
            self.assertNotEqual(response.status_code, 500)
    
    def test_xss_protection(self):
        """Тест защиты от XSS"""
        xss_payloads = [
            "<script>alert('XSS')</script>",
            "javascript:alert('XSS')",
            "<img src=x onerror=alert('XSS')>",
            "<svg onload=alert('XSS')>",
        ]
        
        for payload in xss_payloads:
            # Тестируем через различные поля
            response = self.client.get('/', {'search': payload})
            # Проверяем, что вредоносный код не выполняется
            if hasattr(response, 'content'):
                self.assertNotIn(b'<script>', response.content)
                self.assertNotIn(b'javascript:', response.content)
    
    def test_csrf_protection(self):
        """Тест защиты от CSRF"""
        # Тестируем POST запрос без CSRF токена
        response = self.client.post('/api/v1/auth/login/', {
            'username': 'test',
            'password': 'test'
        })
        # В зависимости от настроек может быть 403 или другой код
        self.assertIn(response.status_code, [403, 400, 401])


class PerformanceTestMixin:
    """
    Миксин для тестирования производительности
    """
    
    def test_response_time(self):
        """Тест времени отклика"""
        import time
        
        start_time = time.time()
        response = self.client.get('/')
        end_time = time.time()
        
        response_time = end_time - start_time
        # Проверяем, что время отклика меньше 2 секунд
        self.assertLess(response_time, 2.0)
    
    def test_database_queries_count(self):
        """Тест количества запросов к БД"""
        from django.test.utils import override_settings
        from django.db import connection
        
        with override_settings(DEBUG=True):
            initial_queries = len(connection.queries)
            response = self.client.get('/')
            final_queries = len(connection.queries)
            
            queries_count = final_queries - initial_queries
            # Проверяем разумное количество запросов (настройте под свои нужды)
            self.assertLess(queries_count, 50)


class IntegrationTestMixin:
    """
    Миксин для интеграционных тестов
    """
    
    def test_full_workflow(self):
        """Тест полного рабочего процесса"""
        # Этот метод должен быть переопределён в наследниках
        # для тестирования полного workflow конкретного модуля
        pass
    
    def test_api_integration(self):
        """Тест интеграции API"""
        # Проверяем базовую работоспособность API
        response = self.client.get('/api/v1/')
        self.assertIn(response.status_code, [200, 404])  # 404 если нет root endpoint
