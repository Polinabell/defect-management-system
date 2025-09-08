"""
Конфигурация pytest и общие фикстуры для тестирования
"""

import pytest
import os
from datetime import datetime, timedelta
from django.conf import settings
from django.test import override_settings
from django.core.management import call_command
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from .factories import (
    UserFactory, ManagerUserFactory, EngineerUserFactory,
    ProjectFactory, DefectFactory, DefectCategoryFactory,
    ReportFactory, ReportTemplateFactory
)

User = get_user_model()


# Конфигурация базы данных для тестов
@pytest.fixture(scope='session')
def django_db_setup():
    """Настройка базы данных для тестов"""
    settings.DATABASES['default'] = {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:',
        'TEST': {
            'NAME': ':memory:',
        },
    }


# Фикстуры пользователей
@pytest.fixture
def user():
    """Базовый пользователь"""
    return UserFactory()


@pytest.fixture
def manager():
    """Пользователь-менеджер"""
    return ManagerUserFactory()


@pytest.fixture
def engineer():
    """Пользователь-инженер"""
    return EngineerUserFactory()


@pytest.fixture
def observer():
    """Пользователь-наблюдатель"""
    return UserFactory(role='observer')


# Фикстуры проектов
@pytest.fixture
def project(manager):
    """Базовый проект"""
    return ProjectFactory(manager=manager)


@pytest.fixture
def project_with_team(manager):
    """Проект с командой"""
    project = ProjectFactory(manager=manager)
    
    # Добавляем инженеров
    engineers = EngineerUserFactory.create_batch(3)
    for engineer in engineers:
        project.add_member(engineer, role='engineer')
    
    # Добавляем наблюдателя
    observer = UserFactory(role='observer')
    project.add_member(observer, role='observer')
    
    return project


@pytest.fixture
def multiple_projects(manager):
    """Несколько проектов"""
    projects = []
    for i in range(5):
        project = ProjectFactory(manager=manager, name=f'Проект {i+1}')
        projects.append(project)
    return projects


# Фикстуры дефектов
@pytest.fixture
def category():
    """Категория дефектов"""
    return DefectCategoryFactory()


@pytest.fixture
def multiple_categories():
    """Несколько категорий дефектов"""
    return DefectCategoryFactory.create_batch(10)


@pytest.fixture
def defect(project, engineer, category):
    """Базовый дефект"""
    return DefectFactory(
        project=project,
        author=engineer,
        category=category
    )


@pytest.fixture
def defects_dataset(project_with_team, multiple_categories):
    """Набор дефектов для тестирования"""
    defects = []
    
    # Создаём дефекты с разными статусами
    statuses = ['new', 'in_progress', 'review', 'closed', 'cancelled']
    priorities = ['low', 'medium', 'high', 'critical']
    severities = ['minor', 'major', 'critical', 'blocker']
    
    for i in range(50):
        defect = DefectFactory(
            project=project_with_team,
            category=multiple_categories[i % len(multiple_categories)],
            status=statuses[i % len(statuses)],
            priority=priorities[i % len(priorities)],
            severity=severities[i % len(severities)],
            title=f'Тестовый дефект {i+1}'
        )
        defects.append(defect)
    
    return defects


# Фикстуры отчётов
@pytest.fixture
def report_template():
    """Шаблон отчёта"""
    return ReportTemplateFactory()


@pytest.fixture
def report(manager):
    """Базовый отчёт"""
    return ReportFactory(created_by=manager)


# Фикстуры API клиента
@pytest.fixture
def api_client():
    """API клиент"""
    return APIClient()


@pytest.fixture
def authenticated_client(api_client, manager):
    """Аутентифицированный API клиент"""
    api_client.force_authenticate(user=manager)
    return api_client


@pytest.fixture
def engineer_client(api_client, engineer):
    """API клиент с аутентификацией инженера"""
    api_client.force_authenticate(user=engineer)
    return api_client


# Фикстуры настроек
@pytest.fixture
def email_backend():
    """Настройка email backend для тестов"""
    with override_settings(EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend'):
        yield


@pytest.fixture
def cache_settings():
    """Настройка кэширования для тестов"""
    with override_settings(
        CACHES={
            'default': {
                'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
            }
        }
    ):
        yield


@pytest.fixture
def media_root(tmp_path):
    """Временная директория для медиа файлов"""
    media_root = tmp_path / "media"
    media_root.mkdir()
    
    with override_settings(MEDIA_ROOT=media_root):
        yield media_root


@pytest.fixture
def celery_settings():
    """Настройка Celery для тестов"""
    with override_settings(
        CELERY_TASK_ALWAYS_EAGER=True,
        CELERY_TASK_EAGER_PROPAGATES=True,
    ):
        yield


# Фикстуры для тестирования производительности
@pytest.fixture
def performance_data():
    """Большой набор данных для тестов производительности"""
    # Создаём много пользователей
    managers = ManagerUserFactory.create_batch(10)
    engineers = EngineerUserFactory.create_batch(50)
    
    # Создаём много проектов
    projects = []
    for manager in managers:
        projects.extend(ProjectFactory.create_batch(5, manager=manager))
    
    # Создаём категории
    categories = DefectCategoryFactory.create_batch(20)
    
    # Создаём много дефектов
    defects = []
    for i in range(1000):
        defect = DefectFactory(
            project=projects[i % len(projects)],
            category=categories[i % len(categories)],
            author=engineers[i % len(engineers)]
        )
        defects.append(defect)
    
    return {
        'managers': managers,
        'engineers': engineers,
        'projects': projects,
        'categories': categories,
        'defects': defects
    }


# Маркеры pytest
def pytest_configure(config):
    """Конфигурация pytest"""
    config.addinivalue_line(
        "markers", "slow: marks tests as slow (deselect with '-m \"not slow\"')"
    )
    config.addinivalue_line(
        "markers", "stress: marks tests as stress tests"
    )
    config.addinivalue_line(
        "markers", "integration: marks tests as integration tests"
    )
    config.addinivalue_line(
        "markers", "unit: marks tests as unit tests"
    )
    config.addinivalue_line(
        "markers", "api: marks tests as API tests"
    )


# Хуки для управления базой данных
@pytest.fixture(autouse=True)
def enable_db_access_for_all_tests(db):
    """Включает доступ к БД для всех тестов"""
    pass


# Фикстура для очистки кэша
@pytest.fixture(autouse=True)
def clear_cache():
    """Очищает кэш перед каждым тестом"""
    from django.core.cache import cache
    cache.clear()


# Фикстуры для тестирования безопасности
@pytest.fixture
def malicious_user():
    """Злонамеренный пользователь для тестов безопасности"""
    return UserFactory(
        email='hacker@malicious.com',
        first_name='<script>alert("XSS")</script>',
        last_name='DROP TABLE users;--'
    )


@pytest.fixture
def sql_injection_payload():
    """Payload для тестирования SQL инъекций"""
    return "'; DROP TABLE defects; --"


@pytest.fixture
def xss_payload():
    """Payload для тестирования XSS"""
    return '<script>alert("XSS Attack")</script>'


# Фикстуры для тестирования файлов
@pytest.fixture
def test_image_file():
    """Тестовый файл изображения"""
    from django.core.files.uploadedfile import SimpleUploadedFile
    return SimpleUploadedFile(
        'test_image.jpg',
        b'fake image content',
        content_type='image/jpeg'
    )


@pytest.fixture
def test_document_file():
    """Тестовый файл документа"""
    from django.core.files.uploadedfile import SimpleUploadedFile
    return SimpleUploadedFile(
        'test_document.pdf',
        b'fake pdf content',
        content_type='application/pdf'
    )


@pytest.fixture
def malicious_file():
    """Вредоносный файл для тестов безопасности"""
    from django.core.files.uploadedfile import SimpleUploadedFile
    return SimpleUploadedFile(
        'malicious.exe',
        b'fake executable content',
        content_type='application/x-executable'
    )


# Фикстуры для тестирования временных интервалов
@pytest.fixture
def date_ranges():
    """Различные временные интервалы для тестов"""
    today = datetime.now().date()
    
    return {
        'today': (today, today),
        'week': (today - timedelta(days=7), today),
        'month': (today - timedelta(days=30), today),
        'quarter': (today - timedelta(days=90), today),
        'year': (today - timedelta(days=365), today),
    }


# Фикстуры для мокирования внешних сервисов
@pytest.fixture
def mock_email_service(mocker):
    """Мок для email сервиса"""
    return mocker.patch('django.core.mail.send_mail')


@pytest.fixture
def mock_file_storage(mocker):
    """Мок для файлового хранилища"""
    return mocker.patch('django.core.files.storage.default_storage')


@pytest.fixture
def mock_celery_task(mocker):
    """Мок для Celery задач"""
    return mocker.patch('celery.Task.delay')


# Фикстуры для логирования
@pytest.fixture
def capture_logs(caplog):
    """Захват логов для тестирования"""
    return caplog


# Cleanup фикстуры
@pytest.fixture(autouse=True)
def cleanup_uploaded_files():
    """Очистка загруженных файлов после тестов"""
    yield
    
    # Удаляем тестовые файлы
    import shutil
    import os
    
    if hasattr(settings, 'MEDIA_ROOT') and os.path.exists(settings.MEDIA_ROOT):
        for root, dirs, files in os.walk(settings.MEDIA_ROOT):
            for file in files:
                if 'test' in file.lower():
                    try:
                        os.remove(os.path.join(root, file))
                    except OSError:
                        pass  # Игнорируем ошибки удаления
