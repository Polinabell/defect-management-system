"""
Фабрики для создания тестовых данных с Factory Boy
"""

import factory
from factory.django import DjangoModelFactory
from factory import SubFactory, LazyAttribute, Sequence
from django.contrib.auth import get_user_model
from datetime import date, timedelta
from apps.projects.models import Project, ProjectStage, ProjectMember
from apps.defects.models import Defect, DefectCategory, DefectFile, DefectComment
from apps.reports.models import ReportTemplate, GeneratedReport

User = get_user_model()


class UserFactory(DjangoModelFactory):
    """Фабрика для создания пользователей"""
    
    class Meta:
        model = User
        django_get_or_create = ('username',)
    
    username = Sequence(lambda n: f'user_{n}')
    email = factory.LazyAttribute(lambda obj: f'{obj.username}@test.com')
    first_name = factory.Faker('first_name')
    last_name = factory.Faker('last_name')
    role = factory.Iterator(['engineer', 'manager', 'observer'])
    is_active = True
    is_staff = False
    is_superuser = False
    
    @factory.post_generation
    def password(self, create, extracted, **kwargs):
        """Устанавливаем пароль после создания"""
        if not create:
            return
        
        password = extracted or 'testpass123'
        self.set_password(password)
        self.save()


class AdminUserFactory(UserFactory):
    """Фабрика для создания администраторов"""
    
    username = Sequence(lambda n: f'admin_{n}')
    role = 'admin'
    is_staff = True
    is_superuser = True


class ManagerUserFactory(UserFactory):
    """Фабрика для создания менеджеров"""
    
    username = Sequence(lambda n: f'manager_{n}')
    role = 'manager'


class EngineerUserFactory(UserFactory):
    """Фабрика для создания инженеров"""
    
    username = Sequence(lambda n: f'engineer_{n}')
    role = 'engineer'


class ObserverUserFactory(UserFactory):
    """Фабрика для создания наблюдателей"""
    
    username = Sequence(lambda n: f'observer_{n}')
    role = 'observer'


class ProjectFactory(DjangoModelFactory):
    """Фабрика для создания проектов"""
    
    class Meta:
        model = Project
        django_get_or_create = ('name',)
    
    name = factory.Sequence(lambda n: f'Проект {n}')
    description = factory.Faker('text', max_nb_chars=500)
    address = factory.Faker('address')
    customer = factory.Faker('company')
    customer_contact = factory.Faker('name')
    customer_phone = factory.Faker('phone_number')
    customer_email = factory.Faker('email')
    manager = SubFactory(ManagerUserFactory)
    start_date = factory.LazyFunction(lambda: date.today())
    end_date = factory.LazyFunction(lambda: date.today() + timedelta(days=365))
    status = factory.Iterator(['planning', 'in_progress', 'on_hold', 'completed'])
    priority = factory.Iterator(['low', 'medium', 'high', 'critical'])
    building_type = factory.Iterator(['residential', 'commercial', 'industrial', 'infrastructure'])
    total_area = factory.Faker('pydecimal', left_digits=4, right_digits=2, positive=True)
    floors_count = factory.Faker('random_int', min=1, max=50)
    contract_number = factory.Sequence(lambda n: f'DOG-{n:04d}')
    contract_date = factory.LazyFunction(lambda: date.today() - timedelta(days=30))
    contract_amount = factory.Faker('pydecimal', left_digits=8, right_digits=2, positive=True)


class ProjectStageFactory(DjangoModelFactory):
    """Фабрика для создания этапов проекта"""
    
    class Meta:
        model = ProjectStage
    
    project = SubFactory(ProjectFactory)
    name = factory.Sequence(lambda n: f'Этап {n}')
    description = factory.Faker('text', max_nb_chars=300)
    order = factory.Sequence(lambda n: n)
    start_date = factory.LazyFunction(lambda: date.today())
    end_date = factory.LazyFunction(lambda: date.today() + timedelta(days=30))
    responsible = SubFactory(EngineerUserFactory)
    status = factory.Iterator(['not_started', 'in_progress', 'completed', 'on_hold'])
    completion_percentage = factory.Faker('random_int', min=0, max=100)
    estimated_hours = factory.Faker('random_int', min=40, max=200)
    actual_hours = factory.Faker('random_int', min=30, max=250)


class ProjectMemberFactory(DjangoModelFactory):
    """Фабрика для создания участников проекта"""
    
    class Meta:
        model = ProjectMember
        django_get_or_create = ('project', 'user')
    
    project = SubFactory(ProjectFactory)
    user = SubFactory(EngineerUserFactory)
    role = factory.Iterator(['manager', 'engineer', 'observer'])
    is_active = True
    joined_at = factory.LazyFunction(lambda: date.today() - timedelta(days=10))


class DefectCategoryFactory(DjangoModelFactory):
    """Фабрика для создания категорий дефектов"""
    
    class Meta:
        model = DefectCategory
        django_get_or_create = ('name',)
    
    name = factory.Iterator([
        'Строительные работы',
        'Электрика',
        'Сантехника',
        'Отделочные работы',
        'Кровельные работы',
        'Фасадные работы'
    ])
    description = factory.Faker('text', max_nb_chars=200)
    color = factory.Iterator(['#ff5722', '#2196f3', '#4caf50', '#ff9800', '#9c27b0', '#607d8b'])
    icon = factory.Iterator(['build', 'electrical_services', 'plumbing', 'format_paint', 'roofing', 'apartment'])
    is_active = True
    order = factory.Sequence(lambda n: n)


class DefectFactory(DjangoModelFactory):
    """Фабрика для создания дефектов"""
    
    class Meta:
        model = Defect
    
    title = factory.Sequence(lambda n: f'Дефект {n}')
    description = factory.Faker('text', max_nb_chars=500)
    project = SubFactory(ProjectFactory)
    stage = SubFactory(ProjectStageFactory)
    category = SubFactory(DefectCategoryFactory)
    priority = factory.Iterator(['low', 'medium', 'high', 'critical'])
    severity = factory.Iterator(['cosmetic', 'minor', 'major', 'critical', 'blocking'])
    location = factory.Faker('text', max_nb_chars=200)
    floor = factory.Faker('random_element', elements=['1', '2', '3', '4', '5', 'Подвал', 'Чердак'])
    room = factory.Faker('random_element', elements=[
        'Кухня', 'Гостиная', 'Спальня', 'Ванная', 'Коридор', 'Балкон'
    ])
    author = SubFactory(EngineerUserFactory)
    assignee = SubFactory(EngineerUserFactory)
    status = factory.Iterator(['new', 'in_progress', 'review', 'closed', 'cancelled'])
    due_date = factory.LazyFunction(lambda: date.today() + timedelta(days=7))
    estimated_cost = factory.Faker('pydecimal', left_digits=5, right_digits=2, positive=True)
    
    @factory.post_generation
    def set_defect_number(self, create, extracted, **kwargs):
        """Генерируем номер дефекта после создания"""
        if not create:
            return
        
        if not self.defect_number:
            # Простая генерация номера для тестов
            self.defect_number = f"DEF-{self.project.id:03d}-{self.id:04d}"
            self.save()


class DefectFileFactory(DjangoModelFactory):
    """Фабрика для создания файлов дефектов"""
    
    class Meta:
        model = DefectFile
    
    defect = SubFactory(DefectFactory)
    filename = factory.Faker('file_name', extension='jpg')
    file_type = factory.Iterator(['image', 'document', 'video'])
    file_size = factory.Faker('random_int', min=1024, max=5242880)  # 1KB - 5MB
    mime_type = factory.Iterator(['image/jpeg', 'image/png', 'application/pdf', 'video/mp4'])
    description = factory.Faker('text', max_nb_chars=200)
    uploaded_by = SubFactory(EngineerUserFactory)
    is_main = False


class DefectCommentFactory(DjangoModelFactory):
    """Фабрика для создания комментариев к дефектам"""
    
    class Meta:
        model = DefectComment
    
    defect = SubFactory(DefectFactory)
    author = SubFactory(EngineerUserFactory)
    content = factory.Faker('text', max_nb_chars=300)
    comment_type = factory.Iterator(['comment', 'status_change', 'assignment', 'resolution'])
    is_internal = factory.Faker('boolean', chance_of_getting_true=30)


class ReportTemplateFactory(DjangoModelFactory):
    """Фабрика для создания шаблонов отчётов"""
    
    class Meta:
        model = ReportTemplate
        django_get_or_create = ('name',)
    
    name = factory.Sequence(lambda n: f'Шаблон отчёта {n}')
    description = factory.Faker('text', max_nb_chars=300)
    report_type = factory.Iterator([
        'project_summary', 'defects_analysis', 'performance_report', 'timeline_report'
    ])
    output_format = factory.Iterator(['pdf', 'excel', 'csv', 'json'])
    filter_config = factory.LazyFunction(lambda: {})
    display_config = factory.LazyFunction(lambda: {})
    is_public = factory.Faker('boolean', chance_of_getting_true=50)
    is_active = True
    created_by = SubFactory(ManagerUserFactory)


class GeneratedReportFactory(DjangoModelFactory):
    """Фабрика для создания сгенерированных отчётов"""
    
    class Meta:
        model = GeneratedReport
    
    template = SubFactory(ReportTemplateFactory)
    name = factory.Sequence(lambda n: f'Отчёт {n}')
    description = factory.Faker('text', max_nb_chars=200)
    project = SubFactory(ProjectFactory)
    date_from = factory.LazyFunction(lambda: date.today() - timedelta(days=30))
    date_to = factory.LazyFunction(lambda: date.today())
    filter_params = factory.LazyFunction(lambda: {})
    status = factory.Iterator(['pending', 'processing', 'completed', 'failed'])
    generated_by = SubFactory(ManagerUserFactory)
    file_size = factory.Faker('random_int', min=1024, max=10485760)  # 1KB - 10MB


# Создаём удобные функции для быстрого создания связанных объектов

def create_project_with_members(members_count=3):
    """Создаёт проект с участниками"""
    project = ProjectFactory()
    for _ in range(members_count):
        ProjectMemberFactory(project=project)
    return project


def create_project_with_stages(stages_count=5):
    """Создаёт проект с этапами"""
    project = ProjectFactory()
    for i in range(stages_count):
        ProjectStageFactory(project=project, order=i+1)
    return project


def create_defect_with_files(files_count=3):
    """Создаёт дефект с файлами"""
    defect = DefectFactory()
    for i in range(files_count):
        DefectFileFactory(defect=defect, is_main=(i == 0))
    return defect


def create_defect_with_comments(comments_count=5):
    """Создаёт дефект с комментариями"""
    defect = DefectFactory()
    for _ in range(comments_count):
        DefectCommentFactory(defect=defect)
    return defect


def create_full_project():
    """Создаёт полный проект с этапами, участниками и дефектами"""
    project = ProjectFactory()
    
    # Добавляем участников
    for _ in range(3):
        ProjectMemberFactory(project=project)
    
    # Добавляем этапы
    stages = []
    for i in range(4):
        stage = ProjectStageFactory(project=project, order=i+1)
        stages.append(stage)
    
    # Добавляем дефекты
    for stage in stages:
        for _ in range(2):
            defect = DefectFactory(project=project, stage=stage)
            # Добавляем файлы и комментарии к дефекту
            DefectFileFactory(defect=defect, is_main=True)
            DefectCommentFactory(defect=defect)
    
    return project
