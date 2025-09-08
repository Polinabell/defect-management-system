"""
Тесты для модуля дефектов
"""

import pytest
from datetime import date, timedelta
from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile
from rest_framework import status
from .base import BaseAPITestCase, IntegrationTestMixin, SecurityTestMixin
from .factories import (
    UserFactory, ManagerUserFactory, EngineerUserFactory,
    ProjectFactory, DefectFactory, DefectCategoryFactory,
    DefectFileFactory, DefectCommentFactory,
    create_defect_with_files, create_defect_with_comments
)
from apps.defects.models import Defect, DefectCategory, DefectFile, DefectComment


class DefectModelTest(BaseAPITestCase):
    """Тесты модели дефекта"""
    
    def test_defect_creation(self):
        """Тест создания дефекта"""
        defect = DefectFactory()
        self.assertIsInstance(defect, Defect)
        self.assertIsNotNone(defect.defect_number)
        self.assertTrue(defect.defect_number.startswith('DEF-'))
    
    def test_defect_number_generation(self):
        """Тест генерации номера дефекта"""
        project = ProjectFactory()
        defect = DefectFactory(project=project)
        
        # Номер должен содержать ID проекта
        self.assertIn(f"{project.id:03d}", defect.defect_number)
        
        # Создаём ещё один дефект в том же проекте
        defect2 = DefectFactory(project=project)
        
        # Номера должны быть разными
        self.assertNotEqual(defect.defect_number, defect2.defect_number)
    
    def test_defect_str_representation(self):
        """Тест строкового представления дефекта"""
        defect = DefectFactory(title='Тестовый дефект')
        self.assertIn('Тестовый дефект', str(defect))
        self.assertIn(defect.defect_number, str(defect))
    
    def test_defect_is_overdue(self):
        """Тест проверки просрочки дефекта"""
        # Просроченный дефект
        overdue_defect = DefectFactory(
            due_date=date.today() - timedelta(days=1),
            status='in_progress'
        )
        self.assertTrue(overdue_defect.is_overdue)
        
        # Дефект в срок
        normal_defect = DefectFactory(
            due_date=date.today() + timedelta(days=1),
            status='in_progress'
        )
        self.assertFalse(normal_defect.is_overdue)
        
        # Закрытый дефект не просрочен
        closed_defect = DefectFactory(
            due_date=date.today() - timedelta(days=1),
            status='closed'
        )
        self.assertFalse(closed_defect.is_overdue)
    
    def test_defect_days_remaining(self):
        """Тест вычисления оставшихся дней"""
        # Дефект с дедлайном через 5 дней
        defect = DefectFactory(due_date=date.today() + timedelta(days=5))
        self.assertEqual(defect.days_remaining, 5)
        
        # Просроченный дефект
        overdue_defect = DefectFactory(due_date=date.today() - timedelta(days=3))
        self.assertEqual(overdue_defect.days_remaining, -3)
        
        # Дефект без дедлайна
        no_deadline_defect = DefectFactory(due_date=None)
        self.assertIsNone(no_deadline_defect.days_remaining)
    
    def test_defect_status_transitions(self):
        """Тест переходов между статусами дефектов"""
        engineer = EngineerUserFactory()
        manager = ManagerUserFactory()
        defect = DefectFactory(status='new', assignee=engineer)
        
        # Инженер может взять дефект в работу
        can_change, error = defect.can_transition_to('in_progress', engineer)
        self.assertTrue(can_change)
        
        # Инженер не может закрыть новый дефект
        can_change, error = defect.can_transition_to('closed', engineer)
        self.assertFalse(can_change)
        
        # Менеджер может закрыть дефект
        can_change, error = defect.can_transition_to('closed', manager)
        self.assertTrue(can_change)
    
    def test_defect_assignment(self):
        """Тест назначения исполнителя"""
        defect = DefectFactory(status='new', assignee=None)
        engineer = EngineerUserFactory()
        manager = ManagerUserFactory()
        due_date = date.today() + timedelta(days=7)
        
        # Назначаем исполнителя
        defect.assign_to(engineer, due_date, manager)
        
        self.assertEqual(defect.assignee, engineer)
        self.assertEqual(defect.due_date, due_date)
        self.assertIsNotNone(defect.assigned_at)
        
        # Статус должен измениться на "в работе"
        self.assertEqual(defect.status, 'in_progress')


class DefectCategoryModelTest(BaseAPITestCase):
    """Тесты модели категории дефектов"""
    
    def test_category_creation(self):
        """Тест создания категории дефектов"""
        category = DefectCategoryFactory()
        self.assertIsInstance(category, DefectCategory)
        self.assertTrue(category.is_active)
    
    def test_category_str_representation(self):
        """Тест строкового представления категории"""
        category = DefectCategoryFactory(name='Тестовая категория')
        self.assertEqual(str(category), 'Тестовая категория')
    
    def test_category_ordering(self):
        """Тест упорядочивания категорий"""
        category1 = DefectCategoryFactory(order=1, name='А')
        category2 = DefectCategoryFactory(order=2, name='Б')
        category3 = DefectCategoryFactory(order=3, name='В')
        
        categories = list(DefectCategory.objects.all())
        self.assertEqual(categories[0], category1)
        self.assertEqual(categories[1], category2)
        self.assertEqual(categories[2], category3)


class DefectAPITest(BaseAPITestCase):
    """Тесты API дефектов"""
    
    def setUp(self):
        self.defects_url = reverse('defects:defect-list-create')
        self.manager = ManagerUserFactory()
        self.engineer = EngineerUserFactory()
        self.project = ProjectFactory(manager=self.manager)
        self.project.add_member(self.engineer, role='engineer')
        self.category = DefectCategoryFactory()
    
    def test_list_defects(self):
        """Тест получения списка дефектов"""
        # Создаём дефекты в проекте
        defect1 = DefectFactory(project=self.project)
        defect2 = DefectFactory(project=self.project)
        
        self.authenticate(self.engineer)
        response = self.client.get(self.defects_url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        defect_ids = [d['id'] for d in response.data['results']]
        self.assertIn(defect1.id, defect_ids)
        self.assertIn(defect2.id, defect_ids)
    
    def test_create_defect_as_engineer(self):
        """Тест создания дефекта инженером"""
        self.authenticate(self.engineer)
        
        data = {
            'title': 'Новый дефект',
            'description': 'Описание дефекта',
            'project': self.project.id,
            'category': self.category.id,
            'priority': 'medium',
            'severity': 'minor',
            'location': 'Комната 101',
            'floor': '1',
            'room': 'Гостиная'
        }
        
        response = self.client.post(self.defects_url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        # Проверяем, что дефект создался
        defect = Defect.objects.get(id=response.data['id'])
        self.assertEqual(defect.title, 'Новый дефект')
        self.assertEqual(defect.author, self.engineer)
        self.assertEqual(defect.status, 'new')
    
    def test_create_defect_with_files(self):
        """Тест создания дефекта с файлами"""
        self.authenticate(self.engineer)
        
        # Создаём тестовый файл
        test_file = SimpleUploadedFile(
            'test_image.jpg',
            b'fake image content',
            content_type='image/jpeg'
        )
        
        data = {
            'title': 'Дефект с файлом',
            'description': 'Описание',
            'project': self.project.id,
            'category': self.category.id,
            'priority': 'high',
            'location': 'Тестовое место',
            'files': [test_file]
        }
        
        response = self.client.post(self.defects_url, data, format='multipart')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        # Проверяем, что файл прикрепился
        defect = Defect.objects.get(id=response.data['id'])
        self.assertEqual(defect.files.count(), 1)
    
    def test_get_defect_detail(self):
        """Тест получения детальной информации о дефекте"""
        defect = DefectFactory(project=self.project, author=self.engineer)
        
        self.authenticate(self.engineer)
        
        defect_url = reverse('defects:defect-detail', args=[defect.id])
        response = self.client.get(defect_url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['id'], defect.id)
        self.assertIn('files', response.data)
        self.assertIn('comments', response.data)
    
    def test_update_defect(self):
        """Тест обновления дефекта"""
        defect = DefectFactory(project=self.project, author=self.engineer)
        
        self.authenticate(self.engineer)
        
        defect_url = reverse('defects:defect-detail', args=[defect.id])
        data = {
            'description': 'Обновлённое описание',
            'priority': 'high'
        }
        
        response = self.client.patch(defect_url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        defect.refresh_from_db()
        self.assertEqual(defect.description, 'Обновлённое описание')
        self.assertEqual(defect.priority, 'high')
    
    def test_change_defect_status(self):
        """Тест изменения статуса дефекта"""
        defect = DefectFactory(
            project=self.project,
            assignee=self.engineer,
            status='new'
        )
        
        self.authenticate(self.engineer)
        
        status_url = reverse('defects:defect-status-change', args=[defect.id])
        data = {
            'status': 'in_progress',
            'comment': 'Начинаю работу над дефектом'
        }
        
        response = self.client.post(status_url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        defect.refresh_from_db()
        self.assertEqual(defect.status, 'in_progress')
        self.assertIsNotNone(defect.started_at)
    
    def test_assign_defect(self):
        """Тест назначения исполнителя дефекта"""
        defect = DefectFactory(project=self.project, status='new')
        
        self.authenticate(self.manager)
        
        assign_url = reverse('defects:defect-assignment', args=[defect.id])
        data = {
            'assignee': self.engineer.id,
            'due_date': (date.today() + timedelta(days=7)).isoformat(),
            'comment': 'Назначаю исполнителя'
        }
        
        response = self.client.post(assign_url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        defect.refresh_from_db()
        self.assertEqual(defect.assignee, self.engineer)
        self.assertIsNotNone(defect.due_date)
        self.assertIsNotNone(defect.assigned_at)
    
    def test_defect_filtering(self):
        """Тест фильтрации дефектов"""
        # Создаём дефекты с разными статусами
        new_defect = DefectFactory(project=self.project, status='new')
        closed_defect = DefectFactory(project=self.project, status='closed')
        
        self.authenticate(self.engineer)
        
        # Фильтр по статусу
        response = self.client.get(self.defects_url, {'status': 'new'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        defect_ids = [d['id'] for d in response.data['results']]
        self.assertIn(new_defect.id, defect_ids)
        self.assertNotIn(closed_defect.id, defect_ids)
    
    def test_defect_search(self):
        """Тест поиска дефектов"""
        defect = DefectFactory(
            project=self.project,
            title='Уникальная проблема',
            description='Описание уникальной проблемы'
        )
        
        self.authenticate(self.engineer)
        
        response = self.client.get(self.defects_url, {'search': 'Уникальная'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        defect_ids = [d['id'] for d in response.data['results']]
        self.assertIn(defect.id, defect_ids)


class DefectFilesAPITest(BaseAPITestCase):
    """Тесты API файлов дефектов"""
    
    def setUp(self):
        self.engineer = EngineerUserFactory()
        self.project = ProjectFactory()
        self.project.add_member(self.engineer, role='engineer')
        self.defect = DefectFactory(project=self.project, author=self.engineer)
        self.files_url = reverse('defects:defect-files', args=[self.defect.id])
    
    def test_upload_file_to_defect(self):
        """Тест загрузки файла к дефекту"""
        self.authenticate(self.engineer)
        
        test_file = SimpleUploadedFile(
            'test_document.pdf',
            b'fake pdf content',
            content_type='application/pdf'
        )
        
        data = {
            'file': test_file,
            'description': 'Документ к дефекту'
        }
        
        response = self.client.post(self.files_url, data, format='multipart')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        # Проверяем, что файл создался
        defect_file = DefectFile.objects.get(id=response.data['id'])
        self.assertEqual(defect_file.defect, self.defect)
        self.assertEqual(defect_file.uploaded_by, self.engineer)
        self.assertEqual(defect_file.file_type, 'document')
    
    def test_list_defect_files(self):
        """Тест получения списка файлов дефекта"""
        # Создаём файлы
        file1 = DefectFileFactory(defect=self.defect, is_main=True)
        file2 = DefectFileFactory(defect=self.defect, is_main=False)
        
        self.authenticate(self.engineer)
        
        response = self.client.get(self.files_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Главный файл должен быть первым
        files_data = response.data['results']
        self.assertEqual(len(files_data), 2)
        self.assertTrue(files_data[0]['is_main'])
        self.assertFalse(files_data[1]['is_main'])
    
    def test_delete_defect_file(self):
        """Тест удаления файла дефекта"""
        defect_file = DefectFileFactory(defect=self.defect, uploaded_by=self.engineer)
        
        self.authenticate(self.engineer)
        
        file_url = reverse('defects:defect-file-detail', 
                          args=[self.defect.id, defect_file.id])
        response = self.client.delete(file_url)
        
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        
        # Проверяем, что файл удалился
        self.assertFalse(DefectFile.objects.filter(id=defect_file.id).exists())


class DefectCommentsAPITest(BaseAPITestCase):
    """Тесты API комментариев дефектов"""
    
    def setUp(self):
        self.engineer = EngineerUserFactory()
        self.manager = ManagerUserFactory()
        self.project = ProjectFactory(manager=self.manager)
        self.project.add_member(self.engineer, role='engineer')
        self.defect = DefectFactory(project=self.project, author=self.engineer)
        self.comments_url = reverse('defects:defect-comments', args=[self.defect.id])
    
    def test_add_comment_to_defect(self):
        """Тест добавления комментария к дефекту"""
        self.authenticate(self.engineer)
        
        data = {
            'content': 'Это мой комментарий к дефекту',
            'comment_type': 'comment'
        }
        
        response = self.client.post(self.comments_url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        # Проверяем, что комментарий создался
        comment = DefectComment.objects.get(id=response.data['id'])
        self.assertEqual(comment.defect, self.defect)
        self.assertEqual(comment.author, self.engineer)
        self.assertEqual(comment.content, 'Это мой комментарий к дефекту')
    
    def test_list_defect_comments(self):
        """Тест получения списка комментариев дефекта"""
        # Создаём комментарии
        comment1 = DefectCommentFactory(defect=self.defect, author=self.engineer)
        comment2 = DefectCommentFactory(defect=self.defect, author=self.manager)
        
        self.authenticate(self.engineer)
        
        response = self.client.get(self.comments_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        comments_data = response.data['results']
        self.assertEqual(len(comments_data), 2)
    
    def test_reply_to_comment(self):
        """Тест ответа на комментарий"""
        parent_comment = DefectCommentFactory(defect=self.defect, author=self.engineer)
        
        self.authenticate(self.manager)
        
        data = {
            'content': 'Это ответ на комментарий',
            'comment_type': 'comment',
            'reply_to': parent_comment.id
        }
        
        response = self.client.post(self.comments_url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        # Проверяем, что это ответ
        reply = DefectComment.objects.get(id=response.data['id'])
        self.assertEqual(reply.reply_to, parent_comment)
    
    def test_internal_comment(self):
        """Тест внутреннего комментария"""
        self.authenticate(self.manager)
        
        data = {
            'content': 'Внутренний комментарий',
            'comment_type': 'comment',
            'is_internal': True
        }
        
        response = self.client.post(self.comments_url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        comment = DefectComment.objects.get(id=response.data['id'])
        self.assertTrue(comment.is_internal)


class DefectIntegrationTest(BaseAPITestCase, IntegrationTestMixin):
    """Интеграционные тесты для модуля дефектов"""
    
    def test_full_defect_workflow(self):
        """Тест полного workflow дефекта"""
        manager = ManagerUserFactory()
        engineer = EngineerUserFactory()
        observer = UserFactory(role='observer')
        
        project = ProjectFactory(manager=manager)
        project.add_member(engineer, role='engineer')
        project.add_member(observer, role='observer')
        
        category = DefectCategoryFactory()
        
        self.authenticate(engineer)
        
        # 1. Создаём дефект
        defects_url = reverse('defects:defect-list-create')
        defect_data = {
            'title': 'Интеграционный тест дефект',
            'description': 'Тестирование полного workflow дефекта',
            'project': project.id,
            'category': category.id,
            'priority': 'high',
            'severity': 'major',
            'location': 'Тестовая комната',
            'floor': '2',
            'room': 'Офис'
        }
        
        response = self.client.post(defects_url, defect_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        defect_id = response.data['id']
        
        # 2. Загружаем файл к дефекту
        files_url = reverse('defects:defect-files', args=[defect_id])
        test_file = SimpleUploadedFile(
            'defect_photo.jpg',
            b'fake image content',
            content_type='image/jpeg'
        )
        
        file_data = {
            'file': test_file,
            'description': 'Фото дефекта'
        }
        
        response = self.client.post(files_url, file_data, format='multipart')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        # 3. Менеджер назначает исполнителя
        self.authenticate(manager)
        
        assign_url = reverse('defects:defect-assignment', args=[defect_id])
        assign_data = {
            'assignee': engineer.id,
            'due_date': (date.today() + timedelta(days=5)).isoformat(),
            'comment': 'Назначаю исполнителя'
        }
        
        response = self.client.post(assign_url, assign_data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # 4. Инженер берёт дефект в работу
        self.authenticate(engineer)
        
        status_url = reverse('defects:defect-status-change', args=[defect_id])
        status_data = {
            'status': 'in_progress',
            'comment': 'Начинаю работу'
        }
        
        response = self.client.post(status_url, status_data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # 5. Добавляем комментарий о ходе работ
        comments_url = reverse('defects:defect-comments', args=[defect_id])
        comment_data = {
            'content': 'Работа выполнена на 50%',
            'comment_type': 'comment'
        }
        
        response = self.client.post(comments_url, comment_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        # 6. Инженер отправляет на проверку
        review_data = {
            'status': 'review',
            'comment': 'Работа выполнена, требуется проверка'
        }
        
        response = self.client.post(status_url, review_data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # 7. Менеджер закрывает дефект
        self.authenticate(manager)
        
        close_data = {
            'status': 'closed',
            'comment': 'Дефект устранён'
        }
        
        response = self.client.post(status_url, close_data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # 8. Проверяем финальное состояние
        defect_url = reverse('defects:defect-detail', args=[defect_id])
        response = self.client.get(defect_url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['status'], 'closed')
        self.assertIsNotNone(response.data['closed_at'])
        self.assertGreater(len(response.data['comments']), 0)
        self.assertGreater(len(response.data['files']), 0)


class DefectSecurityTest(BaseAPITestCase, SecurityTestMixin):
    """Тесты безопасности для модуля дефектов"""
    
    def test_defect_access_permissions(self):
        """Тест прав доступа к дефектам"""
        # Создаём проекты и пользователей
        project1 = ProjectFactory()
        project2 = ProjectFactory()
        
        engineer1 = EngineerUserFactory()
        engineer2 = EngineerUserFactory()
        
        # Добавляем инженеров в разные проекты
        project1.add_member(engineer1, role='engineer')
        project2.add_member(engineer2, role='engineer')
        
        # Создаём дефекты в разных проектах
        defect1 = DefectFactory(project=project1)
        defect2 = DefectFactory(project=project2)
        
        # engineer1 должен видеть только дефекты своего проекта
        self.authenticate(engineer1)
        
        defects_url = reverse('defects:defect-list-create')
        response = self.client.get(defects_url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        defect_ids = [d['id'] for d in response.data['results']]
        
        self.assertIn(defect1.id, defect_ids)
        self.assertNotIn(defect2.id, defect_ids)
    
    def test_file_upload_security(self):
        """Тест безопасности загрузки файлов"""
        engineer = EngineerUserFactory()
        project = ProjectFactory()
        project.add_member(engineer, role='engineer')
        defect = DefectFactory(project=project)
        
        self.authenticate(engineer)
        
        files_url = reverse('defects:defect-files', args=[defect.id])
        
        # Попытка загрузить исполняемый файл
        malicious_file = SimpleUploadedFile(
            'malicious.exe',
            b'fake exe content',
            content_type='application/x-executable'
        )
        
        data = {'file': malicious_file}
        response = self.client.post(files_url, data, format='multipart')
        
        # Должна быть ошибка валидации
        self.assertIn(response.status_code, [400, 415])


@pytest.mark.django_db
class TestDefectModelPytest:
    """Pytest тесты для модели дефектов"""
    
    def test_create_defect_with_files(self):
        """Тест создания дефекта с файлами"""
        defect = create_defect_with_files(files_count=3)
        
        assert defect.files.count() == 3
        assert defect.files.filter(is_main=True).count() == 1
    
    def test_create_defect_with_comments(self):
        """Тест создания дефекта с комментариями"""
        defect = create_defect_with_comments(comments_count=5)
        
        assert defect.comments.count() == 5
    
    @pytest.mark.parametrize('status,can_close', [
        ('new', False),
        ('in_progress', False),
        ('review', True),
        ('closed', False),
    ])
    def test_defect_status_transitions(self, status, can_close):
        """Параметризованный тест переходов статусов"""
        manager = ManagerUserFactory()
        defect = DefectFactory(status=status)
        
        can_change, _ = defect.can_transition_to('closed', manager)
        assert can_change == can_close
