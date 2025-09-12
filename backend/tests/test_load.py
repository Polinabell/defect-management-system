"""
Нагрузочные тесты
"""

import time
from django.test import TestCase
from rest_framework.test import APITestCase
from rest_framework import status


class LoadTest(APITestCase):
    """Нагрузочные тесты"""
    
    def test_response_time(self):
        """Тест времени отклика"""
        start_time = time.time()
        response = self.client.get('/api/v1/health/')
        end_time = time.time()
        
        response_time = end_time - start_time
        self.assertLess(response_time, 1.0)
        self.assertEqual(response.status_code, status.HTTP_200_OK)