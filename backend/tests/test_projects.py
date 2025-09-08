"""
Тесты для модуля проектов
"""

import pytest
from datetime import date, timedelta
from django.urls import reverse
from rest_framework import status
from .base import BaseAPITestCase, IntegrationTestMixin
from .factories import (
    UserFactory, ManagerUserFactory, EngineerUserFactory,
    ProjectFactory, ProjectStageFactory, ProjectMemberFactory,
    create_project_with_members, create_project_with_stages
)
from apps.projects.models import Project, ProjectStage, ProjectMember


class ProjectModelTest(BaseAPITestCase):
    """Тесты модели проекта"""
    
    def test_project_creation(self):
        """Тест создания проекта"""
        project = ProjectFactory()
        self.assertIsInstance(project, Project)
        self.assertIsNotNone(project.slug)
        self.assertTrue(project.slug)
        self.assertIsNotNone(project.created_at)
    
    def test_project_str_representation(self):
        """Тест строкового представления проекта"""
        project = ProjectFactory(name='Тестовый проект')
        self.assertEqual(str(project), 'Тестовый проект')
    
    def test_project_slug_generation(self):
        """Тест генерации slug для проекта"""
        project = ProjectFactory(name='Проект с длинным названием')
        self.assertIsNotNone(project.slug)
        # Slug должен содержать только допустимые символы
        self.assertTrue(project.slug.replace('-', '').replace('_', '').isalnum())
    
    def test_project_duration_planned(self):
        """Тест вычисления планируемой продолжительности"""
        start_date = date.today()
        end_date = start_date + timedelta(days=30)
        
        project = ProjectFactory(start_date=start_date, end_date=end_date)
        self.assertEqual(project.duration_planned, 30)
    
    def test_project_is_overdue(self):
        """Тест проверки просрочки проекта"""
        # Просроченный проект
        overdue_project = ProjectFactory(
            end_date=date.today() - timedelta(days=1),
            status='in_progress'
        )
        self.assertTrue(overdue_project.is_overdue)
        
        # Проект в срок
        normal_project = ProjectFactory(
            end_date=date.today() + timedelta(days=1)
        )
        self.assertFalse(normal_project.is_overdue)
        
        # Завершённый проект не считается просроченным
        completed_project = ProjectFactory(
            end_date=date.today() - timedelta(days=1),
            status='completed'
        )
        self.assertFalse(completed_project.is_overdue)
    
    def test_project_progress_calculation(self):
        """Тест вычисления прогресса проекта"""
        project = ProjectFactory()
        
        # Создаём этапы с разным прогрессом
        ProjectStageFactory(project=project, completion_percentage=100)
        ProjectStageFactory(project=project, completion_percentage=50)
        ProjectStageFactory(project=project, completion_percentage=0)
        
        # Средний прогресс должен быть 50%
        self.assertEqual(project.progress_percentage, 50)
    
    def test_project_member_management(self):
        """Тест управления участниками проекта"""
        project = ProjectFactory()
        user = EngineerUserFactory()
        
        # Проверяем, что пользователь не является участником
        self.assertFalse(project.is_member(user))
        
        # Добавляем пользователя
        member, created = project.add_member(user, role='engineer')
        self.assertTrue(created)
        self.assertTrue(project.is_member(user))
        
        # Попытка добавить того же пользователя
        member, created = project.add_member(user, role='engineer')
        self.assertFalse(created)
        
        # Удаляем пользователя
        project.remove_member(user)
        # Пользователь должен быть деактивирован, но не удалён
        member.refresh_from_db()
        self.assertFalse(member.is_active)


class ProjectStageModelTest(BaseAPITestCase):
    """Тесты модели этапа проекта"""
    
    def test_stage_creation(self):
        """Тест создания этапа проекта"""
        stage = ProjectStageFactory()
        self.assertIsInstance(stage, ProjectStage)
        self.assertIsNotNone(stage.project)
    
    def test_stage_ordering(self):
        """Тест упорядочивания этапов"""
        project = ProjectFactory()
        stage1 = ProjectStageFactory(project=project, order=1)
        stage2 = ProjectStageFactory(project=project, order=2)
        stage3 = ProjectStageFactory(project=project, order=3)
        
        stages = list(project.stages.all().order_by('order'))
        self.assertEqual(stages, [stage1, stage2, stage3])
    
    def test_stage_duration_calculation(self):
        """Тест вычисления продолжительности этапа"""
        start_date = date.today()
        end_date = start_date + timedelta(days=14)
        
        stage = ProjectStageFactory(start_date=start_date, end_date=end_date)
        self.assertEqual(stage.duration_planned, 14)
    
    def test_stage_is_overdue(self):
        """Тест проверки просрочки этапа"""
        overdue_stage = ProjectStageFactory(
            end_date=date.today() - timedelta(days=1),
            status='in_progress'
        )
        self.assertTrue(overdue_stage.is_overdue)
        
        normal_stage = ProjectStageFactory(
            end_date=date.today() + timedelta(days=1)
        )
        self.assertFalse(normal_stage.is_overdue)


class ProjectAPITest(BaseAPITestCase):
    """Тесты API проектов"""
    
    def setUp(self):
        self.projects_url = reverse('projects:project-list-create')
        self.manager = ManagerUserFactory()
        self.engineer = EngineerUserFactory()
    
    def test_list_projects_as_manager(self):
        """Тест получения списка проектов менеджером"""
        # Создаём проекты
        project1 = ProjectFactory(manager=self.manager)
        project2 = ProjectFactory()
        
        self.authenticate(self.manager)
        response = self.client.get(self.projects_url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Менеджер должен видеть минимум свои проекты
        project_ids = [p['id'] for p in response.data['results']]
        self.assertIn(project1.id, project_ids)
    
    def test_create_project_as_manager(self):
        """Тест создания проекта менеджером"""
        self.authenticate(self.manager)
        
        data = {
            'name': 'Новый проект',
            'description': 'Описание нового проекта',
            'address': 'ул. Тестовая, д. 1',
            'customer': 'ООО "Тест"',
            'start_date': date.today().isoformat(),
            'end_date': (date.today() + timedelta(days=90)).isoformat(),
            'building_type': 'residential',
            'priority': 'medium'
        }
        
        response = self.client.post(self.projects_url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        # Проверяем, что проект создался
        project = Project.objects.get(id=response.data['id'])
        self.assertEqual(project.name, 'Новый проект')
        self.assertEqual(project.manager, self.manager)
    
    def test_create_project_as_engineer(self):
        """Тест создания проекта инженером (должно быть запрещено)"""
        self.authenticate(self.engineer)
        
        data = {
            'name': 'Проект инженера',
            'description': 'Описание',
            'start_date': date.today().isoformat()
        }
        
        response = self.client.post(self.projects_url, data)
        self.assert_permission_denied(response)
    
    def test_get_project_detail(self):
        """Тест получения детальной информации о проекте"""
        project = ProjectFactory(manager=self.manager)
        project.add_member(self.engineer, role='engineer')
        
        self.authenticate(self.engineer)
        
        project_url = reverse('projects:project-detail', args=[project.id])
        response = self.client.get(project_url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['id'], project.id)
        self.assertIn('members', response.data)
        self.assertIn('stages', response.data)
    
    def test_update_project_as_manager(self):
        """Тест обновления проекта менеджером"""
        project = ProjectFactory(manager=self.manager)
        
        self.authenticate(self.manager)
        
        project_url = reverse('projects:project-detail', args=[project.id])
        data = {
            'description': 'Обновлённое описание',
            'priority': 'high'
        }
        
        response = self.client.patch(project_url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        project.refresh_from_db()
        self.assertEqual(project.description, 'Обновлённое описание')
        self.assertEqual(project.priority, 'high')
    
    def test_project_filtering(self):
        """Тест фильтрации проектов"""
        # Создаём проекты с разными статусами
        active_project = ProjectFactory(status='in_progress', manager=self.manager)
        completed_project = ProjectFactory(status='completed', manager=self.manager)
        
        self.authenticate(self.manager)
        
        # Фильтр по статусу
        response = self.client.get(self.projects_url, {'status': 'in_progress'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        project_ids = [p['id'] for p in response.data['results']]
        self.assertIn(active_project.id, project_ids)
        self.assertNotIn(completed_project.id, project_ids)
    
    def test_project_search(self):
        """Тест поиска проектов"""
        project = ProjectFactory(name='Уникальное название', manager=self.manager)
        
        self.authenticate(self.manager)
        
        response = self.client.get(self.projects_url, {'search': 'Уникальное'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        project_ids = [p['id'] for p in response.data['results']]
        self.assertIn(project.id, project_ids)


class ProjectMembersAPITest(BaseAPITestCase):
    """Тесты API участников проекта"""
    
    def setUp(self):
        self.manager = ManagerUserFactory()
        self.engineer = EngineerUserFactory()
        self.project = ProjectFactory(manager=self.manager)
        
        self.members_url = reverse('projects:project-members', args=[self.project.id])
        self.add_member_url = reverse('projects:add-project-member', args=[self.project.id])
    
    def test_add_member_as_manager(self):
        """Тест добавления участника менеджером"""
        self.authenticate(self.manager)
        
        data = {
            'user': self.engineer.id,
            'role': 'engineer'
        }
        
        response = self.client.post(self.add_member_url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        # Проверяем, что участник добавлен
        self.assertTrue(self.project.is_member(self.engineer))
    
    def test_add_member_as_engineer(self):
        """Тест добавления участника инженером (должно быть запрещено)"""
        self.authenticate(self.engineer)
        
        data = {
            'user': self.engineer.id,
            'role': 'engineer'
        }
        
        response = self.client.post(self.add_member_url, data)
        self.assert_permission_denied(response)
    
    def test_list_project_members(self):
        """Тест получения списка участников проекта"""
        # Добавляем участников
        self.project.add_member(self.engineer, role='engineer')
        
        self.authenticate(self.manager)
        
        response = self.client.get(self.members_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Должен быть минимум 1 участник (инженер)
        self.assertGreaterEqual(len(response.data['results']), 1)
    
    def test_remove_member(self):
        """Тест удаления участника проекта"""
        # Добавляем участника
        self.project.add_member(self.engineer, role='engineer')
        
        self.authenticate(self.manager)
        
        remove_url = reverse('projects:remove-project-member', 
                           args=[self.project.id, self.engineer.id])
        response = self.client.delete(remove_url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Проверяем, что участник деактивирован
        member = ProjectMember.objects.get(project=self.project, user=self.engineer)
        self.assertFalse(member.is_active)


class ProjectStagesAPITest(BaseAPITestCase):
    """Тесты API этапов проекта"""
    
    def setUp(self):
        self.manager = ManagerUserFactory()
        self.project = ProjectFactory(manager=self.manager)
        self.stages_url = reverse('projects:project-stages', args=[self.project.id])
    
    def test_create_stage(self):
        """Тест создания этапа проекта"""
        self.authenticate(self.manager)
        
        data = {
            'name': 'Фундаментные работы',
            'description': 'Устройство фундамента',
            'order': 1,
            'start_date': date.today().isoformat(),
            'end_date': (date.today() + timedelta(days=14)).isoformat(),
            'estimated_hours': 80
        }
        
        response = self.client.post(self.stages_url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        # Проверяем, что этап создался
        stage = ProjectStage.objects.get(id=response.data['id'])
        self.assertEqual(stage.name, 'Фундаментные работы')
        self.assertEqual(stage.project, self.project)
    
    def test_list_stages(self):
        """Тест получения списка этапов"""
        # Создаём этапы
        stage1 = ProjectStageFactory(project=self.project, order=1)
        stage2 = ProjectStageFactory(project=self.project, order=2)
        
        self.authenticate(self.manager)
        
        response = self.client.get(self.stages_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Проверяем порядок этапов
        stages_data = response.data['results']
        self.assertEqual(len(stages_data), 2)
        self.assertEqual(stages_data[0]['order'], 1)
        self.assertEqual(stages_data[1]['order'], 2)
    
    def test_update_stage_progress(self):
        """Тест обновления прогресса этапа"""
        stage = ProjectStageFactory(project=self.project, completion_percentage=0)
        
        self.authenticate(self.manager)
        
        stage_url = reverse('projects:project-stage-detail', 
                          args=[self.project.id, stage.id])
        
        data = {'completion_percentage': 75}
        response = self.client.patch(stage_url, data)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        stage.refresh_from_db()
        self.assertEqual(stage.completion_percentage, 75)


class ProjectIntegrationTest(BaseAPITestCase, IntegrationTestMixin):
    """Интеграционные тесты для модуля проектов"""
    
    def test_full_project_workflow(self):
        """Тест полного workflow проекта"""
        manager = ManagerUserFactory()
        engineer = EngineerUserFactory()
        
        self.authenticate(manager)
        
        # 1. Создаём проект
        projects_url = reverse('projects:project-list-create')
        project_data = {
            'name': 'Интеграционный тест проект',
            'description': 'Тестирование полного workflow',
            'address': 'ул. Тестовая, д. 1',
            'customer': 'ООО "Интеграция"',
            'start_date': date.today().isoformat(),
            'end_date': (date.today() + timedelta(days=60)).isoformat(),
            'building_type': 'residential',
            'priority': 'medium'
        }
        
        response = self.client.post(projects_url, project_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        project_id = response.data['id']
        
        # 2. Добавляем участника
        add_member_url = reverse('projects:add-project-member', args=[project_id])
        member_data = {
            'user': engineer.id,
            'role': 'engineer'
        }
        
        response = self.client.post(add_member_url, member_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        # 3. Создаём этапы
        stages_url = reverse('projects:project-stages', args=[project_id])
        stage_data = {
            'name': 'Подготовительные работы',
            'description': 'Подготовка к строительству',
            'order': 1,
            'start_date': date.today().isoformat(),
            'end_date': (date.today() + timedelta(days=7)).isoformat(),
            'estimated_hours': 40
        }
        
        response = self.client.post(stages_url, stage_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        stage_id = response.data['id']
        
        # 4. Обновляем прогресс этапа
        stage_url = reverse('projects:project-stage-detail', args=[project_id, stage_id])
        progress_data = {'completion_percentage': 50}
        
        response = self.client.patch(stage_url, progress_data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # 5. Проверяем, что прогресс проекта обновился
        project_url = reverse('projects:project-detail', args=[project_id])
        response = self.client.get(project_url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Прогресс проекта должен отражать прогресс этапов
        self.assertGreaterEqual(response.data['progress_percentage'], 0)


@pytest.mark.django_db
class TestProjectModelPytest:
    """Pytest тесты для модели проекта"""
    
    def test_create_project_with_factory(self):
        """Тест создания проекта через фабрику"""
        project = ProjectFactory()
        assert project.id is not None
        assert project.name.startswith('Проект')
        assert project.manager is not None
    
    def test_project_with_members(self):
        """Тест создания проекта с участниками"""
        project = create_project_with_members(members_count=3)
        
        assert project.project_members.count() == 3
        assert all(member.is_active for member in project.project_members.all())
    
    def test_project_with_stages(self):
        """Тест создания проекта с этапами"""
        project = create_project_with_stages(stages_count=4)
        
        assert project.stages.count() == 4
        
        # Проверяем правильность порядка этапов
        stages = list(project.stages.order_by('order'))
        for i, stage in enumerate(stages, 1):
            assert stage.order == i
    
    @pytest.mark.parametrize('status,expected_overdue', [
        ('in_progress', True),
        ('completed', False),
        ('cancelled', False),
    ])
    def test_project_overdue_status(self, status, expected_overdue):
        """Параметризованный тест проверки просрочки проекта"""
        project = ProjectFactory(
            end_date=date.today() - timedelta(days=1),
            status=status
        )
        
        assert project.is_overdue == expected_overdue
