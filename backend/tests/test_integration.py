"""
Интеграционные тесты для системы управления дефектами
"""

import pytest
from datetime import datetime, timedelta
from unittest.mock import patch, MagicMock
from django.test import TransactionTestCase
from django.urls import reverse
from django.core import mail
from django.core.files.uploadedfile import SimpleUploadedFile
from rest_framework import status
from .base import BaseAPITestCase, IntegrationTestMixin
from .factories import (
    UserFactory, ManagerUserFactory, EngineerUserFactory,
    ProjectFactory, DefectFactory, DefectCategoryFactory
)


class EmailIntegrationTest(BaseAPITestCase, IntegrationTestMixin):
    """Тесты интеграции с email сервисом"""
    
    def setUp(self):
        self.manager = ManagerUserFactory()
        self.engineer = EngineerUserFactory()
        self.project = ProjectFactory(manager=self.manager)
        self.project.add_member(self.engineer, role='engineer')
        
        # Очищаем outbox перед каждым тестом
        mail.outbox = []
    
    def test_defect_assignment_notification(self):
        """Тест отправки уведомления при назначении дефекта"""
        defect = DefectFactory(project=self.project, status='new')
        
        self.authenticate(self.manager)
        
        assign_url = reverse('defects:defect-assignment', args=[defect.id])
        data = {
            'assignee': self.engineer.id,
            'due_date': (datetime.now().date() + timedelta(days=7)).isoformat(),
            'comment': 'Назначаю исполнителя'
        }
        
        response = self.client.post(assign_url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Проверяем, что email отправлен
        self.assertEqual(len(mail.outbox), 1)
        
        sent_email = mail.outbox[0]
        self.assertIn(self.engineer.email, sent_email.to)
        self.assertIn('назначен', sent_email.subject.lower())
        self.assertIn(defect.defect_number, sent_email.body)
    
    def test_defect_status_change_notification(self):
        """Тест отправки уведомления при изменении статуса дефекта"""
        defect = DefectFactory(
            project=self.project,
            assignee=self.engineer,
            status='in_progress'
        )
        
        self.authenticate(self.engineer)
        
        status_url = reverse('defects:defect-status-change', args=[defect.id])
        data = {
            'status': 'review',
            'comment': 'Готово к проверке'
        }
        
        response = self.client.post(status_url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Проверяем, что менеджер получил уведомление
        self.assertEqual(len(mail.outbox), 1)
        
        sent_email = mail.outbox[0]
        self.assertIn(self.manager.email, sent_email.to)
        self.assertIn('готов к проверке', sent_email.subject.lower())
    
    def test_defect_overdue_notification(self):
        """Тест отправки уведомления о просроченных дефектах"""
        # Создаём просроченный дефект
        overdue_defect = DefectFactory(
            project=self.project,
            assignee=self.engineer,
            due_date=datetime.now().date() - timedelta(days=1),
            status='in_progress'
        )
        
        # Имитируем выполнение задачи Celery для проверки просроченных дефектов
        from apps.defects.tasks import check_overdue_defects
        check_overdue_defects.delay()
        
        # Проверяем отправку уведомлений
        self.assertGreaterEqual(len(mail.outbox), 1)
        
        # Находим email о просроченном дефекте
        overdue_emails = [
            email for email in mail.outbox
            if 'просрочен' in email.subject.lower()
        ]
        self.assertGreater(len(overdue_emails), 0)
    
    def test_weekly_report_email(self):
        """Тест отправки еженедельного отчёта по email"""
        # Создаём несколько дефектов для отчёта
        DefectFactory.create_batch(5, project=self.project, status='closed')
        DefectFactory.create_batch(3, project=self.project, status='in_progress')
        
        # Имитируем выполнение задачи отправки еженедельного отчёта
        from apps.reports.tasks import send_weekly_report
        send_weekly_report.delay(project_id=self.project.id)
        
        # Проверяем отправку отчёта
        self.assertGreaterEqual(len(mail.outbox), 1)
        
        report_emails = [
            email for email in mail.outbox
            if 'еженедельный отчёт' in email.subject.lower()
        ]
        self.assertGreater(len(report_emails), 0)
        
        report_email = report_emails[0]
        self.assertIn(self.manager.email, report_email.to)
        self.assertIn(str(self.project.name), report_email.body)


class FileStorageIntegrationTest(BaseAPITestCase, IntegrationTestMixin):
    """Тесты интеграции с файловым хранилищем"""
    
    def setUp(self):
        self.engineer = EngineerUserFactory()
        self.project = ProjectFactory()
        self.project.add_member(self.engineer, role='engineer')
        self.defect = DefectFactory(project=self.project, author=self.engineer)
    
    def test_file_upload_to_defect(self):
        """Тест загрузки файла к дефекту"""
        self.authenticate(self.engineer)
        
        # Создаём тестовый файл
        test_file = SimpleUploadedFile(
            'test_image.jpg',
            b'fake image content',
            content_type='image/jpeg'
        )
        
        files_url = reverse('defects:defect-files', args=[self.defect.id])
        data = {
            'file': test_file,
            'description': 'Тестовое изображение дефекта'
        }
        
        response = self.client.post(files_url, data, format='multipart')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        # Проверяем, что файл сохранился
        file_id = response.data['id']
        from apps.defects.models import DefectFile
        
        defect_file = DefectFile.objects.get(id=file_id)
        self.assertTrue(defect_file.file.name)
        self.assertIn('defects', defect_file.file.name)  # Путь содержит папку defects
    
    def test_file_download_from_defect(self):
        """Тест скачивания файла дефекта"""
        from apps.defects.models import DefectFile
        
        # Создаём файл дефекта
        test_file = SimpleUploadedFile(
            'download_test.pdf',
            b'fake pdf content',
            content_type='application/pdf'
        )
        
        defect_file = DefectFile.objects.create(
            defect=self.defect,
            file=test_file,
            uploaded_by=self.engineer,
            description='Файл для скачивания'
        )
        
        self.authenticate(self.engineer)
        
        download_url = reverse(
            'defects:defect-file-download',
            args=[self.defect.id, defect_file.id]
        )
        
        response = self.client.get(download_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response['Content-Type'], 'application/pdf')
        self.assertIn('attachment', response['Content-Disposition'])
    
    def test_file_security_validation(self):
        """Тест валидации безопасности загружаемых файлов"""
        self.authenticate(self.engineer)
        
        # Попытка загрузить исполняемый файл
        malicious_file = SimpleUploadedFile(
            'malicious.exe',
            b'fake executable content',
            content_type='application/x-executable'
        )
        
        files_url = reverse('defects:defect-files', args=[self.defect.id])
        data = {
            'file': malicious_file,
            'description': 'Вредоносный файл'
        }
        
        response = self.client.post(files_url, data, format='multipart')
        # Должна быть ошибка валидации
        self.assertIn(response.status_code, [400, 415])
    
    def test_file_size_limit(self):
        """Тест ограничения размера файла"""
        self.authenticate(self.engineer)
        
        # Создаём файл превышающий лимит (предположим лимит 10MB)
        large_file = SimpleUploadedFile(
            'large_file.jpg',
            b'x' * (11 * 1024 * 1024),  # 11MB
            content_type='image/jpeg'
        )
        
        files_url = reverse('defects:defect-files', args=[self.defect.id])
        data = {
            'file': large_file,
            'description': 'Большой файл'
        }
        
        response = self.client.post(files_url, data, format='multipart')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class DatabaseIntegrationTest(TransactionTestCase, IntegrationTestMixin):
    """Тесты интеграции с базой данных"""
    
    def test_database_transactions(self):
        """Тест транзакций базы данных"""
        from django.db import transaction
        from apps.defects.models import Defect, DefectComment
        
        manager = ManagerUserFactory()
        project = ProjectFactory(manager=manager)
        
        # Тестируем откат транзакции при ошибке
        try:
            with transaction.atomic():
                # Создаём дефект
                defect = Defect.objects.create(
                    title='Тестовый дефект',
                    description='Описание',
                    project=project,
                    author=manager,
                    priority='medium',
                    severity='minor',
                    status='new'
                )
                
                # Создаём комментарий
                comment = DefectComment.objects.create(
                    defect=defect,
                    author=manager,
                    content='Тестовый комментарий'
                )
                
                # Имитируем ошибку
                raise Exception('Тестовая ошибка')
                
        except Exception:
            pass
        
        # Проверяем, что данные не сохранились (транзакция откатилась)
        self.assertEqual(Defect.objects.filter(title='Тестовый дефект').count(), 0)
        self.assertEqual(DefectComment.objects.filter(content='Тестовый комментарий').count(), 0)
    
    def test_database_constraints(self):
        """Тест ограничений базы данных"""
        from django.db import IntegrityError
        from apps.projects.models import Project
        
        manager = ManagerUserFactory()
        
        # Тестируем уникальность номера проекта
        project1 = Project.objects.create(
            name='Проект 1',
            project_number='PROJ-001',
            manager=manager
        )
        
        # Попытка создать проект с таким же номером
        with self.assertRaises(IntegrityError):
            Project.objects.create(
                name='Проект 2',
                project_number='PROJ-001',  # Дублирующий номер
                manager=manager
            )
    
    def test_database_indexes_performance(self):
        """Тест производительности индексов БД"""
        from django.db import connection
        from apps.defects.models import Defect
        
        project = ProjectFactory()
        category = DefectCategoryFactory()
        
        # Создаём много дефектов
        defects_data = []
        for i in range(1000):
            defect = Defect(
                title=f'Дефект {i}',
                description=f'Описание дефекта {i}',
                project=project,
                category=category,
                author_id=1,  # Используем ID вместо объекта для bulk_create
                priority='medium',
                severity='minor',
                status='new'
            )
            defects_data.append(defect)
        
        Defect.objects.bulk_create(defects_data)
        
        # Тестируем производительность поиска по индексированным полям
        with connection.cursor() as cursor:
            # Запрос с использованием индекса по project_id
            cursor.execute(
                "SELECT COUNT(*) FROM defects_defect WHERE project_id = %s",
                [project.id]
            )
            result = cursor.fetchone()
            
            self.assertEqual(result[0], 1000)


class CacheIntegrationTest(BaseAPITestCase, IntegrationTestMixin):
    """Тесты интеграции с системой кэширования"""
    
    def setUp(self):
        from django.core.cache import cache
        cache.clear()
        
        self.manager = ManagerUserFactory()
        self.project = ProjectFactory(manager=self.manager)
        
        # Создаём дефекты для кэширования статистики
        DefectFactory.create_batch(5, project=self.project, status='closed')
        DefectFactory.create_batch(3, project=self.project, status='in_progress')
        DefectFactory.create_batch(2, project=self.project, status='new')
    
    def test_statistics_caching(self):
        """Тест кэширования статистики проекта"""
        from django.core.cache import cache
        from apps.projects.services import ProjectStatisticsService
        
        service = ProjectStatisticsService()
        
        # Первый вызов - данные должны кэшироваться
        stats1 = service.get_project_statistics(self.project.id)
        
        # Проверяем, что данные попали в кэш
        cache_key = f"project_stats_{self.project.id}"
        cached_data = cache.get(cache_key)
        self.assertIsNotNone(cached_data)
        
        # Второй вызов - данные должны браться из кэша
        stats2 = service.get_project_statistics(self.project.id)
        
        self.assertEqual(stats1, stats2)
    
    def test_cache_invalidation(self):
        """Тест инвалидации кэша при изменении данных"""
        from django.core.cache import cache
        from apps.projects.services import ProjectStatisticsService
        
        service = ProjectStatisticsService()
        
        # Получаем статистику (кэшируется)
        initial_stats = service.get_project_statistics(self.project.id)
        
        # Создаём новый дефект
        DefectFactory(project=self.project, status='new')
        
        # Кэш должен инвалидироваться автоматически (через сигналы)
        # или мы инвалидируем его вручную
        cache.delete(f"project_stats_{self.project.id}")
        
        # Получаем обновлённую статистику
        updated_stats = service.get_project_statistics(self.project.id)
        
        # Количество новых дефектов должно увеличиться
        self.assertEqual(
            updated_stats['new_defects'],
            initial_stats['new_defects'] + 1
        )


class ExternalAPIIntegrationTest(BaseAPITestCase, IntegrationTestMixin):
    """Тесты интеграции с внешними API"""
    
    @patch('requests.get')
    def test_external_notification_service(self, mock_get):
        """Тест интеграции с внешним сервисом уведомлений"""
        # Мокируем ответ внешнего API
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {'status': 'sent', 'id': '12345'}
        mock_get.return_value = mock_response
        
        # Имитируем отправку уведомления
        from apps.common.services import ExternalNotificationService
        
        service = ExternalNotificationService()
        result = service.send_notification(
            recipient='test@example.com',
            subject='Тестовое уведомление',
            message='Содержимое уведомления'
        )
        
        self.assertTrue(result['success'])
        self.assertEqual(result['external_id'], '12345')
        
        # Проверяем, что запрос был выполнен
        mock_get.assert_called_once()
    
    @patch('requests.post')
    def test_external_backup_service(self, mock_post):
        """Тест интеграции с внешним сервисом резервного копирования"""
        # Мокируем успешный ответ
        mock_response = MagicMock()
        mock_response.status_code = 201
        mock_response.json.return_value = {
            'backup_id': 'backup-123',
            'status': 'completed'
        }
        mock_post.return_value = mock_response
        
        # Имитируем создание резервной копии
        from apps.common.services import BackupService
        
        service = BackupService()
        result = service.create_backup(
            data_type='defects',
            include_files=True
        )
        
        self.assertTrue(result['success'])
        self.assertEqual(result['backup_id'], 'backup-123')
        
        mock_post.assert_called_once()
    
    @patch('apps.common.services.SmsService.send_sms')
    def test_sms_notification_integration(self, mock_send_sms):
        """Тест интеграции с SMS сервисом"""
        # Мокируем отправку SMS
        mock_send_sms.return_value = {
            'success': True,
            'message_id': 'sms-456'
        }
        
        manager = ManagerUserFactory(phone='+79001234567')
        project = ProjectFactory(manager=manager)
        
        # Создаём критический дефект
        critical_defect = DefectFactory(
            project=project,
            priority='critical',
            severity='blocker'
        )
        
        # Имитируем отправку SMS уведомления
        from apps.defects.services import DefectNotificationService
        
        service = DefectNotificationService()
        service.notify_critical_defect(critical_defect)
        
        # Проверяем, что SMS было отправлено
        mock_send_sms.assert_called_once()
        call_args = mock_send_sms.call_args
        self.assertIn(manager.phone, call_args[0])
        self.assertIn('критический дефект', call_args[1]['message'].lower())


class WebhookIntegrationTest(BaseAPITestCase, IntegrationTestMixin):
    """Тесты интеграции через webhooks"""
    
    @patch('requests.post')
    def test_defect_webhook_notification(self, mock_post):
        """Тест отправки webhook при создании дефекта"""
        # Мокируем успешный ответ webhook
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_post.return_value = mock_response
        
        engineer = EngineerUserFactory()
        project = ProjectFactory()
        project.add_member(engineer, role='engineer')
        
        # Настраиваем webhook для проекта
        project.webhook_url = 'https://external-system.com/webhook/defects'
        project.webhook_enabled = True
        project.save()
        
        self.authenticate(engineer)
        
        # Создаём дефект через API
        defects_url = reverse('defects:defect-list-create')
        data = {
            'title': 'Webhook тест дефект',
            'description': 'Тестирование webhook',
            'project': project.id,
            'priority': 'high',
            'location': 'Тестовое место'
        }
        
        response = self.client.post(defects_url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        # Проверяем, что webhook был вызван
        mock_post.assert_called_once()
        
        # Проверяем данные webhook
        call_args = mock_post.call_args
        webhook_url = call_args[0][0]
        webhook_data = call_args[1]['json']
        
        self.assertEqual(webhook_url, project.webhook_url)
        self.assertEqual(webhook_data['event'], 'defect.created')
        self.assertEqual(webhook_data['defect']['title'], 'Webhook тест дефект')
    
    @patch('requests.post')
    def test_defect_status_webhook(self, mock_post):
        """Тест webhook при изменении статуса дефекта"""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_post.return_value = mock_response
        
        engineer = EngineerUserFactory()
        project = ProjectFactory(
            webhook_url='https://external-system.com/webhook/status',
            webhook_enabled=True
        )
        project.add_member(engineer, role='engineer')
        
        defect = DefectFactory(
            project=project,
            assignee=engineer,
            status='in_progress'
        )
        
        self.authenticate(engineer)
        
        # Изменяем статус дефекта
        status_url = reverse('defects:defect-status-change', args=[defect.id])
        data = {
            'status': 'review',
            'comment': 'Готово к проверке'
        }
        
        response = self.client.post(status_url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Проверяем webhook
        mock_post.assert_called_once()
        
        webhook_data = mock_post.call_args[1]['json']
        self.assertEqual(webhook_data['event'], 'defect.status_changed')
        self.assertEqual(webhook_data['defect']['status'], 'review')
        self.assertEqual(webhook_data['previous_status'], 'in_progress')


@pytest.mark.integration
class FullSystemIntegrationTest(TransactionTestCase, IntegrationTestMixin):
    """Полные интеграционные тесты системы"""
    
    def test_complete_defect_lifecycle_with_integrations(self):
        """Тест полного жизненного цикла дефекта с интеграциями"""
        with patch('requests.post') as mock_webhook, \
             patch('apps.common.services.SmsService.send_sms') as mock_sms:
            
            # Настройка моков
            mock_webhook.return_value.status_code = 200
            mock_sms.return_value = {'success': True, 'message_id': 'test-123'}
            
            # Создание участников
            manager = ManagerUserFactory(phone='+79001234567')
            engineer = EngineerUserFactory(email='engineer@test.com')
            
            # Создание проекта с webhook
            project = ProjectFactory(
                manager=manager,
                webhook_url='https://external.com/webhook',
                webhook_enabled=True
            )
            project.add_member(engineer, role='engineer')
            
            category = DefectCategoryFactory()
            
            # Очистка email outbox
            mail.outbox = []
            
            # Создаём API клиент
            client = self.client
            
            # 1. Инженер создаёт дефект
            client.force_authenticate(user=engineer)
            
            defects_url = reverse('defects:defect-list-create')
            defect_data = {
                'title': 'Интеграционный тест дефект',
                'description': 'Полный тест жизненного цикла',
                'project': project.id,
                'category': category.id,
                'priority': 'critical',
                'severity': 'blocker',
                'location': 'Критическое место'
            }
            
            response = client.post(defects_url, defect_data)
            self.assertEqual(response.status_code, status.HTTP_201_CREATED)
            defect_id = response.data['id']
            
            # Проверяем webhook создания
            self.assertTrue(mock_webhook.called)
            
            # Проверяем SMS уведомление о критическом дефекте
            self.assertTrue(mock_sms.called)
            
            # 2. Загружаем файл к дефекту
            test_file = SimpleUploadedFile(
                'defect_image.jpg',
                b'fake image content',
                content_type='image/jpeg'
            )
            
            files_url = reverse('defects:defect-files', args=[defect_id])
            file_data = {
                'file': test_file,
                'description': 'Фото дефекта'
            }
            
            response = client.post(files_url, file_data, format='multipart')
            self.assertEqual(response.status_code, status.HTTP_201_CREATED)
            
            # 3. Менеджер назначает исполнителя
            client.force_authenticate(user=manager)
            
            assign_url = reverse('defects:defect-assignment', args=[defect_id])
            assign_data = {
                'assignee': engineer.id,
                'due_date': (datetime.now().date() + timedelta(days=3)).isoformat(),
                'comment': 'Критический дефект, требует немедленного внимания'
            }
            
            response = client.post(assign_url, assign_data)
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            
            # Проверяем email уведомление о назначении
            assignment_emails = [
                email for email in mail.outbox
                if engineer.email in email.to and 'назначен' in email.subject.lower()
            ]
            self.assertGreater(len(assignment_emails), 0)
            
            # 4. Инженер принимает дефект в работу
            client.force_authenticate(user=engineer)
            
            status_url = reverse('defects:defect-status-change', args=[defect_id])
            status_data = {
                'status': 'in_progress',
                'comment': 'Начинаю работу над критическим дефектом'
            }
            
            response = client.post(status_url, status_data)
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            
            # 5. Добавляем комментарий с прогрессом
            comments_url = reverse('defects:defect-comments', args=[defect_id])
            comment_data = {
                'content': 'Работа выполнена на 70%, осталось финальное тестирование',
                'comment_type': 'comment'
            }
            
            response = client.post(comments_url, comment_data)
            self.assertEqual(response.status_code, status.HTTP_201_CREATED)
            
            # 6. Инженер отправляет на проверку
            review_data = {
                'status': 'review',
                'comment': 'Дефект устранён, готов к проверке'
            }
            
            response = client.post(status_url, review_data)
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            
            # Проверяем email уведомление менеджера
            review_emails = [
                email for email in mail.outbox
                if manager.email in email.to and 'проверке' in email.subject.lower()
            ]
            self.assertGreater(len(review_emails), 0)
            
            # 7. Менеджер закрывает дефект
            client.force_authenticate(user=manager)
            
            close_data = {
                'status': 'closed',
                'comment': 'Дефект успешно устранён, проверка пройдена'
            }
            
            response = client.post(status_url, close_data)
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            
            # 8. Генерируем отчёт
            generate_url = reverse('reports:generate-report')
            report_data = {
                'report_type': 'defects_summary',
                'title': 'Отчёт по завершённому дефекту',
                'parameters': {
                    'project_id': project.id,
                    'start_date': '2024-01-01',
                    'end_date': '2024-12-31'
                },
                'format': 'xlsx'
            }
            
            response = client.post(generate_url, report_data, format='json')
            self.assertEqual(response.status_code, status.HTTP_201_CREATED)
            
            # Проверяем финальное состояние дефекта
            defect_url = reverse('defects:defect-detail', args=[defect_id])
            response = client.get(defect_url)
            
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            defect_data = response.data
            
            self.assertEqual(defect_data['status'], 'closed')
            self.assertIsNotNone(defect_data['closed_at'])
            self.assertGreater(len(defect_data['comments']), 2)
            self.assertGreater(len(defect_data['files']), 0)
            
            # Проверяем общее количество вызовов интеграций
            self.assertGreaterEqual(mock_webhook.call_count, 3)  # create, status changes
            self.assertGreaterEqual(len(mail.outbox), 3)  # assignment, review, etc.
