y# Система управления дефектами в строительстве

Современная веб-система для эффективного управления дефектами на строительных объектах с полным жизненным циклом от выявления до устранения.

[![CI/CD Pipeline](https://github.com/username/defect-management-system/actions/workflows/ci-cd.yml/badge.svg)](https://github.com/username/defect-management-system/actions/workflows/ci-cd.yml)
[![Coverage Status](https://codecov.io/gh/username/defect-management-system/branch/main/graph/badge.svg)](https://codecov.io/gh/username/defect-management-system)
[![Security Rating](https://sonarcloud.io/api/project_badges/measure?project=defect-management-system&metric=security_rating)](https://sonarcloud.io/dashboard?id=defect-management-system)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

## 🚀 Особенности системы

### Основной функционал
- **Управление дефектами**: Создание, назначение, отслеживание и закрытие дефектов
- **Управление проектами**: Структурированная работа с строительными объектами
- **Система ролей**: Менеджер, Инженер, Наблюдатель с различными правами доступа
- **Файловые вложения**: Фото, документы и схемы к дефектам
- **Комментарии**: Коммуникация команды в рамках дефекта
- **Отчётность**: Аналитические отчёты и экспорт в Excel/CSV
- **Уведомления**: Email и SMS уведомления о статусах

### Технические особенности
- **Современная архитектура**: Monolithic приложение с микросервисной готовностью
- **Высокая производительность**: Оптимизированные запросы и кэширование
- **Безопасность**: Полная защита от OWASP Top 10
- **Мониторинг**: Prometheus + Grafana для отслеживания метрик
- **Масштабируемость**: Docker Swarm/Kubernetes ready
- **CI/CD**: Автоматизированные тесты и деплой

## 🏗️ Архитектура системы

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Frontend      │    │   Backend       │    │   Database      │
│   React + TS    │◄───┤   Django + DRF  │◄───┤   PostgreSQL    │
│   Material-UI   │    │   Celery        │    │   Redis         │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         ▲                       ▲                       ▲
         │                       │                       │
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Nginx         │    │   Monitoring    │    │   File Storage  │
│   Load Balancer │    │   Prometheus    │    │   S3 / Local    │
│   SSL/TLS       │    │   Grafana       │    │   Media Files   │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## 🛠️ Технический стек

### Backend
- **Python 3.11** - язык программирования
- **Django 4.2** - веб-фреймворк
- **Django REST Framework** - API framework
- **PostgreSQL 15** - основная база данных
- **Redis 7** - кэширование и брокер сообщений
- **Celery** - асинхронные задачи
- **Gunicorn** - WSGI сервер

### Frontend
- **React 18** - UI библиотека
- **TypeScript** - типизированный JavaScript
- **Material-UI (MUI)** - UI компоненты
- **Redux Toolkit** - управление состоянием
- **React Router** - маршрутизация
- **Axios** - HTTP клиент

### Инфраструктура
- **Docker & Docker Compose** - контейнеризация
- **Nginx** - веб-сервер и load balancer
- **Prometheus** - сбор метрик
- **Grafana** - визуализация метрик
- **GitHub Actions** - CI/CD пайплайн

### Тестирование
- **Pytest** - тестирование backend
- **Jest + React Testing Library** - тестирование frontend
- **Factory Boy** - генерация тестовых данных
- **Coverage.py** - покрытие кода тестами

## 📋 Требования

### Минимальные требования
- **CPU**: 2 cores
- **RAM**: 4 GB
- **Disk**: 20 GB SSD
- **OS**: Linux (Ubuntu 20.04+), macOS, Windows 10+

### Рекомендуемые требования
- **CPU**: 4+ cores
- **RAM**: 8+ GB
- **Disk**: 50+ GB SSD
- **OS**: Linux (Ubuntu 22.04+)

### Программное обеспечение
- **Docker**: 20.10+
- **Docker Compose**: 2.0+
- **Git**: 2.30+

## 🚀 Быстрый старт

### 1. Клонирование репозитория
```bash
git clone https://github.com/username/defect-management-system.git
cd defect-management-system
```

### 2. Настройка переменных окружения
```bash
cp env.example .env
# Отредактируйте .env файл с вашими настройками
```

### 3. Запуск с Docker Compose
```bash
# Для разработки
docker-compose up -d

# Для production
docker-compose -f docker-compose.prod.yml up -d
```

### 4. Инициализация данных
```bash
# Выполнение миграций
docker-compose exec web python manage.py migrate

# Создание суперпользователя
docker-compose exec web python manage.py createsuperuser

# Загрузка начальных данных
docker-compose exec web python manage.py loaddata fixtures/initial_data.json
```

### 5. Открытие приложения
- **Основное приложение**: http://localhost
- **Django Admin**: http://localhost/admin
- **API Documentation**: http://localhost/api/docs
- **Grafana**: http://localhost:3000 (admin/admin)
- **Prometheus**: http://localhost:9090

## 🔧 Разработка

### Настройка среды разработки

1. **Установка Python зависимостей**:
```bash
cd backend
pip install -r requirements/development.txt
```

2. **Установка Node.js зависимостей**:
```bash
cd frontend
npm install
```

3. **Запуск в режиме разработки**:
```bash
# Backend
cd backend
python manage.py runserver

# Frontend
cd frontend
npm start
```

### Структура проекта
```
defect-management-system/
├── backend/                 # Django приложение
│   ├── apps/               # Django приложения
│   │   ├── users/          # Управление пользователями
│   │   ├── projects/       # Управление проектами
│   │   ├── defects/        # Управление дефектами
│   │   ├── reports/        # Система отчётов
│   │   └── common/         # Общие компоненты
│   ├── config/             # Настройки Django
│   ├── requirements/       # Python зависимости
│   └── tests/              # Тесты
├── frontend/               # React приложение
│   ├── src/
│   │   ├── components/     # React компоненты
│   │   ├── pages/          # Страницы
│   │   ├── store/          # Redux store
│   │   ├── services/       # API сервисы
│   │   └── types/          # TypeScript типы
│   └── public/             # Статические файлы
├── docker/                 # Docker конфигурации
├── .github/                # GitHub Actions
└── docs/                   # Документация
```

### Запуск тестов

```bash
# Backend тесты
cd backend
pytest

# Frontend тесты
cd frontend
npm test

# Интеграционные тесты
docker-compose -f docker-compose.test.yml up --abort-on-container-exit

# Покрытие кода
cd backend
pytest --cov=. --cov-report=html
```

### Линтинг и форматирование

```bash
# Python
cd backend
flake8 .
black .
isort .
mypy .

# TypeScript/JavaScript
cd frontend
npm run lint
npm run format
```

## 🔒 Безопасность

### Реализованные меры безопасности
- **OWASP Top 10 защита**
- **JWT аутентификация**
- **Rate limiting**
- **CSRF защита**
- **XSS защита**
- **SQL injection защита**
- **Валидация файлов**
- **Аудит логирование**
- **Шифрование паролей** (Argon2)
- **HTTPS принуждение**

### Конфигурация безопасности
```python
# Основные настройки безопасности в production
SECURE_SSL_REDIRECT = True
SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_BROWSER_XSS_FILTER = True
X_FRAME_OPTIONS = 'DENY'
```

## 📊 Мониторинг

### Доступные метрики
- **Производительность приложения**
- **Использование ресурсов**
- **Ошибки и исключения**
- **Количество запросов**
- **Время ответа API**
- **Статус задач Celery**
- **Метрики базы данных**

### Алерты
- **Высокая нагрузка CPU**
- **Нехватка памяти**
- **Медленные запросы**
- **Ошибки приложения**
- **Недоступность сервисов**

## 🚀 Деплой

### Production деплой

1. **Настройка production окружения**:
```bash
cp env.example .env.production
# Настройте production переменные
```

2. **Сборка и деплой**:
```bash
# Сборка образов
docker build -t defect-management:latest .

# Запуск в production
docker-compose -f docker-compose.prod.yml up -d

# Масштабирование
docker-compose -f docker-compose.prod.yml up -d --scale web=3
```

3. **Blue-Green деплой**:
```bash
# Скрипт в docker/deploy.sh
./docker/deploy.sh production
```

### CI/CD Pipeline
Автоматический деплой настроен через GitHub Actions:
- **Code Quality**: Линтинг и проверка типов
- **Testing**: Unit, integration, e2e тесты
- **Security**: Сканирование уязвимостей
- **Build**: Сборка Docker образов
- **Deploy**: Автоматический деплой в staging/production

## 📈 Производительность

### Оптимизация базы данных
- **Индексы** на часто используемые поля
- **Соединения (JOINs)** минимизированы
- **Пагинация** для больших наборов данных
- **Кэширование** запросов

### Кэширование
- **Redis** для кэширования данных
- **CDN** для статических файлов
- **Browser caching** с правильными заголовками
- **API response caching**

### Масштабируемость
- **Horizontal scaling** через Docker Swarm
- **Load balancing** с Nginx
- **Database replication** ready
- **Microservices** архитектура готова

## 🧪 Тестирование

### Покрытие тестами
- **Backend**: >90% покрытия
- **Frontend**: >85% покрытия
- **Integration**: Ключевые пользовательские сценарии
- **Load testing**: До 1000 одновременных пользователей

### Типы тестов
- **Unit tests**: Тестирование отдельных компонентов
- **Integration tests**: Тестирование взаимодействия компонентов
- **API tests**: Тестирование REST API
- **E2E tests**: Полные пользовательские сценарии
- **Load tests**: Тестирование производительности

## 📚 API Документация

### REST API
- **OpenAPI/Swagger**: Автоматически генерируемая документация
- **Postman Collection**: Коллекция для тестирования API
- **Authentication**: JWT токены
- **Versioning**: API версионирование
- **Rate Limiting**: Ограничения по запросам

### Основные эндпоинты
```
GET    /api/v1/projects/           # Список проектов
POST   /api/v1/projects/           # Создание проекта
GET    /api/v1/defects/            # Список дефектов
POST   /api/v1/defects/            # Создание дефекта
PUT    /api/v1/defects/{id}/       # Обновление дефекта
GET    /api/v1/reports/            # Генерация отчётов
POST   /api/v1/auth/login/         # Авторизация
POST   /api/v1/auth/refresh/       # Обновление токена
```

## 🤝 Участие в разработке

### Процесс разработки
1. **Fork** репозитория
2. Создайте **feature branch**
3. Внесите изменения
4. Добавьте **тесты**
5. Запустите **линтеры**
6. Создайте **Pull Request**

### Стандарты кода
- **PEP 8** для Python
- **ESLint + Prettier** для TypeScript
- **Conventional Commits** для сообщений коммитов
- **100% test coverage** для новых функций

### Code Review
- **Минимум 2 approvals**
- **Автоматические проверки** должны пройти
- **Documentation** должна быть обновлена

## 🐛 Известные проблемы

### Текущие ограничения
- Максимальный размер файла: 50MB
- Количество одновременных пользователей: 1000
- Поддержка только PostgreSQL

### Roadmap
- [ ] **GraphQL API**
- [ ] **Mobile приложение**
- [ ] **Offline support**
- [ ] **Multi-tenancy**
- [ ] **Advanced analytics**
- [ ] **Machine Learning** для предсказания дефектов

## 📞 Поддержка

### Контакты
- **Email**: support@defect-management.com
- **Documentation**: https://docs.defect-management.com
- **Issues**: GitHub Issues
- **Discussions**: GitHub Discussions

### Часто задаваемые вопросы
- **Как сбросить пароль?** Используйте функцию восстановления пароля
- **Как настроить email?** Проверьте настройки SMTP в .env
- **Как масштабировать?** Используйте Docker Swarm или Kubernetes

## 📄 Лицензия

Этот проект распространяется под лицензией MIT. См. файл [LICENSE](LICENSE) для подробной информации.

## 🙏 Благодарности

- **Django Community** за отличный фреймворк
- **React Team** за современную библиотеку
- **Contributors** за вклад в проект
- **Open Source Community** за инструменты и библиотеки

---

**Система управления дефектами** - современное решение для эффективного управления качеством в строительстве. Создано с ❤️ для строительной индустрии.