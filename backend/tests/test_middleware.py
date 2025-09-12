"""
Тесты для middleware
"""

from django.test import TestCase, RequestFactory
from django.http import HttpResponse
from django.contrib.auth import get_user_model
from apps.common.security_middleware import (
    SecurityHeadersMiddleware, RateLimitMiddleware,
    SQLInjectionProtectionMiddleware, XSSProtectionMiddleware
)

User = get_user_model()


class SecurityHeadersMiddlewareTest(TestCase):
    """Тесты для SecurityHeadersMiddleware"""
    
    def setUp(self):
        self.middleware = SecurityHeadersMiddleware(lambda r: HttpResponse())
        self.factory = RequestFactory()
    
    def test_security_headers_added(self):
        """Тест добавления заголовков безопасности"""
        request = self.factory.get('/')
        response = self.middleware.process_response(request, HttpResponse())
        
        # Проверяем заголовки безопасности
        self.assertEqual(response['X-Content-Type-Options'], 'nosniff')
        self.assertEqual(response['X-Frame-Options'], 'DENY')
        self.assertEqual(response['X-XSS-Protection'], '1; mode=block')
        self.assertEqual(response['Referrer-Policy'], 'strict-origin-when-cross-origin')
        self.assertIn('Content-Security-Policy', response)


class RateLimitMiddlewareTest(TestCase):
    """Тесты для RateLimitMiddleware"""
    
    def setUp(self):
        self.middleware = RateLimitMiddleware(lambda r: HttpResponse())
        self.factory = RequestFactory()
    
    def test_rate_limiting(self):
        """Тест ограничения частоты запросов"""
        request = self.factory.get('/')
        
        # Делаем много запросов
        for i in range(101):  # Превышаем лимит в 100
            response = self.middleware.process_request(request)
            if response:  # Если получили ответ (блокировка)
                break
        
        # Проверяем, что получили блокировку
        self.assertIsNotNone(response)
        self.assertEqual(response.status_code, 403)


class SQLInjectionProtectionMiddlewareTest(TestCase):
    """Тесты для SQLInjectionProtectionMiddleware"""
    
    def setUp(self):
        self.middleware = SQLInjectionProtectionMiddleware(lambda r: HttpResponse())
        self.factory = RequestFactory()
    
    def test_sql_injection_detection(self):
        """Тест обнаружения SQL инъекций"""
        # Тест GET параметров
        request = self.factory.get('/', {'q': "'; DROP TABLE users; --"})
        response = self.middleware.process_request(request)
        self.assertIsNotNone(response)
        self.assertEqual(response.status_code, 403)
        
        # Тест POST параметров
        request = self.factory.post('/', {'title': "1' OR '1'='1"})
        response = self.middleware.process_request(request)
        self.assertIsNotNone(response)
        self.assertEqual(response.status_code, 403)
    
    def test_legitimate_requests(self):
        """Тест легитимных запросов"""
        # Обычный GET запрос
        request = self.factory.get('/', {'q': 'обычный поиск'})
        response = self.middleware.process_request(request)
        self.assertIsNone(response)  # Должен пройти
        
        # Обычный POST запрос
        request = self.factory.post('/', {'title': 'Обычный заголовок'})
        response = self.middleware.process_request(request)
        self.assertIsNone(response)  # Должен пройти


class XSSProtectionMiddlewareTest(TestCase):
    """Тесты для XSSProtectionMiddleware"""
    
    def setUp(self):
        self.middleware = XSSProtectionMiddleware(lambda r: HttpResponse())
        self.factory = RequestFactory()
    
    def test_xss_detection(self):
        """Тест обнаружения XSS атак"""
        # Тест GET параметров
        request = self.factory.get('/', {'q': '<script>alert("XSS")</script>'})
        response = self.middleware.process_request(request)
        self.assertIsNotNone(response)
        self.assertEqual(response.status_code, 403)
        
        # Тест POST параметров
        request = self.factory.post('/', {'title': '<iframe src="malicious.com"></iframe>'})
        response = self.middleware.process_request(request)
        self.assertIsNotNone(response)
        self.assertEqual(response.status_code, 403)
    
    def test_legitimate_html(self):
        """Тест легитимного HTML"""
        # Обычный HTML
        request = self.factory.post('/', {'content': '<p>Обычный текст</p>'})
        response = self.middleware.process_request(request)
        self.assertIsNone(response)  # Должен пройти
        
        # Простые теги
        request = self.factory.post('/', {'content': '<b>Жирный текст</b>'})
        response = self.middleware.process_request(request)
        self.assertIsNone(response)  # Должен пройти
