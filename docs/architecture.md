# Архитектура системы
## Система управления дефектами на строительных объектах

---

## 1. Общая архитектура системы

### 1.1 Архитектурный стиль
Система построена на основе трёхуровневой архитектуры с использованием микросервисного подхода в рамках монолитного приложения (модульный монолит).

```
┌─────────────────────────────────────────────────────────────┐
│                     Presentation Layer                      │
├─────────────────────────────────────────────────────────────┤
│                     Business Logic Layer                    │
├─────────────────────────────────────────────────────────────┤
│                     Data Access Layer                       │
└─────────────────────────────────────────────────────────────┘
```

### 1.2 Компонентная диаграмма

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Web Browser   │    │  Mobile Device  │    │   API Client    │
└─────────┬───────┘    └─────────┬───────┘    └─────────┬───────┘
          │                      │                      │
          └──────────────────────┼──────────────────────┘
                                 │
                    ┌─────────────┴──────────────┐
                    │       Load Balancer        │
                    │         (Nginx)            │
                    └─────────────┬──────────────┘
                                 │
          ┌──────────────────────┼──────────────────────┐
          │                      │                      │
┌─────────┴───────┐    ┌─────────┴───────┐    ┌─────────┴───────┐
│   Frontend      │    │   Frontend      │    │   Frontend      │
│   (React)       │    │   (React)       │    │   (React)       │
│   Instance 1    │    │   Instance 2    │    │   Instance N    │
└─────────┬───────┘    └─────────┬───────┘    └─────────┬───────┘
          │                      │                      │
          └──────────────────────┼──────────────────────┘
                                 │
                    ┌─────────────┴──────────────┐
                    │         API Gateway        │
                    │     (Django + DRF)         │
                    └─────────────┬──────────────┘
                                 │
          ┌──────────────────────┼──────────────────────┐
          │                      │                      │
┌─────────┴───────┐    ┌─────────┴───────┐    ┌─────────┴───────┐
│   Backend       │    │   Backend       │    │   Backend       │
│   (Django)      │    │   (Django)      │    │   (Django)      │
│   Instance 1    │    │   Instance 2    │    │   Instance N    │
└─────────┬───────┘    └─────────┬───────┘    └─────────┬───────┘
          │                      │                      │
          └──────────────────────┼──────────────────────┘
                                 │
          ┌─────────────────────────────────────────────┐
          │                                             │
┌─────────┴───────┐              ┌─────────────────────┴┐
│   PostgreSQL    │              │        Redis         │
│   (Primary)     │              │      (Cache &        │
│                 │              │       Sessions)      │
└─────────┬───────┘              └──────────────────────┘
          │
┌─────────┴───────┐
│   PostgreSQL    │
│   (Replica)     │
└─────────────────┘
```

### 1.3 Технологический стек

#### Frontend
- **React 18+** - библиотека для создания пользовательских интерфейсов
- **TypeScript** - типизированный JavaScript для повышения надёжности
- **Material-UI (MUI)** - библиотека компонентов следующая Material Design
- **React Router** - маршрутизация в SPA
- **Axios** - HTTP клиент для API запросов
- **React Query** - управление состоянием сервера и кэширование
- **Chart.js** - библиотека для создания интерактивных графиков

#### Backend  
- **Python 3.11+** - основной язык программирования
- **Django 4.2+** - веб-фреймворк
- **Django REST Framework** - создание REST API
- **PostgreSQL 15+** - основная база данных
- **Redis 7+** - кэширование и хранение сессий
- **Celery** - асинхронная обработка задач
- **Gunicorn** - WSGI HTTP Server

#### DevOps & Infrastructure
- **Docker & Docker Compose** - контейнеризация
- **Nginx** - веб-сервер и load balancer
- **GitHub Actions** - CI/CD пайплайны
- **PostgreSQL** - СУБД
- **Redis** - кэш и брокер сообщений

---

## 2. Детальная архитектура backend

### 2.1 Структура Django приложения

```
backend/
├── config/                 # Настройки проекта
│   ├── settings/
│   │   ├── base.py        # Базовые настройки
│   │   ├── development.py  # Настройки для разработки
│   │   ├── production.py   # Настройки для продакшена
│   │   └── testing.py      # Настройки для тестирования
│   ├── urls.py            # Главный URL конфигуратор
│   └── wsgi.py            # WSGI приложение
├── apps/                   # Django приложения
│   ├── users/             # Управление пользователями
│   ├── projects/          # Управление проектами
│   ├── defects/           # Управление дефектами
│   ├── reports/           # Отчёты и аналитика
│   └── common/            # Общие компоненты
├── static/                # Статические файлы
├── media/                 # Пользовательские файлы
├── requirements/          # Python зависимости
│   ├── base.txt
│   ├── development.txt
│   └── production.txt
└── manage.py
```

### 2.2 Модульная архитектура

#### Apps.Users - Управление пользователями
```python
apps/users/
├── models.py              # Модели User, Profile
├── serializers.py         # DRF сериализаторы
├── views.py               # API views
├── permissions.py         # Права доступа
├── authentication.py      # JWT аутентификация
├── urls.py                # URL маршруты
└── tests/                 # Тесты модуля
```

**Ключевые компоненты:**
- Кастомная модель User
- JWT аутентификация
- Система ролей и разрешений
- Профили пользователей

#### Apps.Projects - Управление проектами
```python
apps/projects/
├── models.py              # Project, ProjectStage, ProjectMember
├── serializers.py         # API сериализаторы
├── views.py               # ViewSets для CRUD
├── permissions.py         # Права доступа к проектам
├── filters.py             # Фильтры для проектов
└── tests/
```

**Ключевые компоненты:**
- Модель проекта с этапами
- Управление участниками
- Контроль доступа по проектам

#### Apps.Defects - Управление дефектами
```python
apps/defects/
├── models.py              # Defect, DefectComment, DefectFile
├── serializers.py         # Сериализаторы с валидацией
├── views.py               # API для дефектов
├── permissions.py         # Права на дефекты
├── filters.py             # Сложные фильтры и поиск
├── services.py            # Бизнес-логика
├── tasks.py               # Celery задачи
└── tests/
```

**Ключевые компоненты:**
- Workflow статусов дефектов
- Файловые вложения
- Система комментариев
- Полнотекстовый поиск

#### Apps.Reports - Отчёты и аналитика
```python
apps/reports/
├── models.py              # Модели для отчётов
├── serializers.py         # Сериализаторы данных
├── views.py               # API для отчётов
├── generators.py          # Генераторы отчётов
├── analytics.py           # Аналитические функции
└── tests/
```

**Ключевые компоненты:**
- Генераторы CSV/Excel отчётов
- Аналитические запросы
- Дашборд данные

### 2.3 Слои приложения

#### Presentation Layer (Views)
- **API Views** - REST API endpoints
- **Permissions** - контроль доступа
- **Serializers** - валидация и сериализация данных
- **Filters** - фильтрация и поиск

#### Business Logic Layer (Services)
- **Services** - бизнес-логика приложения
- **Tasks** - асинхронные задачи (Celery)
- **Validators** - кастомная валидация
- **Utils** - вспомогательные функции

#### Data Access Layer (Models)
- **Models** - ORM модели Django
- **Managers** - кастомные менеджеры запросов
- **Migrations** - миграции базы данных

---

## 3. Frontend архитектура

### 3.1 Структура React приложения

```
frontend/
├── public/                # Публичные файлы
├── src/
│   ├── components/        # React компоненты
│   │   ├── common/        # Общие компоненты
│   │   ├── layout/        # Компоненты layout
│   │   ├── forms/         # Формы
│   │   └── charts/        # Графики и диаграммы
│   ├── pages/             # Страницы приложения
│   │   ├── auth/          # Страницы аутентификации
│   │   ├── projects/      # Страницы проектов
│   │   ├── defects/       # Страницы дефектов
│   │   └── reports/       # Страницы отчётов
│   ├── services/          # API сервисы
│   │   ├── api.ts         # Axios конфигурация
│   │   ├── auth.ts        # Аутентификация API
│   │   ├── projects.ts    # Проекты API
│   │   └── defects.ts     # Дефекты API
│   ├── hooks/             # Custom React hooks
│   ├── contexts/          # React contexts
│   ├── utils/             # Утилиты
│   ├── types/             # TypeScript типы
│   └── styles/            # Стили и темы
├── package.json
└── tsconfig.json
```

### 3.2 Архитектурные паттерны

#### Component Architecture
```
App
├── Layout
│   ├── Header
│   ├── Sidebar
│   └── Main
│       ├── ProjectsPage
│       │   ├── ProjectsList
│       │   ├── ProjectForm
│       │   └── ProjectDetails
│       ├── DefectsPage
│       │   ├── DefectsList
│       │   ├── DefectForm
│       │   └── DefectDetails
│       └── ReportsPage
│           ├── Dashboard
│           ├── Charts
│           └── Export
```

#### State Management
- **React Query** - серверное состояние и кэширование
- **React Context** - глобальное состояние приложения
- **Local State** - локальное состояние компонентов
- **Form State** - состояние форм (React Hook Form)

---

## 4. База данных

### 4.1 ER-диаграмма

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│      User       │    │    Project      │    │   ProjectStage  │
├─────────────────┤    ├─────────────────┤    ├─────────────────┤
│ id (PK)         │    │ id (PK)         │    │ id (PK)         │
│ username        │◄──┐│ name            │◄──┐│ name            │
│ email           │   ││ description     │   ││ description     │
│ password_hash   │   ││ address         │   ││ start_date      │
│ first_name      │   ││ customer        │   ││ end_date        │
│ last_name       │   ││ start_date      │   ││ project_id (FK) │
│ role            │   ││ end_date        │   ││ responsible_id  │
│ is_active       │   ││ manager_id (FK) │   │└─────────────────┘
│ created_at      │   │└─────────────────┘   │
│ updated_at      │   │                      │
└─────────────────┘   │                      │
          │           │                      │
          │           │                      │
┌─────────┴───────────┴──┐                   │
│    ProjectMember       │                   │
├────────────────────────┤                   │
│ id (PK)                │                   │
│ project_id (FK)        │───────────────────┘
│ user_id (FK)           │
│ role                   │
│ joined_at              │
└────────────────────────┘
          │
          │
┌─────────┴───────┐    ┌─────────────────┐    ┌─────────────────┐
│     Defect      │    │  DefectComment  │    │   DefectFile    │
├─────────────────┤    ├─────────────────┤    ├─────────────────┤
│ id (PK)         │    │ id (PK)         │    │ id (PK)         │
│ title           │    │ content         │    │ file            │
│ description     │    │ defect_id (FK)  │    │ filename        │
│ project_id (FK) │◄───┤ author_id (FK)  │    │ file_type       │
│ stage_id (FK)   │    │ created_at      │    │ file_size       │
│ category        │    └─────────────────┘    │ defect_id (FK)  │
│ priority        │                           │ uploaded_at     │
│ status          │                           └─────────────────┘
│ location        │
│ author_id (FK)  │
│ assignee_id     │
│ due_date        │
│ created_at      │
│ updated_at      │
└─────────────────┘
```

### 4.2 Основные модели данных

#### User Model
```python
class User(AbstractUser):
    class Role(models.TextChoices):
        ADMIN = 'admin', 'Администратор'
        MANAGER = 'manager', 'Менеджер'
        ENGINEER = 'engineer', 'Инженер'
        OBSERVER = 'observer', 'Наблюдатель'
    
    role = models.CharField(max_length=20, choices=Role.choices)
    phone = models.CharField(max_length=20, blank=True)
    position = models.CharField(max_length=100, blank=True)
```

#### Project Model
```python
class Project(models.Model):
    name = models.CharField(max_length=200, unique=True)
    description = models.TextField()
    address = models.TextField()
    customer = models.CharField(max_length=200)
    manager = models.ForeignKey(User, on_delete=models.PROTECT)
    start_date = models.DateField()
    end_date = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)
```

#### Defect Model
```python
class Defect(models.Model):
    class Status(models.TextChoices):
        NEW = 'new', 'Новый'
        IN_PROGRESS = 'in_progress', 'В работе'
        REVIEW = 'review', 'На проверке'
        CLOSED = 'closed', 'Закрыт'
        CANCELLED = 'cancelled', 'Отменён'
    
    class Priority(models.TextChoices):
        LOW = 'low', 'Низкий'
        MEDIUM = 'medium', 'Средний'
        HIGH = 'high', 'Высокий'
        CRITICAL = 'critical', 'Критический'
    
    title = models.CharField(max_length=200)
    description = models.TextField()
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    category = models.CharField(max_length=100)
    priority = models.CharField(max_length=20, choices=Priority.choices)
    status = models.CharField(max_length=20, choices=Status.choices)
    author = models.ForeignKey(User, on_delete=models.PROTECT)
    assignee = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    due_date = models.DateField(null=True, blank=True)
```

---

## 5. API архитектура

### 5.1 REST API структура

```
/api/v1/
├── auth/
│   ├── login/          POST    # Вход в систему
│   ├── logout/         POST    # Выход из системы
│   ├── refresh/        POST    # Обновление токена
│   └── me/             GET     # Профиль пользователя
├── users/
│   ├── /               GET     # Список пользователей
│   ├── /               POST    # Создание пользователя
│   ├── /{id}/          GET     # Детали пользователя
│   ├── /{id}/          PUT     # Обновление пользователя
│   └── /{id}/          DELETE  # Удаление пользователя
├── projects/
│   ├── /               GET     # Список проектов
│   ├── /               POST    # Создание проекта
│   ├── /{id}/          GET     # Детали проекта
│   ├── /{id}/          PUT     # Обновление проекта
│   ├── /{id}/members/  GET     # Участники проекта
│   └── /{id}/stages/   GET     # Этапы проекта
├── defects/
│   ├── /               GET     # Список дефектов
│   ├── /               POST    # Создание дефекта
│   ├── /{id}/          GET     # Детали дефекта
│   ├── /{id}/          PUT     # Обновление дефекта
│   ├── /{id}/comments/ GET     # Комментарии к дефекту
│   ├── /{id}/files/    GET     # Файлы дефекта
│   └── /{id}/history/  GET     # История изменений
└── reports/
    ├── dashboard/      GET     # Данные дашборда
    ├── export/         POST    # Экспорт отчётов
    └── analytics/      GET     # Аналитические данные
```

### 5.2 Аутентификация и авторизация

#### JWT Authentication
```
Authorization: Bearer <JWT_TOKEN>
```

#### Permissions
- **IsAuthenticated** - только аутентифицированные пользователи
- **IsAdminUser** - только администраторы
- **IsProjectMember** - только участники проекта
- **IsDefectAuthorOrAssignee** - автор или исполнитель дефекта

---

## 6. Безопасность

### 6.1 Уровни защиты

#### Application Level
- JWT токены с ограниченным временем жизни
- Хеширование паролей (bcrypt)
- Валидация входных данных
- Ограничение размера загружаемых файлов

#### Network Level
- HTTPS для всех соединений
- CORS политики
- Rate limiting для API
- Firewall правила

#### Database Level
- Параметризованные запросы (ORM)
- Шифрование чувствительных данных
- Регулярные резервные копии
- Права доступа к БД

### 6.2 OWASP Top 10 Protection

1. **Injection** - ORM Django, валидация данных
2. **Broken Authentication** - JWT, защита от brute force
3. **Sensitive Data Exposure** - HTTPS, шифрование БД
4. **XML External Entities** - не используется XML
5. **Broken Access Control** - система разрешений Django
6. **Security Misconfiguration** - проверенные настройки
7. **Cross-Site Scripting** - автоматическое экранирование
8. **Insecure Deserialization** - безопасные сериализаторы
9. **Components with Known Vulnerabilities** - регулярные обновления
10. **Insufficient Logging** - подробные логи безопасности

---

## 7. Масштабирование

### 7.1 Горизонтальное масштабирование

#### Frontend
- Множественные экземпляры за load balancer
- CDN для статических ресурсов
- Кэширование в браузере

#### Backend
- Множественные экземпляры Django
- Load balancing с Nginx
- Stateless сессии (JWT)

#### Database
- Read replicas для PostgreSQL
- Connection pooling
- Кэширование в Redis

### 7.2 Производительность

#### Кэширование
- Redis для сессий и кэша
- Кэширование запросов к БД
- Кэширование статического контента

#### Оптимизация запросов
- Использование select_related/prefetch_related
- Индексы для часто используемых полей
- Пагинация больших результатов

#### Асинхронная обработка
- Celery для тяжёлых задач
- Генерация отчётов в фоне
- Отправка уведомлений

---

## 8. Мониторинг и логирование

### 8.1 Логирование

#### Application Logs
```python
LOGGING = {
    'version': 1,
    'loggers': {
        'defects': {
            'handlers': ['file', 'console'],
            'level': 'INFO',
        },
        'security': {
            'handlers': ['security_file'],
            'level': 'WARNING',
        }
    }
}
```

#### Логируемые события
- Все действия пользователей
- Ошибки приложения
- События безопасности
- Производительность API

### 8.2 Мониторинг

#### Health Checks
- `/health/` - общее состояние приложения
- `/health/db/` - состояние базы данных
- `/health/cache/` - состояние Redis

#### Метрики
- Время ответа API
- Использование памяти и CPU
- Количество активных пользователей
- Ошибки приложения

---

## 9. Развёртывание

### 9.1 Docker контейнеры

```yaml
version: '3.8'
services:
  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
  
  frontend:
    build: ./frontend
    environment:
      - NODE_ENV=production
  
  backend:
    build: ./backend
    environment:
      - DJANGO_SETTINGS_MODULE=config.settings.production
    
  postgres:
    image: postgres:15
    environment:
      - POSTGRES_DB=defects_db
  
  redis:
    image: redis:7-alpine
```

### 9.2 CI/CD Pipeline

#### GitHub Actions Workflow
1. **Тестирование** - запуск всех тестов
2. **Линтинг** - проверка качества кода
3. **Сборка** - создание Docker образов
4. **Деплой** - развёртывание на сервере
5. **Проверка** - smoke tests после деплоя

---

## 10. Планы развития

### 10.1 Ближайшие улучшения
- Мобильное приложение (React Native)
- Push уведомления
- Интеграция с внешними системами
- Расширенная аналитика

### 10.2 Долгосрочные планы
- Машинное обучение для классификации дефектов
- IoT интеграция с датчиками
- Blockchain для аудита изменений
- Микросервисная архитектура
