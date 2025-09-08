"""
Тесты для модуля управления проектами
"""

from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.utils import timezone
from rest_framework.test import APITestCase
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from datetime import date, timedelta
from .models import Project, ProjectMember, ProjectStage, ProjectTemplate, ProjectStageTemplate

User = get_user_model()


class ProjectModelTest(TestCase):
    """
    Тесты модели Project
    """
    
    def setUp(self):
        """Подготовка данных для тестов"""
        self.manager = User.objects.create_user(
            email='manager@example.com',
            username='manager',
            first_name='Менеджер',
            last_name='Проектов',
            role=User.Role.MANAGER
        )
        
        self.engineer = User.objects.create_user(
            email='engineer@example.com',
            username='engineer',
            first_name='Инженер',
            last_name='Строитель',
            role=User.Role.ENGINEER
        )
        
        self.project_data = {
            'name': 'Тестовый проект',
            'description': 'Описание тестового проекта',
            'address': 'г. Москва, ул. Тестовая, д. 1',
            'customer': 'ООО "Тест"',
            'manager': self.manager,
            'start_date': date.today(),
            'end_date': date.today() + timedelta(days=30),
            'priority': 'medium',
            'building_type': 'residential',
        }
    
    def test_create_project(self):
        """Тест создания проекта"""
        project = Project.objects.create(**self.project_data)
        
        self.assertEqual(project.name, self.project_data['name'])
        self.assertEqual(project.manager, self.manager)
        self.assertEqual(project.status, Project.Status.PLANNING)
        self.assertIsNotNone(project.slug)
        self.assertTrue(project.slug)
    
    def test_project_slug_generation(self):
        """Тест автогенерации slug"""
        project = Project.objects.create(**self.project_data)
        self.assertIsNotNone(project.slug)
        self.assertTrue(len(project.slug) > 0)
    
    def test_project_duration_planned(self):
        """Тест вычисления планируемой продолжительности"""
        project = Project.objects.create(**self.project_data)
        expected_duration = (self.project_data['end_date'] - self.project_data['start_date']).days
        self.assertEqual(project.duration_planned, expected_duration)
    
    def test_project_is_overdue(self):
        """Тест проверки просрочки проекта"""
        # Просроченный проект
        overdue_data = self.project_data.copy()
        overdue_data['end_date'] = date.today() - timedelta(days=1)
        overdue_project = Project.objects.create(**overdue_data)
        self.assertTrue(overdue_project.is_overdue)
        
        # Проект в срок
        normal_project = Project.objects.create(**self.project_data)
        self.assertFalse(normal_project.is_overdue)
    
    def test_add_member(self):
        """Тест добавления участника в проект"""
        project = Project.objects.create(**self.project_data)
        
        member, created = project.add_member(self.engineer, role='engineer')
        
        self.assertTrue(created)
        self.assertEqual(member.user, self.engineer)
        self.assertEqual(member.role, 'engineer')
        self.assertTrue(project.is_member(self.engineer))
    
    def test_remove_member(self):
        """Тест удаления участника из проекта"""
        project = Project.objects.create(**self.project_data)
        project.add_member(self.engineer, role='engineer')
        
        self.assertTrue(project.is_member(self.engineer))
        
        project.remove_member(self.engineer)
        
        self.assertFalse(project.is_member(self.engineer))
    
    def test_get_defects_stats(self):
        """Тест получения статистики дефектов"""
        project = Project.objects.create(**self.project_data)
        stats = project.get_defects_stats()
        
        self.assertIsInstance(stats, dict)
        self.assertIn('total', stats)
        self.assertIn('new', stats)
        self.assertIn('closed', stats)
        self.assertEqual(stats['total'], 0)  # Пока дефектов нет


class ProjectStageModelTest(TestCase):
    """
    Тесты модели ProjectStage
    """
    
    def setUp(self):
        """Подготовка данных для тестов"""
        self.manager = User.objects.create_user(
            email='manager@example.com',
            username='manager',
            first_name='Менеджер',
            last_name='Проектов',
            role=User.Role.MANAGER
        )
        
        self.project = Project.objects.create(
            name='Тестовый проект',
            description='Описание проекта',
            address='Тестовый адрес',
            customer='Тестовый заказчик',
            manager=self.manager,
            start_date=date.today(),
            end_date=date.today() + timedelta(days=30)
        )
        
        self.stage_data = {
            'project': self.project,
            'name': 'Подготовительные работы',
            'description': 'Описание этапа',
            'order': 1,
            'start_date': date.today(),
            'end_date': date.today() + timedelta(days=7),
            'estimated_hours': 40,
        }
    
    def test_create_stage(self):
        """Тест создания этапа проекта"""
        stage = ProjectStage.objects.create(**self.stage_data)
        
        self.assertEqual(stage.name, self.stage_data['name'])
        self.assertEqual(stage.project, self.project)
        self.assertEqual(stage.status, ProjectStage.Status.NOT_STARTED)
        self.assertEqual(stage.completion_percentage, 0)
    
    def test_stage_duration_planned(self):
        """Тест вычисления планируемой продолжительности этапа"""
        stage = ProjectStage.objects.create(**self.stage_data)
        expected_duration = (self.stage_data['end_date'] - self.stage_data['start_date']).days
        self.assertEqual(stage.duration_planned, expected_duration)
    
    def test_stage_is_overdue(self):
        """Тест проверки просрочки этапа"""
        # Просроченный этап
        overdue_data = self.stage_data.copy()
        overdue_data['end_date'] = date.today() - timedelta(days=1)
        overdue_stage = ProjectStage.objects.create(**overdue_data)
        self.assertTrue(overdue_stage.is_overdue)
        
        # Этап в срок
        normal_stage = ProjectStage.objects.create(**self.stage_data)
        self.assertFalse(normal_stage.is_overdue)


class ProjectTemplateTest(TestCase):
    """
    Тесты модели ProjectTemplate
    """
    
    def setUp(self):
        """Подготовка данных для тестов"""
        self.admin = User.objects.create_user(
            email='admin@example.com',
            username='admin',
            first_name='Администратор',
            last_name='Системы',
            role=User.Role.ADMIN
        )
        
        self.template = ProjectTemplate.objects.create(
            name='Жилой дом',
            description='Шаблон для жилых домов',
            building_type='residential',
            created_by=self.admin
        )
    
    def test_create_template(self):
        """Тест создания шаблона проекта"""
        self.assertEqual(self.template.name, 'Жилой дом')
        self.assertEqual(self.template.building_type, 'residential')
        self.assertTrue(self.template.is_active)
        self.assertEqual(self.template.created_by, self.admin)
    
    def test_create_stage_templates(self):
        """Тест создания шаблонов этапов"""
        stage_template = ProjectStageTemplate.objects.create(
            template=self.template,
            name='Фундаментные работы',
            description='Устройство фундамента',
            order=1,
            estimated_days=14
        )
        
        self.assertEqual(stage_template.template, self.template)
        self.assertEqual(stage_template.name, 'Фундаментные работы')
        self.assertEqual(stage_template.estimated_days, 14)


class ProjectAPITest(APITestCase):
    """
    Тесты API проектов
    """
    
    def setUp(self):
        """Подготовка данных для тестов"""
        # Создаём пользователей
        self.admin = User.objects.create_user(
            email='admin@example.com',
            username='admin',
            role=User.Role.ADMIN,
            first_name='Админ',
            last_name='Админов'
        )
        
        self.manager = User.objects.create_user(
            email='manager@example.com',
            username='manager',
            role=User.Role.MANAGER,
            first_name='Менеджер',
            last_name='Менеджеров'
        )
        
        self.engineer = User.objects.create_user(
            email='engineer@example.com',
            username='engineer',
            role=User.Role.ENGINEER,
            first_name='Инженер',
            last_name='Инженеров'
        )
        
        # Создаём проект
        self.project = Project.objects.create(
            name='API Тест Проект',
            description='Проект для тестирования API',
            address='Тестовый адрес',
            customer='Тестовый заказчик',
            manager=self.manager,
            start_date=date.today(),
            end_date=date.today() + timedelta(days=30)
        )
        
        # Добавляем инженера в проект
        self.project.add_member(self.engineer, role='engineer')
        
        # URL для тестов
        self.projects_url = reverse('projects:project-list-create')
        self.project_detail_url = reverse('projects:project-detail', args=[self.project.id])
    
    def _authenticate(self, user):
        """Хелпер для аутентификации пользователя"""
        refresh = RefreshToken.for_user(user)
        access_token = str(refresh.access_token)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token}')
    
    def test_list_projects_as_admin(self):
        """Тест получения списка проектов администратором"""
        self._authenticate(self.admin)
        
        response = self.client.get(self.projects_url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['name'], self.project.name)
    
    def test_list_projects_as_manager(self):
        """Тест получения списка проектов менеджером"""
        self._authenticate(self.manager)
        
        response = self.client.get(self.projects_url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)  # Видит управляемый проект
    
    def test_list_projects_as_engineer(self):
        """Тест получения списка проектов инженером"""
        self._authenticate(self.engineer)
        
        response = self.client.get(self.projects_url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)  # Видит проект, где участвует
    
    def test_create_project_as_manager(self):
        """Тест создания проекта менеджером"""
        self._authenticate(self.manager)
        
        project_data = {
            'name': 'Новый проект',
            'description': 'Описание нового проекта',
            'address': 'Новый адрес',
            'customer': 'Новый заказчик',
            'start_date': date.today(),
            'end_date': date.today() + timedelta(days=60),
            'priority': 'high'
        }
        
        response = self.client.post(self.projects_url, project_data)
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['name'], project_data['name'])
        
        # Проверяем, что проект создался в БД
        self.assertTrue(Project.objects.filter(name='Новый проект').exists())
    
    def test_create_project_as_engineer(self):
        """Тест создания проекта инженером (должно быть запрещено)"""
        self._authenticate(self.engineer)
        
        project_data = {
            'name': 'Проект инженера',
            'description': 'Описание',
            'address': 'Адрес',
            'customer': 'Заказчик',
            'start_date': date.today(),
            'end_date': date.today() + timedelta(days=30)
        }
        
        response = self.client.post(self.projects_url, project_data)
        
        # Инженер не может создавать проекты
        self.assertIn(response.status_code, [status.HTTP_403_FORBIDDEN, status.HTTP_400_BAD_REQUEST])
    
    def test_get_project_detail(self):
        """Тест получения деталей проекта"""
        self._authenticate(self.manager)
        
        response = self.client.get(self.project_detail_url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], self.project.name)
        self.assertIn('members', response.data)
        self.assertIn('stages', response.data)
    
    def test_update_project_as_manager(self):
        """Тест обновления проекта менеджером"""
        self._authenticate(self.manager)
        
        update_data = {
            'description': 'Обновлённое описание',
            'priority': 'high'
        }
        
        response = self.client.patch(self.project_detail_url, update_data)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Проверяем, что данные обновились
        self.project.refresh_from_db()
        self.assertEqual(self.project.description, 'Обновлённое описание')
        self.assertEqual(self.project.priority, 'high')
    
    def test_update_project_as_engineer(self):
        """Тест обновления проекта инженером (должно быть запрещено)"""
        self._authenticate(self.engineer)
        
        update_data = {
            'description': 'Попытка обновления'
        }
        
        response = self.client.patch(self.project_detail_url, update_data)
        
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
    
    def test_project_search(self):
        """Тест поиска проектов"""
        self._authenticate(self.admin)
        
        search_url = reverse('projects:project-search')
        search_data = {
            'query': 'API Тест',
            'status': ['planning'],
            'priority': ['medium']
        }
        
        response = self.client.post(search_url, search_data)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 1)
        self.assertEqual(response.data['results'][0]['name'], self.project.name)
    
    def test_project_stats(self):
        """Тест получения статистики проектов"""
        self._authenticate(self.admin)
        
        stats_url = reverse('projects:project-stats')
        response = self.client.get(stats_url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('total_projects', response.data)
        self.assertIn('active_projects', response.data)
        self.assertIn('projects_by_status', response.data)
        self.assertEqual(response.data['total_projects'], 1)


class ProjectMemberAPITest(APITestCase):
    """
    Тесты API участников проектов
    """
    
    def setUp(self):
        """Подготовка данных для тестов"""
        self.manager = User.objects.create_user(
            email='manager@example.com',
            username='manager',
            role=User.Role.MANAGER,
            first_name='Менеджер',
            last_name='Менеджеров'
        )
        
        self.engineer = User.objects.create_user(
            email='engineer@example.com',
            username='engineer',
            role=User.Role.ENGINEER,
            first_name='Инженер',
            last_name='Инженеров'
        )
        
        self.observer = User.objects.create_user(
            email='observer@example.com',
            username='observer',
            role=User.Role.OBSERVER,
            first_name='Наблюдатель',
            last_name='Наблюдателев'
        )
        
        self.project = Project.objects.create(
            name='Тест проект для участников',
            description='Описание',
            address='Адрес',
            customer='Заказчик',
            manager=self.manager,
            start_date=date.today(),
            end_date=date.today() + timedelta(days=30)
        )
        
        self.members_url = reverse('projects:project-members', args=[self.project.id])
        self.add_member_url = reverse('projects:add-project-member', args=[self.project.id])
    
    def _authenticate(self, user):
        """Хелпер для аутентификации пользователя"""
        refresh = RefreshToken.for_user(user)
        access_token = str(refresh.access_token)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token}')
    
    def test_add_member_as_manager(self):
        """Тест добавления участника менеджером"""
        self._authenticate(self.manager)
        
        member_data = {
            'user': self.engineer.id,
            'role': 'engineer'
        }
        
        response = self.client.post(self.add_member_url, member_data)
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(self.project.is_member(self.engineer))
    
    def test_add_existing_member(self):
        """Тест добавления уже существующего участника"""
        self._authenticate(self.manager)
        
        # Добавляем участника
        self.project.add_member(self.engineer, role='engineer')
        
        member_data = {
            'user': self.engineer.id,
            'role': 'engineer'
        }
        
        response = self.client.post(self.add_member_url, member_data)
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_list_members(self):
        """Тест получения списка участников"""
        self._authenticate(self.manager)
        
        # Добавляем участника
        self.project.add_member(self.engineer, role='engineer')
        
        response = self.client.get(self.members_url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Менеджер + инженер = 2 участника
        self.assertEqual(len(response.data['results']), 2)
    
    def test_remove_member(self):
        """Тест удаления участника"""
        self._authenticate(self.manager)
        
        # Добавляем участника
        self.project.add_member(self.engineer, role='engineer')
        
        remove_url = reverse('projects:remove-project-member', args=[self.project.id, self.engineer.id])
        response = self.client.delete(remove_url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Проверяем, что участник деактивирован
        member = ProjectMember.objects.get(project=self.project, user=self.engineer)
        self.assertFalse(member.is_active)


class ProjectStageAPITest(APITestCase):
    """
    Тесты API этапов проектов
    """
    
    def setUp(self):
        """Подготовка данных для тестов"""
        self.manager = User.objects.create_user(
            email='manager@example.com',
            username='manager',
            role=User.Role.MANAGER,
            first_name='Менеджер',
            last_name='Менеджеров'
        )
        
        self.project = Project.objects.create(
            name='Тест проект для этапов',
            description='Описание',
            address='Адрес',
            customer='Заказчик',
            manager=self.manager,
            start_date=date.today(),
            end_date=date.today() + timedelta(days=30)
        )
        
        self.stages_url = reverse('projects:project-stages', args=[self.project.id])
    
    def _authenticate(self, user):
        """Хелпер для аутентификации пользователя"""
        refresh = RefreshToken.for_user(user)
        access_token = str(refresh.access_token)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token}')
    
    def test_create_stage(self):
        """Тест создания этапа проекта"""
        self._authenticate(self.manager)
        
        stage_data = {
            'name': 'Фундаментные работы',
            'description': 'Устройство фундамента',
            'order': 1,
            'start_date': date.today(),
            'end_date': date.today() + timedelta(days=7),
            'estimated_hours': 40
        }
        
        response = self.client.post(self.stages_url, stage_data)
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['name'], stage_data['name'])
        
        # Проверяем, что этап создался в БД
        self.assertTrue(ProjectStage.objects.filter(
            project=self.project,
            name='Фундаментные работы'
        ).exists())
    
    def test_list_stages(self):
        """Тест получения списка этапов"""
        self._authenticate(self.manager)
        
        # Создаём этап
        ProjectStage.objects.create(
            project=self.project,
            name='Тестовый этап',
            order=1,
            start_date=date.today(),
            end_date=date.today() + timedelta(days=7)
        )
        
        response = self.client.get(self.stages_url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['name'], 'Тестовый этап')
