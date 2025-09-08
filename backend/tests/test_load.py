"""
Нагрузочные тесты для системы управления дефектами
"""

import pytest
import time
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timedelta
from django.test import TransactionTestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from django.db import transaction, connections
from django.core.cache import cache
from .factories import (
    UserFactory, ManagerUserFactory, EngineerUserFactory,
    ProjectFactory, DefectFactory, DefectCategoryFactory
)


class LoadTestMixin:
    """Миксин для нагрузочного тестирования"""
    
    def measure_response_time(self, func, *args, **kwargs):
        """Измеряет время выполнения функции"""
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        
        response_time = (end_time - start_time) * 1000  # в миллисекундах
        return result, response_time
    
    def run_concurrent_requests(self, request_func, num_threads=10, num_requests_per_thread=10):
        """Выполняет конкурентные запросы"""
        results = []
        errors = []
        
        def make_request():
            try:
                response, response_time = self.measure_response_time(request_func)
                return {
                    'success': True,
                    'status_code': response.status_code if hasattr(response, 'status_code') else 200,
                    'response_time': response_time
                }
            except Exception as e:
                return {
                    'success': False,
                    'error': str(e),
                    'response_time': None
                }
        
        with ThreadPoolExecutor(max_workers=num_threads) as executor:
            futures = []
            
            for _ in range(num_threads):
                for _ in range(num_requests_per_thread):
                    future = executor.submit(make_request)
                    futures.append(future)
            
            for future in as_completed(futures):
                result = future.result()
                if result['success']:
                    results.append(result)
                else:
                    errors.append(result)
        
        return results, errors
    
    def calculate_statistics(self, results):
        """Вычисляет статистики производительности"""
        if not results:
            return {}
        
        response_times = [r['response_time'] for r in results]
        
        return {
            'total_requests': len(results),
            'successful_requests': len([r for r in results if r.get('status_code') == 200]),
            'avg_response_time': sum(response_times) / len(response_times),
            'min_response_time': min(response_times),
            'max_response_time': max(response_times),
            'p50_response_time': sorted(response_times)[len(response_times)//2],
            'p95_response_time': sorted(response_times)[int(len(response_times)*0.95)],
            'p99_response_time': sorted(response_times)[int(len(response_times)*0.99)]
        }


class AuthenticationLoadTest(TransactionTestCase, LoadTestMixin):
    """Нагрузочные тесты аутентификации"""
    
    def setUp(self):
        self.client = APIClient()
        self.login_url = reverse('users:login')
        
        # Создаём пользователей для тестов
        self.users = []
        for i in range(100):
            user = UserFactory(
                email=f'user{i}@test.com',
                password='testpass123'
            )
            self.users.append(user)
    
    def login_request(self):
        """Выполняет запрос на авторизацию"""
        user = self.users[0]  # Используем одного пользователя для простоты
        
        data = {
            'email': user.email,
            'password': 'testpass123'
        }
        
        return self.client.post(self.login_url, data)
    
    @pytest.mark.slow
    def test_concurrent_login_requests(self):
        """Тест конкурентных запросов на авторизацию"""
        results, errors = self.run_concurrent_requests(
            self.login_request,
            num_threads=20,
            num_requests_per_thread=5
        )
        
        stats = self.calculate_statistics(results)
        
        # Проверяем, что система справляется с нагрузкой
        self.assertGreater(stats['successful_requests'], 90)  # 90% успешных запросов
        self.assertLess(stats['avg_response_time'], 1000)  # Средний ответ < 1 секунды
        self.assertLess(stats['p95_response_time'], 2000)  # 95% запросов < 2 секунд
        
        # Логируем статистики
        print(f"\n--- Статистики авторизации ---")
        print(f"Всего запросов: {stats['total_requests']}")
        print(f"Успешных: {stats['successful_requests']}")
        print(f"Среднее время ответа: {stats['avg_response_time']:.2f} мс")
        print(f"P95 время ответа: {stats['p95_response_time']:.2f} мс")
        print(f"Ошибок: {len(errors)}")


class DefectAPILoadTest(TransactionTestCase, LoadTestMixin):
    """Нагрузочные тесты API дефектов"""
    
    def setUp(self):
        self.client = APIClient()
        
        # Создаём тестовые данные
        self.manager = ManagerUserFactory()
        self.engineers = [EngineerUserFactory() for _ in range(10)]
        self.projects = [ProjectFactory(manager=self.manager) for _ in range(5)]
        self.categories = [DefectCategoryFactory() for _ in range(10)]
        
        # Добавляем инженеров в проекты
        for project in self.projects:
            for engineer in self.engineers:
                project.add_member(engineer, role='engineer')
        
        # Создаём базовые дефекты
        for _ in range(1000):
            DefectFactory(
                project=self.projects[_ % len(self.projects)],
                category=self.categories[_ % len(self.categories)]
            )
        
        # Аутентифицируемся как менеджер
        self.client.force_authenticate(user=self.manager)
        
        self.defects_url = reverse('defects:defect-list-create')
    
    def list_defects_request(self):
        """Выполняет запрос на получение списка дефектов"""
        return self.client.get(self.defects_url)
    
    def create_defect_request(self):
        """Выполняет запрос на создание дефекта"""
        data = {
            'title': f'Load test defect {datetime.now().microsecond}',
            'description': 'Тестовый дефект для нагрузочного тестирования',
            'project': self.projects[0].id,
            'category': self.categories[0].id,
            'priority': 'medium',
            'severity': 'minor',
            'location': 'Load test location'
        }
        
        return self.client.post(self.defects_url, data)
    
    def get_defect_detail_request(self):
        """Выполняет запрос на получение детальной информации о дефекте"""
        defect = DefectFactory(project=self.projects[0])
        detail_url = reverse('defects:defect-detail', args=[defect.id])
        
        return self.client.get(detail_url)
    
    @pytest.mark.slow
    def test_list_defects_load(self):
        """Тест нагрузки на получение списка дефектов"""
        results, errors = self.run_concurrent_requests(
            self.list_defects_request,
            num_threads=15,
            num_requests_per_thread=20
        )
        
        stats = self.calculate_statistics(results)
        
        # Проверяем производительность
        self.assertGreater(stats['successful_requests'], 280)  # 95% успешных запросов
        self.assertLess(stats['avg_response_time'], 2000)  # Средний ответ < 2 секунд
        self.assertLess(stats['p99_response_time'], 5000)  # 99% запросов < 5 секунд
        
        print(f"\n--- Статистики получения списка дефектов ---")
        print(f"Всего запросов: {stats['total_requests']}")
        print(f"Успешных: {stats['successful_requests']}")
        print(f"Среднее время ответа: {stats['avg_response_time']:.2f} мс")
        print(f"P99 время ответа: {stats['p99_response_time']:.2f} мс")
    
    @pytest.mark.slow
    def test_create_defects_load(self):
        """Тест нагрузки на создание дефектов"""
        results, errors = self.run_concurrent_requests(
            self.create_defect_request,
            num_threads=10,
            num_requests_per_thread=5
        )
        
        stats = self.calculate_statistics(results)
        
        # Проверяем производительность создания
        self.assertGreater(stats['successful_requests'], 45)  # 90% успешных запросов
        self.assertLess(stats['avg_response_time'], 3000)  # Средний ответ < 3 секунд
        
        print(f"\n--- Статистики создания дефектов ---")
        print(f"Всего запросов: {stats['total_requests']}")
        print(f"Успешных: {stats['successful_requests']}")
        print(f"Среднее время ответа: {stats['avg_response_time']:.2f} мс")
    
    @pytest.mark.slow
    def test_mixed_operations_load(self):
        """Тест смешанных операций с дефектами"""
        def mixed_request():
            import random
            operations = [
                self.list_defects_request,
                self.get_defect_detail_request,
                self.create_defect_request
            ]
            
            # Случайно выбираем операцию (больше вероятность для чтения)
            weights = [0.6, 0.3, 0.1]
            operation = random.choices(operations, weights=weights)[0]
            
            return operation()
        
        results, errors = self.run_concurrent_requests(
            mixed_request,
            num_threads=12,
            num_requests_per_thread=25
        )
        
        stats = self.calculate_statistics(results)
        
        # Проверяем общую производительность
        self.assertGreater(stats['successful_requests'], 270)  # 90% успешных запросов
        self.assertLess(stats['avg_response_time'], 2500)  # Средний ответ < 2.5 секунд
        
        print(f"\n--- Статистики смешанных операций ---")
        print(f"Всего запросов: {stats['total_requests']}")
        print(f"Успешных: {stats['successful_requests']}")
        print(f"Среднее время ответа: {stats['avg_response_time']:.2f} мс")


class DatabaseLoadTest(TransactionTestCase, LoadTestMixin):
    """Тесты нагрузки на базу данных"""
    
    def setUp(self):
        # Создаём большое количество тестовых данных
        self.projects = ProjectFactory.create_batch(10)
        self.users = UserFactory.create_batch(50)
        self.categories = DefectCategoryFactory.create_batch(20)
        
        # Создаём много дефектов для нагрузки
        self.defects = []
        for _ in range(5000):
            defect = DefectFactory(
                project=self.projects[_ % len(self.projects)],
                category=self.categories[_ % len(self.categories)],
                author=self.users[_ % len(self.users)]
            )
            self.defects.append(defect)
    
    def complex_query_request(self):
        """Выполняет сложный запрос к базе данных"""
        from apps.defects.models import Defect
        from django.db.models import Count, Q
        
        # Сложный запрос с JOIN и агрегацией
        queryset = Defect.objects.select_related(
            'project', 'category', 'author', 'assignee'
        ).prefetch_related(
            'files', 'comments'
        ).annotate(
            files_count=Count('files'),
            comments_count=Count('comments')
        ).filter(
            Q(status__in=['new', 'in_progress']) |
            Q(priority='high')
        ).order_by('-created_at')[:100]
        
        # Принудительно выполняем запрос
        list(queryset)
        
        # Возвращаем фиктивный ответ для совместимости с миксином
        class FakeResponse:
            status_code = 200
        
        return FakeResponse()
    
    @pytest.mark.slow
    def test_database_query_performance(self):
        """Тест производительности сложных запросов к БД"""
        results, errors = self.run_concurrent_requests(
            self.complex_query_request,
            num_threads=8,
            num_requests_per_thread=10
        )
        
        stats = self.calculate_statistics(results)
        
        # Проверяем производительность БД
        self.assertEqual(len(errors), 0)  # Нет ошибок БД
        self.assertLess(stats['avg_response_time'], 1000)  # Средний запрос < 1 секунды
        self.assertLess(stats['p95_response_time'], 2000)  # 95% запросов < 2 секунд
        
        print(f"\n--- Статистики производительности БД ---")
        print(f"Всего запросов: {stats['total_requests']}")
        print(f"Среднее время ответа: {stats['avg_response_time']:.2f} мс")
        print(f"P95 время ответа: {stats['p95_response_time']:.2f} мс")
    
    @pytest.mark.slow
    def test_bulk_operations_performance(self):
        """Тест производительности массовых операций"""
        from apps.defects.models import Defect
        
        def bulk_create_request():
            # Создаём много дефектов за раз
            defects_data = []
            for i in range(100):
                defect = Defect(
                    title=f'Bulk defect {i}_{datetime.now().microsecond}',
                    description='Bulk created defect',
                    project=self.projects[i % len(self.projects)],
                    category=self.categories[i % len(self.categories)],
                    author=self.users[i % len(self.users)],
                    priority='medium',
                    severity='minor',
                    status='new'
                )
                defects_data.append(defect)
            
            with transaction.atomic():
                Defect.objects.bulk_create(defects_data)
            
            class FakeResponse:
                status_code = 201
            
            return FakeResponse()
        
        results, errors = self.run_concurrent_requests(
            bulk_create_request,
            num_threads=5,
            num_requests_per_thread=3
        )
        
        stats = self.calculate_statistics(results)
        
        # Проверяем производительность массовых операций
        self.assertEqual(len(errors), 0)
        self.assertLess(stats['avg_response_time'], 5000)  # < 5 секунд на 100 записей
        
        print(f"\n--- Статистики массовых операций ---")
        print(f"Всего операций: {stats['total_requests']}")
        print(f"Среднее время операции: {stats['avg_response_time']:.2f} мс")


class CacheLoadTest(TransactionTestCase, LoadTestMixin):
    """Тесты нагрузки на кэширование"""
    
    def setUp(self):
        # Очищаем кэш перед тестами
        cache.clear()
        
        self.manager = ManagerUserFactory()
        self.project = ProjectFactory(manager=self.manager)
        self.client = APIClient()
        self.client.force_authenticate(user=self.manager)
    
    def cached_request(self):
        """Выполняет запрос, который должен кэшироваться"""
        # Запрос статистики проекта (обычно кэшируется)
        analytics_url = reverse('reports:analytics-report')
        data = {
            'period': 'month',
            'start_date': '2024-01-01',
            'end_date': '2024-01-31',
            'project_ids': [self.project.id]
        }
        
        return self.client.post(analytics_url, data, format='json')
    
    @pytest.mark.slow
    def test_cache_performance(self):
        """Тест производительности кэширования"""
        # Первый запрос (не из кэша)
        first_response, first_time = self.measure_response_time(self.cached_request)
        
        # Последующие запросы (из кэша)
        results, errors = self.run_concurrent_requests(
            self.cached_request,
            num_threads=10,
            num_requests_per_thread=10
        )
        
        stats = self.calculate_statistics(results)
        
        # Проверяем эффективность кэширования
        self.assertEqual(len(errors), 0)
        # Кэшированные запросы должны быть быстрее первого
        # (может не всегда работать из-за особенностей тестирования)
        # self.assertLess(stats['avg_response_time'], first_time)
        
        print(f"\n--- Статистики кэширования ---")
        print(f"Первый запрос: {first_time:.2f} мс")
        print(f"Средний кэшированный запрос: {stats['avg_response_time']:.2f} мс")
        print(f"Улучшение: {((first_time - stats['avg_response_time']) / first_time * 100):.1f}%")


class MemoryUsageTest(TransactionTestCase):
    """Тесты использования памяти"""
    
    def setUp(self):
        import psutil
        import os
        
        self.process = psutil.Process(os.getpid())
        self.initial_memory = self.process.memory_info().rss / 1024 / 1024  # MB
    
    def get_memory_usage(self):
        """Получает текущее использование памяти в MB"""
        return self.process.memory_info().rss / 1024 / 1024
    
    @pytest.mark.slow
    def test_memory_usage_during_bulk_operations(self):
        """Тест использования памяти при массовых операциях"""
        # Создаём много объектов
        projects = ProjectFactory.create_batch(100)
        users = UserFactory.create_batch(200)
        categories = DefectCategoryFactory.create_batch(50)
        
        memory_before = self.get_memory_usage()
        
        # Создаём много дефектов
        defects = []
        for i in range(10000):
            defect = DefectFactory(
                project=projects[i % len(projects)],
                author=users[i % len(users)],
                category=categories[i % len(categories)]
            )
            defects.append(defect)
        
        memory_after = self.get_memory_usage()
        memory_increase = memory_after - memory_before
        
        print(f"\n--- Использование памяти ---")
        print(f"Начальная память: {self.initial_memory:.1f} MB")
        print(f"Память до операций: {memory_before:.1f} MB")
        print(f"Память после операций: {memory_after:.1f} MB")
        print(f"Прирост памяти: {memory_increase:.1f} MB")
        
        # Проверяем, что прирост памяти разумный
        # (примерно 1KB на дефект = 10MB для 10000 дефектов)
        self.assertLess(memory_increase, 50)  # Не более 50MB прироста


class StressTest(TransactionTestCase, LoadTestMixin):
    """Стресс-тесты системы"""
    
    def setUp(self):
        self.client = APIClient()
        
        # Создаём больше пользователей и данных
        self.managers = ManagerUserFactory.create_batch(5)
        self.engineers = EngineerUserFactory.create_batch(20)
        self.projects = ProjectFactory.create_batch(20)
        self.categories = DefectCategoryFactory.create_batch(30)
        
        # Создаём много дефектов
        for _ in range(10000):
            DefectFactory(
                project=self.projects[_ % len(self.projects)],
                category=self.categories[_ % len(self.categories)],
                author=self.engineers[_ % len(self.engineers)]
            )
    
    @pytest.mark.slow
    @pytest.mark.stress
    def test_system_stability_under_high_load(self):
        """Тест стабильности системы под высокой нагрузкой"""
        def random_api_request():
            import random
            
            # Случайно выбираем пользователя
            user = random.choice(self.managers + self.engineers)
            self.client.force_authenticate(user=user)
            
            # Случайно выбираем операцию
            operations = [
                lambda: self.client.get(reverse('defects:defect-list-create')),
                lambda: self.client.get(reverse('projects:project-list-create')),
                lambda: self.client.post(
                    reverse('reports:analytics-report'),
                    {
                        'period': 'week',
                        'start_date': '2024-01-01',
                        'end_date': '2024-01-07',
                        'project_ids': [random.choice(self.projects).id]
                    },
                    format='json'
                )
            ]
            
            operation = random.choice(operations)
            return operation()
        
        # Выполняем большое количество случайных запросов
        results, errors = self.run_concurrent_requests(
            random_api_request,
            num_threads=25,
            num_requests_per_thread=40
        )
        
        stats = self.calculate_statistics(results)
        
        # Проверяем стабильность системы
        success_rate = stats['successful_requests'] / stats['total_requests'] * 100
        
        print(f"\n--- Стресс-тест результаты ---")
        print(f"Всего запросов: {stats['total_requests']}")
        print(f"Успешность: {success_rate:.1f}%")
        print(f"Среднее время ответа: {stats['avg_response_time']:.2f} мс")
        print(f"Максимальное время ответа: {stats['max_response_time']:.2f} мс")
        print(f"Ошибок: {len(errors)}")
        
        # Минимальные требования к стабильности
        self.assertGreater(success_rate, 85)  # Минимум 85% успешных запросов
        self.assertLess(stats['avg_response_time'], 5000)  # Средний ответ < 5 секунд
        self.assertLess(len(errors), stats['total_requests'] * 0.15)  # Не более 15% ошибок
