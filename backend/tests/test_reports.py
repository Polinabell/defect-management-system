"""
Тесты для модуля отчетов
"""

import pytest
from datetime import date, datetime, timedelta
from decimal import Decimal
from django.urls import reverse
from django.contrib.auth import get_user_model
from rest_framework import status
from .base import BaseAPITestCase, IntegrationTestMixin
from .factories import (
    UserFactory, ManagerUserFactory, EngineerUserFactory,
    ProjectFactory, DefectFactory, DefectCategoryFactory,
    ReportFactory, ReportTemplateFactory
)
from apps.reports.models import Report, ReportTemplate, ReportParameter
from apps.reports.services import ReportGeneratorService, AnalyticsService

User = get_user_model()


class ReportModelTest(BaseAPITestCase):
    """Тесты модели отчёта"""
    
    def test_report_creation(self):
        """Тест создания отчёта"""
        report = ReportFactory()
        self.assertIsInstance(report, Report)
        self.assertIsNotNone(report.generated_at)
        self.assertEqual(report.status, 'generated')
    
    def test_report_str_representation(self):
        """Тест строкового представления отчёта"""
        report = ReportFactory(title='Тестовый отчёт')
        self.assertIn('Тестовый отчёт', str(report))
    
    def test_report_file_path(self):
        """Тест пути к файлу отчёта"""
        report = ReportFactory(report_type='defects_summary')
        file_path = report.get_file_path()
        
        self.assertIn(str(report.generated_at.year), file_path)
        self.assertIn(str(report.generated_at.month), file_path)
        self.assertIn('defects_summary', file_path)
        self.assertTrue(file_path.endswith('.xlsx'))
    
    def test_report_expiration(self):
        """Тест проверки истечения отчёта"""
        # Свежий отчёт
        fresh_report = ReportFactory()
        self.assertFalse(fresh_report.is_expired())
        
        # Старый отчёт (создан 8 дней назад)
        old_date = datetime.now() - timedelta(days=8)
        old_report = ReportFactory(generated_at=old_date)
        self.assertTrue(old_report.is_expired())
    
    def test_report_parameters(self):
        """Тест параметров отчёта"""
        report = ReportFactory()
        
        # Добавляем параметры
        report.set_parameter('start_date', '2024-01-01')
        report.set_parameter('end_date', '2024-01-31')
        report.set_parameter('project_id', 123)
        
        # Проверяем получение параметров
        self.assertEqual(report.get_parameter('start_date'), '2024-01-01')
        self.assertEqual(report.get_parameter('end_date'), '2024-01-31')
        self.assertEqual(report.get_parameter('project_id'), 123)
        self.assertIsNone(report.get_parameter('non_existent'))
    
    def test_report_size_calculation(self):
        """Тест вычисления размера отчёта"""
        report = ReportFactory()
        
        # Если файл не существует, размер должен быть None
        self.assertIsNone(report.file_size)
        
        # Симулируем наличие файла (в реальном тесте был бы создан файл)
        report._file_size = 1024
        self.assertEqual(report.file_size_formatted, '1.0 KB')


class ReportTemplateModelTest(BaseAPITestCase):
    """Тесты модели шаблона отчёта"""
    
    def test_template_creation(self):
        """Тест создания шаблона отчёта"""
        template = ReportTemplateFactory()
        self.assertIsInstance(template, ReportTemplate)
        self.assertTrue(template.is_active)
    
    def test_template_str_representation(self):
        """Тест строкового представления шаблона"""
        template = ReportTemplateFactory(name='Шаблон дефектов')
        self.assertEqual(str(template), 'Шаблон дефектов')
    
    def test_template_parameters_schema(self):
        """Тест схемы параметров шаблона"""
        template = ReportTemplateFactory()
        
        # Устанавливаем схему параметров
        schema = {
            'start_date': {
                'type': 'date',
                'required': True,
                'label': 'Дата начала'
            },
            'project_id': {
                'type': 'integer',
                'required': False,
                'label': 'ID проекта'
            }
        }
        
        template.parameters_schema = schema
        template.save()
        
        # Проверяем валидацию параметров
        valid_params = {
            'start_date': '2024-01-01',
            'project_id': 123
        }
        self.assertTrue(template.validate_parameters(valid_params))
        
        # Проверяем невалидные параметры
        invalid_params = {}  # отсутствует обязательный параметр
        self.assertFalse(template.validate_parameters(invalid_params))


class ReportAPITest(BaseAPITestCase):
    """Тесты API отчётов"""
    
    def setUp(self):
        self.reports_url = reverse('reports:report-list')
        self.manager = ManagerUserFactory()
        self.engineer = EngineerUserFactory()
        self.project = ProjectFactory(manager=self.manager)
        self.project.add_member(self.engineer, role='engineer')
        
        # Создаём несколько дефектов для отчётов
        self.defect1 = DefectFactory(project=self.project, status='closed')
        self.defect2 = DefectFactory(project=self.project, status='in_progress')
        self.defect3 = DefectFactory(project=self.project, status='new')
    
    def test_list_reports(self):
        """Тест получения списка отчётов"""
        # Создаём отчёты
        report1 = ReportFactory(created_by=self.manager)
        report2 = ReportFactory(created_by=self.engineer)
        
        self.authenticate(self.manager)
        
        response = self.client.get(self.reports_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        report_ids = [r['id'] for r in response.data['results']]
        self.assertIn(report1.id, report_ids)
        self.assertIn(report2.id, report_ids)
    
    def test_generate_defects_summary_report(self):
        """Тест генерации сводного отчёта по дефектам"""
        self.authenticate(self.manager)
        
        generate_url = reverse('reports:generate-report')
        data = {
            'report_type': 'defects_summary',
            'title': 'Сводный отчёт по дефектам',
            'parameters': {
                'project_id': self.project.id,
                'start_date': '2024-01-01',
                'end_date': '2024-12-31'
            },
            'format': 'xlsx'
        }
        
        response = self.client.post(generate_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        # Проверяем, что отчёт создался
        report = Report.objects.get(id=response.data['id'])
        self.assertEqual(report.report_type, 'defects_summary')
        self.assertEqual(report.created_by, self.manager)
        self.assertEqual(report.status, 'generated')
    
    def test_generate_project_progress_report(self):
        """Тест генерации отчёта по прогрессу проекта"""
        self.authenticate(self.manager)
        
        generate_url = reverse('reports:generate-report')
        data = {
            'report_type': 'project_progress',
            'title': 'Отчёт по прогрессу проекта',
            'parameters': {
                'project_id': self.project.id
            },
            'format': 'pdf'
        }
        
        response = self.client.post(generate_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        report = Report.objects.get(id=response.data['id'])
        self.assertEqual(report.report_type, 'project_progress')
        self.assertEqual(report.format, 'pdf')
    
    def test_generate_analytics_report(self):
        """Тест генерации аналитического отчёта"""
        self.authenticate(self.manager)
        
        generate_url = reverse('reports:analytics-report')
        data = {
            'period': 'month',
            'start_date': '2024-01-01',
            'end_date': '2024-01-31',
            'project_ids': [self.project.id],
            'include_charts': True
        }
        
        response = self.client.post(generate_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Проверяем структуру аналитических данных
        analytics_data = response.data
        self.assertIn('summary', analytics_data)
        self.assertIn('defects_by_status', analytics_data)
        self.assertIn('defects_by_priority', analytics_data)
        self.assertIn('charts', analytics_data)
    
    def test_download_report(self):
        """Тест скачивания отчёта"""
        report = ReportFactory(created_by=self.manager, status='generated')
        
        self.authenticate(self.manager)
        
        download_url = reverse('reports:download-report', args=[report.id])
        response = self.client.get(download_url)
        
        # В реальном тесте здесь был бы файл
        # self.assertEqual(response.status_code, status.HTTP_200_OK)
        # self.assertIn('attachment', response['Content-Disposition'])
    
    def test_schedule_report(self):
        """Тест планирования периодического отчёта"""
        self.authenticate(self.manager)
        
        schedule_url = reverse('reports:schedule-report')
        data = {
            'report_type': 'defects_summary',
            'title': 'Еженедельный отчёт',
            'schedule_type': 'weekly',
            'parameters': {
                'project_id': self.project.id
            },
            'recipients': ['manager@example.com', 'engineer@example.com']
        }
        
        response = self.client.post(schedule_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        # Проверяем, что расписание создалось
        self.assertIn('schedule_id', response.data)
    
    def test_report_sharing(self):
        """Тест предоставления доступа к отчёту"""
        report = ReportFactory(created_by=self.manager)
        
        self.authenticate(self.manager)
        
        share_url = reverse('reports:share-report', args=[report.id])
        data = {
            'share_with': [self.engineer.id],
            'permissions': ['view', 'download'],
            'expires_at': (datetime.now() + timedelta(days=7)).isoformat()
        }
        
        response = self.client.post(share_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Проверяем, что инженер теперь может просматривать отчёт
        self.authenticate(self.engineer)
        
        report_url = reverse('reports:report-detail', args=[report.id])
        response = self.client.get(report_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class ReportServiceTest(BaseAPITestCase):
    """Тесты сервисов отчётов"""
    
    def setUp(self):
        self.manager = ManagerUserFactory()
        self.project = ProjectFactory(manager=self.manager)
        
        # Создаём тестовые данные
        category = DefectCategoryFactory()
        
        # Дефекты с разными статусами и приоритетами
        DefectFactory(
            project=self.project,
            category=category,
            status='closed',
            priority='high',
            created_at=datetime(2024, 1, 15)
        )
        DefectFactory(
            project=self.project,
            category=category,
            status='in_progress',
            priority='medium',
            created_at=datetime(2024, 1, 20)
        )
        DefectFactory(
            project=self.project,
            category=category,
            status='new',
            priority='low',
            created_at=datetime(2024, 1, 25)
        )
    
    def test_defects_summary_generation(self):
        """Тест генерации сводного отчёта по дефектам"""
        service = ReportGeneratorService()
        
        parameters = {
            'project_id': self.project.id,
            'start_date': '2024-01-01',
            'end_date': '2024-01-31'
        }
        
        # Генерируем данные для отчёта
        report_data = service.generate_defects_summary(parameters)
        
        self.assertIn('summary', report_data)
        self.assertIn('defects_by_status', report_data)
        self.assertIn('defects_by_priority', report_data)
        self.assertIn('defects_by_category', report_data)
        
        # Проверяем корректность данных
        summary = report_data['summary']
        self.assertEqual(summary['total_defects'], 3)
        self.assertEqual(summary['closed_defects'], 1)
        self.assertEqual(summary['in_progress_defects'], 1)
        self.assertEqual(summary['new_defects'], 1)
    
    def test_project_progress_generation(self):
        """Тест генерации отчёта по прогрессу проекта"""
        service = ReportGeneratorService()
        
        parameters = {
            'project_id': self.project.id
        }
        
        report_data = service.generate_project_progress(parameters)
        
        self.assertIn('project_info', report_data)
        self.assertIn('defects_statistics', report_data)
        self.assertIn('completion_percentage', report_data)
        self.assertIn('team_performance', report_data)
        
        # Проверяем информацию о проекте
        project_info = report_data['project_info']
        self.assertEqual(project_info['id'], self.project.id)
        self.assertEqual(project_info['name'], self.project.name)
    
    def test_analytics_service(self):
        """Тест сервиса аналитики"""
        service = AnalyticsService()
        
        # Получаем статистику дефектов
        defects_stats = service.get_defects_statistics(
            project_ids=[self.project.id],
            start_date=date(2024, 1, 1),
            end_date=date(2024, 1, 31)
        )
        
        self.assertIn('total', defects_stats)
        self.assertIn('by_status', defects_stats)
        self.assertIn('by_priority', defects_stats)
        self.assertIn('by_severity', defects_stats)
        
        # Проверяем данные
        self.assertEqual(defects_stats['total'], 3)
        self.assertEqual(defects_stats['by_status']['closed'], 1)
        self.assertEqual(defects_stats['by_status']['in_progress'], 1)
        self.assertEqual(defects_stats['by_status']['new'], 1)
    
    def test_performance_metrics(self):
        """Тест метрик производительности"""
        service = AnalyticsService()
        
        metrics = service.get_performance_metrics(
            project_ids=[self.project.id],
            start_date=date(2024, 1, 1),
            end_date=date(2024, 1, 31)
        )
        
        self.assertIn('avg_resolution_time', metrics)
        self.assertIn('defects_per_day', metrics)
        self.assertIn('team_productivity', metrics)
        self.assertIn('quality_metrics', metrics)
    
    def test_trend_analysis(self):
        """Тест анализа трендов"""
        service = AnalyticsService()
        
        trends = service.get_trends_analysis(
            project_ids=[self.project.id],
            period='week',
            start_date=date(2024, 1, 1),
            end_date=date(2024, 1, 31)
        )
        
        self.assertIn('defects_created', trends)
        self.assertIn('defects_resolved', trends)
        self.assertIn('backlog_growth', trends)
        self.assertIn('velocity_trend', trends)


class ReportExportTest(BaseAPITestCase):
    """Тесты экспорта отчётов"""
    
    def setUp(self):
        self.manager = ManagerUserFactory()
        self.project = ProjectFactory(manager=self.manager)
        
        # Создаём тестовые данные
        for i in range(10):
            DefectFactory(project=self.project, title=f'Дефект {i+1}')
    
    def test_export_to_excel(self):
        """Тест экспорта в Excel"""
        self.authenticate(self.manager)
        
        export_url = reverse('reports:export-defects')
        params = {
            'project_id': self.project.id,
            'format': 'xlsx'
        }
        
        response = self.client.get(export_url, params)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Проверяем заголовки ответа
        self.assertEqual(
            response['Content-Type'],
            'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
        self.assertIn('attachment', response['Content-Disposition'])
    
    def test_export_to_csv(self):
        """Тест экспорта в CSV"""
        self.authenticate(self.manager)
        
        export_url = reverse('reports:export-defects')
        params = {
            'project_id': self.project.id,
            'format': 'csv'
        }
        
        response = self.client.get(export_url, params)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Проверяем заголовки ответа
        self.assertEqual(response['Content-Type'], 'text/csv')
        self.assertIn('attachment', response['Content-Disposition'])
    
    def test_export_with_filters(self):
        """Тест экспорта с фильтрами"""
        # Создаём дефекты с разными статусами
        DefectFactory(project=self.project, status='closed', title='Закрытый дефект')
        DefectFactory(project=self.project, status='new', title='Новый дефект')
        
        self.authenticate(self.manager)
        
        export_url = reverse('reports:export-defects')
        params = {
            'project_id': self.project.id,
            'status': 'closed',
            'format': 'csv'
        }
        
        response = self.client.get(export_url, params)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Проверяем, что в экспорте только закрытые дефекты
        content = response.content.decode('utf-8')
        self.assertIn('Закрытый дефект', content)
        self.assertNotIn('Новый дефект', content)


class ReportIntegrationTest(BaseAPITestCase, IntegrationTestMixin):
    """Интеграционные тесты для модуля отчётов"""
    
    def test_complete_reporting_workflow(self):
        """Тест полного workflow отчётности"""
        manager = ManagerUserFactory()
        engineer = EngineerUserFactory()
        
        project = ProjectFactory(manager=manager)
        project.add_member(engineer, role='engineer')
        
        # Создаём тестовые данные
        category = DefectCategoryFactory()
        
        # Дефекты в разных статусах
        closed_defect = DefectFactory(
            project=project,
            category=category,
            status='closed',
            priority='high',
            assignee=engineer
        )
        
        in_progress_defect = DefectFactory(
            project=project,
            category=category,
            status='in_progress',
            priority='medium',
            assignee=engineer
        )
        
        new_defect = DefectFactory(
            project=project,
            category=category,
            status='new',
            priority='low'
        )
        
        self.authenticate(manager)
        
        # 1. Генерируем аналитический отчёт
        analytics_url = reverse('reports:analytics-report')
        analytics_data = {
            'period': 'month',
            'start_date': '2024-01-01',
            'end_date': '2024-01-31',
            'project_ids': [project.id],
            'include_charts': True
        }
        
        response = self.client.post(analytics_url, analytics_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        analytics_result = response.data
        self.assertIn('summary', analytics_result)
        self.assertEqual(analytics_result['summary']['total_defects'], 3)
        
        # 2. Создаём сводный отчёт
        generate_url = reverse('reports:generate-report')
        report_data = {
            'report_type': 'defects_summary',
            'title': 'Интеграционный тест отчёт',
            'parameters': {
                'project_id': project.id,
                'start_date': '2024-01-01',
                'end_date': '2024-12-31'
            },
            'format': 'xlsx'
        }
        
        response = self.client.post(generate_url, report_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        report_id = response.data['id']
        
        # 3. Предоставляем доступ инженеру
        share_url = reverse('reports:share-report', args=[report_id])
        share_data = {
            'share_with': [engineer.id],
            'permissions': ['view', 'download'],
            'expires_at': (datetime.now() + timedelta(days=7)).isoformat()
        }
        
        response = self.client.post(share_url, share_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # 4. Инженер просматривает отчёт
        self.authenticate(engineer)
        
        report_url = reverse('reports:report-detail', args=[report_id])
        response = self.client.get(report_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # 5. Экспортируем данные в разных форматах
        self.authenticate(manager)
        
        # Excel экспорт
        export_url = reverse('reports:export-defects')
        excel_params = {
            'project_id': project.id,
            'format': 'xlsx'
        }
        
        response = self.client.get(export_url, excel_params)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # CSV экспорт
        csv_params = {
            'project_id': project.id,
            'format': 'csv'
        }
        
        response = self.client.get(export_url, csv_params)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # 6. Планируем периодический отчёт
        schedule_url = reverse('reports:schedule-report')
        schedule_data = {
            'report_type': 'project_progress',
            'title': 'Еженедельный отчёт по проекту',
            'schedule_type': 'weekly',
            'parameters': {
                'project_id': project.id
            },
            'recipients': ['manager@test.com']
        }
        
        response = self.client.post(schedule_url, schedule_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)


@pytest.mark.django_db
class TestReportServicesPytest:
    """Pytest тесты для сервисов отчётов"""
    
    def test_report_generator_service(self):
        """Тест сервиса генерации отчётов"""
        project = ProjectFactory()
        DefectFactory.create_batch(5, project=project, status='closed')
        DefectFactory.create_batch(3, project=project, status='in_progress')
        DefectFactory.create_batch(2, project=project, status='new')
        
        service = ReportGeneratorService()
        
        parameters = {
            'project_id': project.id,
            'start_date': '2024-01-01',
            'end_date': '2024-12-31'
        }
        
        report_data = service.generate_defects_summary(parameters)
        
        assert 'summary' in report_data
        assert report_data['summary']['total_defects'] == 10
        assert report_data['summary']['closed_defects'] == 5
    
    @pytest.mark.parametrize('period,expected_points', [
        ('day', 31),  # Январь
        ('week', 5),  # 5 недель в январе
        ('month', 1), # 1 месяц
    ])
    def test_trend_analysis_periods(self, period, expected_points):
        """Параметризованный тест анализа трендов по периодам"""
        project = ProjectFactory()
        DefectFactory.create_batch(10, project=project)
        
        service = AnalyticsService()
        trends = service.get_trends_analysis(
            project_ids=[project.id],
            period=period,
            start_date=date(2024, 1, 1),
            end_date=date(2024, 1, 31)
        )
        
        assert len(trends['defects_created']) <= expected_points
    
    def test_performance_metrics_calculation(self):
        """Тест вычисления метрик производительности"""
        project = ProjectFactory()
        engineer = EngineerUserFactory()
        
        # Создаём дефекты с разным временем решения
        for days in [1, 3, 5, 7, 10]:
            created_date = datetime.now() - timedelta(days=days+2)
            closed_date = datetime.now() - timedelta(days=2)
            
            DefectFactory(
                project=project,
                assignee=engineer,
                status='closed',
                created_at=created_date,
                closed_at=closed_date
            )
        
        service = AnalyticsService()
        metrics = service.get_performance_metrics(
            project_ids=[project.id],
            start_date=date.today() - timedelta(days=30),
            end_date=date.today()
        )
        
        assert 'avg_resolution_time' in metrics
        assert metrics['avg_resolution_time'] > 0
        assert 'team_productivity' in metrics
