# Техническая документация системы управления дефектами

## Содержание

1. [Архитектура системы](#архитектура-системы)
2. [Технологический стек](#технологический-стек)
3. [Установка и настройка](#установка-и-настройка)
4. [Конфигурация](#конфигурация)
5. [Развертывание](#развертывание)
6. [Мониторинг и логирование](#мониторинг-и-логирование)
7. [Безопасность](#безопасность)
8. [Резервное копирование](#резервное-копирование)
9. [Устранение неполадок](#устранение-неполадок)

## Архитектура системы

### Общая архитектура

Система построена по принципу микросервисной архитектуры с разделением на frontend и backend компоненты:

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Frontend      │    │   Backend       │    │   Database      │
│   (React)       │◄──►│   (Django)      │◄──►│   (PostgreSQL)  │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Nginx         │    │   Redis         │    │   Celery        │
│   (Proxy)       │    │   (Cache)       │    │   (Tasks)       │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

### Компоненты системы

#### Frontend
- **React 18** - основной фреймворк
- **TypeScript** - типизация
- **Material-UI** - компоненты интерфейса
- **Redux Toolkit** - управление состоянием
- **React Query** - работа с API
- **React Router** - маршрутизация

#### Backend
- **Django 5.2** - веб-фреймворк
- **Django REST Framework** - API
- **PostgreSQL** - основная база данных
- **Redis** - кэширование и очереди
- **Celery** - фоновые задачи
- **Gunicorn** - WSGI сервер

#### Инфраструктура
- **Docker** - контейнеризация
- **Nginx** - веб-сервер и балансировщик
- **Prometheus** - мониторинг
- **Grafana** - визуализация метрик

## Технологический стек

### Backend

```python
# requirements/production.txt
Django==5.2.6
djangorestframework==3.14.0
django-cors-headers==4.3.1
django-filter==23.5
psycopg2-binary==2.9.9
redis==5.0.1
celery==5.3.4
django-celery-beat==2.5.0
gunicorn==21.2.0
whitenoise==6.6.0
django-environ==0.11.2
phonenumber-field==7.1.0
Pillow==10.1.0
```

### Frontend

```json
{
  "dependencies": {
    "react": "^18.2.0",
    "react-dom": "^18.2.0",
    "typescript": "^5.2.2",
    "@mui/material": "^5.14.18",
    "@mui/icons-material": "^5.14.18",
    "@reduxjs/toolkit": "^1.9.7",
    "react-redux": "^8.1.3",
    "@tanstack/react-query": "^5.8.4",
    "react-router-dom": "^6.18.0",
    "react-dropzone": "^14.2.3",
    "recharts": "^2.8.0"
  }
}
```

### Инфраструктура

```yaml
# docker-compose.prod.yml
services:
  web:
    image: python:3.11-slim
  frontend:
    image: node:18-alpine
  db:
    image: postgres:15-alpine
  redis:
    image: redis:7-alpine
  nginx:
    image: nginx:alpine
  prometheus:
    image: prom/prometheus:latest
  grafana:
    image: grafana/grafana:latest
```

## Установка и настройка

### Системные требования

#### Минимальные требования
- **CPU**: 2 ядра
- **RAM**: 4 GB
- **Диск**: 20 GB свободного места
- **ОС**: Ubuntu 20.04+ / CentOS 8+ / Windows 10+

#### Рекомендуемые требования
- **CPU**: 4 ядра
- **RAM**: 8 GB
- **Диск**: 50 GB SSD
- **ОС**: Ubuntu 22.04 LTS

### Установка зависимостей

#### Ubuntu/Debian
```bash
# Обновление системы
sudo apt update && sudo apt upgrade -y

# Установка Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER

# Установка Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/download/v2.21.0/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Установка Node.js
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt-get install -y nodejs

# Установка Python
sudo apt-get install -y python3.11 python3.11-venv python3.11-dev
```

#### CentOS/RHEL
```bash
# Установка Docker
sudo yum install -y yum-utils
sudo yum-config-manager --add-repo https://download.docker.com/linux/centos/docker-ce.repo
sudo yum install -y docker-ce docker-ce-cli containerd.io
sudo systemctl start docker
sudo systemctl enable docker

# Установка Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/download/v2.21.0/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose
```

### Клонирование репозитория

```bash
git clone https://github.com/Polinabell/defect-management-system.git
cd defect-management-system
```

### Настройка окружения

```bash
# Копирование файлов конфигурации
cp env.production.example .env.production
cp backend/env.example backend/.env

# Редактирование переменных окружения
nano .env.production
nano backend/.env
```

## Конфигурация

### Переменные окружения

#### Основные настройки
```bash
# Django
SECRET_KEY=your-super-secret-key-here
DEBUG=False
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com

# База данных
DB_NAME=defect_management_prod
DB_USER=postgres
DB_PASSWORD=your-db-password
DB_HOST=db
DB_PORT=5432

# Redis
REDIS_PASSWORD=your-redis-password
REDIS_URL=redis://:your-redis-password@redis:6379/0

# Email
EMAIL_HOST=smtp.gmail.com
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
EMAIL_PORT=587
EMAIL_USE_TLS=True
```

#### Настройки безопасности
```bash
# SSL/TLS
SECURE_SSL_REDIRECT=True
SECURE_HSTS_SECONDS=31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS=True
SECURE_HSTS_PRELOAD=True

# CSRF
CSRF_TRUSTED_ORIGINS=https://yourdomain.com,https://www.yourdomain.com
CSRF_COOKIE_SECURE=True
CSRF_COOKIE_HTTPONLY=True

# Сессии
SESSION_COOKIE_SECURE=True
SESSION_COOKIE_HTTPONLY=True
SESSION_COOKIE_SAMESITE=Strict
```

### Настройка базы данных

#### PostgreSQL
```sql
-- Создание базы данных
CREATE DATABASE defect_management_prod;
CREATE USER defect_user WITH PASSWORD 'secure_password';
GRANT ALL PRIVILEGES ON DATABASE defect_management_prod TO defect_user;

-- Настройка производительности
ALTER SYSTEM SET shared_buffers = '256MB';
ALTER SYSTEM SET effective_cache_size = '1GB';
ALTER SYSTEM SET maintenance_work_mem = '64MB';
ALTER SYSTEM SET checkpoint_completion_target = 0.9;
ALTER SYSTEM SET wal_buffers = '16MB';
ALTER SYSTEM SET default_statistics_target = 100;
```

#### Redis
```conf
# redis.conf
maxmemory 256mb
maxmemory-policy allkeys-lru
save 900 1
save 300 10
save 60 10000
```

### Настройка Nginx

```nginx
# nginx.conf
server {
    listen 80;
    server_name yourdomain.com;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name yourdomain.com;
    
    ssl_certificate /etc/nginx/ssl/cert.pem;
    ssl_certificate_key /etc/nginx/ssl/key.pem;
    
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-RSA-AES256-GCM-SHA512:DHE-RSA-AES256-GCM-SHA512;
    ssl_prefer_server_ciphers off;
    
    location / {
        proxy_pass http://frontend:3000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
    
    location /api/ {
        proxy_pass http://backend:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

## Развертывание

### Docker Compose

```bash
# Сборка и запуск
docker-compose -f docker-compose.prod.yml build
docker-compose -f docker-compose.prod.yml up -d

# Проверка статуса
docker-compose -f docker-compose.prod.yml ps

# Просмотр логов
docker-compose -f docker-compose.prod.yml logs -f
```

### Автоматический деплой

```bash
# Использование скрипта деплоя
chmod +x scripts/deploy.sh
./scripts/deploy.sh production
```

### Kubernetes (опционально)

```yaml
# k8s-deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: defect-management-backend
spec:
  replicas: 3
  selector:
    matchLabels:
      app: defect-management-backend
  template:
    metadata:
      labels:
        app: defect-management-backend
    spec:
      containers:
      - name: backend
        image: your-registry/defect-management-backend:latest
        ports:
        - containerPort: 8000
        env:
        - name: DATABASE_URL
          valueFrom:
            secretKeyRef:
              name: db-secret
              key: url
```

## Мониторинг и логирование

### Prometheus метрики

```python
# metrics.py
from prometheus_client import Counter, Histogram, Gauge

# Счетчики
DEFECTS_CREATED = Counter('defects_created_total', 'Total defects created')
API_REQUESTS = Counter('api_requests_total', 'Total API requests', ['method', 'endpoint', 'status'])

# Гистограммы
REQUEST_DURATION = Histogram('request_duration_seconds', 'Request duration', ['method', 'endpoint'])

# Датчики
ACTIVE_USERS = Gauge('active_users', 'Number of active users')
```

### Grafana дашборды

```json
{
  "dashboard": {
    "title": "Defect Management System",
    "panels": [
      {
        "title": "API Requests",
        "type": "graph",
        "targets": [
          {
            "expr": "rate(api_requests_total[5m])",
            "legendFormat": "{{method}} {{endpoint}}"
          }
        ]
      }
    ]
  }
}
```

### Логирование

```python
# settings.py
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'file': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': 'logs/django.log',
            'formatter': 'verbose',
        },
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
    },
    'root': {
        'handlers': ['console', 'file'],
    },
}
```

## Безопасность

### Настройки безопасности Django

```python
# settings/production.py
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
SECURE_SSL_REDIRECT = True
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

# CSRF
CSRF_COOKIE_SECURE = True
CSRF_COOKIE_HTTPONLY = True
CSRF_COOKIE_SAMESITE = 'Strict'

# Сессии
SESSION_COOKIE_SECURE = True
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = 'Strict'
```

### Middleware безопасности

```python
# security_middleware.py
class SecurityHeadersMiddleware:
    def process_response(self, request, response):
        response['X-Content-Type-Options'] = 'nosniff'
        response['X-Frame-Options'] = 'DENY'
        response['X-XSS-Protection'] = '1; mode=block'
        response['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
        return response
```

### Валидация данных

```python
# validators.py
def validate_password_strength(value):
    if len(value) < 8:
        raise ValidationError('Пароль должен содержать минимум 8 символов')
    if not re.search(r'[A-Z]', value):
        raise ValidationError('Пароль должен содержать заглавную букву')
    if not re.search(r'\d', value):
        raise ValidationError('Пароль должен содержать цифру')
```

## Резервное копирование

### Автоматическое резервное копирование

```python
# tasks.py
@periodic_task(run_every=crontab(hour=2, minute=0))
def backup_database():
    """Ежедневное резервное копирование базы данных"""
    timestamp = timezone.now().strftime('%Y%m%d_%H%M%S')
    backup_file = f'backup_{timestamp}.sql'
    
    # Создание резервной копии
    subprocess.run([
        'pg_dump',
        '-h', settings.DATABASES['default']['HOST'],
        '-U', settings.DATABASES['default']['USER'],
        '-d', settings.DATABASES['default']['NAME'],
        '-f', backup_file
    ])
    
    # Сжатие
    if settings.BACKUP_COMPRESS:
        subprocess.run(['gzip', backup_file])
        backup_file += '.gz'
    
    # Загрузка в S3
    upload_to_s3(backup_file)
```

### Восстановление из резервной копии

```bash
# Восстановление базы данных
gunzip backup_20241215_020000.sql.gz
psql -h localhost -U postgres -d defect_management_prod < backup_20241215_020000.sql

# Восстановление медиа файлов
tar -xzf media_backup_20241215_020000.tar.gz -C backend/
```

## Устранение неполадок

### Частые проблемы

#### 1. Ошибка подключения к базе данных
```bash
# Проверка статуса PostgreSQL
docker-compose -f docker-compose.prod.yml ps db

# Проверка логов
docker-compose -f docker-compose.prod.yml logs db

# Проверка подключения
docker-compose -f docker-compose.prod.yml exec web python manage.py dbshell
```

#### 2. Проблемы с Redis
```bash
# Проверка статуса Redis
docker-compose -f docker-compose.prod.yml exec redis redis-cli ping

# Очистка кэша
docker-compose -f docker-compose.prod.yml exec redis redis-cli FLUSHALL
```

#### 3. Ошибки Celery
```bash
# Проверка статуса Celery
docker-compose -f docker-compose.prod.yml exec celery celery -A config inspect active

# Перезапуск Celery
docker-compose -f docker-compose.prod.yml restart celery
```

#### 4. Проблемы с Nginx
```bash
# Проверка конфигурации
docker-compose -f docker-compose.prod.yml exec nginx nginx -t

# Перезагрузка конфигурации
docker-compose -f docker-compose.prod.yml exec nginx nginx -s reload
```

### Мониторинг производительности

```bash
# Использование ресурсов
docker stats

# Логи приложения
docker-compose -f docker-compose.prod.yml logs -f web

# Метрики Prometheus
curl http://localhost:9090/api/v1/query?query=up
```

### Отладка

```python
# Включение отладки в production (временно)
DEBUG = True
LOGGING['loggers']['django']['level'] = 'DEBUG'

# Добавление отладочной информации
import logging
logger = logging.getLogger(__name__)
logger.debug(f'Request data: {request.data}')
```

---

**Версия документации**: 1.0  
**Дата обновления**: Декабрь 2024  
**Автор**: Команда разработки системы управления дефектами
