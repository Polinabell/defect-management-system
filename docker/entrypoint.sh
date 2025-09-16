#!/bin/bash
# Entrypoint скрипт для Docker контейнера

set -e

# Цвета для вывода
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Функция для логирования
log() {
    echo -e "${GREEN}[$(date +'%Y-%m-%d %H:%M:%S')] $1${NC}"
}

warn() {
    echo -e "${YELLOW}[$(date +'%Y-%m-%d %H:%M:%S')] WARNING: $1${NC}"
}

error() {
    echo -e "${RED}[$(date +'%Y-%m-%d %H:%M:%S')] ERROR: $1${NC}"
}

# Ожидание доступности базы данных
wait_for_db() {
    log "Ожидание доступности базы данных..."
    
    if [ "$DATABASE_URL" ]; then
        # Извлекаем параметры из DATABASE_URL
        DB_HOST=$(echo $DATABASE_URL | sed -n 's/.*@\([^:]*\):.*/\1/p')
        DB_PORT=$(echo $DATABASE_URL | sed -n 's/.*:\([0-9]*\)\/.*/\1/p')
        
        if [ -z "$DB_PORT" ]; then
            DB_PORT=5432
        fi
        
        log "Проверка подключения к $DB_HOST:$DB_PORT"
        
        /wait-for-it.sh "$DB_HOST:$DB_PORT" --timeout=60 --strict -- echo "База данных доступна!"
    else
        warn "DATABASE_URL не задан, пропускаем ожидание БД"
    fi
}

# Ожидание доступности Redis
wait_for_redis() {
    log "Ожидание доступности Redis..."
    
    if [ "$REDIS_URL" ]; then
        # Извлекаем хост и порт из REDIS_URL
        REDIS_HOST=$(echo $REDIS_URL | sed -n 's/.*@\([^:]*\):.*/\1/p')
        REDIS_PORT=$(echo $REDIS_URL | sed -n 's/.*:\([0-9]*\)\/.*/\1/p')
        
        if [ -z "$REDIS_HOST" ]; then
            REDIS_HOST=$(echo $REDIS_URL | sed -n 's/redis:\/\/[^@]*@*\([^:]*\):.*/\1/p')
        fi
        
        if [ -z "$REDIS_PORT" ]; then
            REDIS_PORT=6379
        fi
        
        log "Проверка подключения к Redis $REDIS_HOST:$REDIS_PORT"
        
        /wait-for-it.sh "$REDIS_HOST:$REDIS_PORT" --timeout=30 --strict -- echo "Redis доступен!"
    else
        warn "REDIS_URL не задан, пропускаем ожидание Redis"
    fi
}

# Выполнение миграций базы данных
run_migrations() {
    log "Выполнение миграций базы данных..."
    cd /app/backend
    
    # Проверяем соединение с БД
    python manage.py check --database default || {
        error "Не удалось подключиться к базе данных"
        exit 1
    }
    
    # Выполняем миграции
    python manage.py migrate --noinput || {
        error "Ошибка выполнения миграций"
        exit 1
    }
    
    log "Миграции выполнены успешно"
}

# Сборка статических файлов
collect_static() {
    log "Сборка статических файлов..."
    cd /app/backend
    
    python manage.py collectstatic --noinput --clear || {
        error "Ошибка сборки статических файлов"
        exit 1
    }
    
    log "Статические файлы собраны"
}

# Создание суперпользователя
create_superuser() {
    log "Проверка наличия суперпользователя..."
    cd /app/backend
    
    if [ "$DJANGO_SUPERUSER_EMAIL" ] && [ "$DJANGO_SUPERUSER_PASSWORD" ]; then
        python manage.py shell << EOF
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(is_superuser=True).exists():
    User.objects.create_superuser(
        email='$DJANGO_SUPERUSER_EMAIL',
        password='$DJANGO_SUPERUSER_PASSWORD',
        first_name='Admin',
        last_name='User'
    )
    print('Суперпользователь создан')
else:
    print('Суперпользователь уже существует')
EOF
    else
        warn "DJANGO_SUPERUSER_EMAIL или DJANGO_SUPERUSER_PASSWORD не заданы"
    fi
}

# Загрузка начальных данных
load_fixtures() {
    if [ "$LOAD_FIXTURES" = "true" ]; then
        log "Загрузка начальных данных..."
        cd /app/backend
        
        # Загружаем фикстуры если они есть
        if [ -f "fixtures/initial_data.json" ]; then
            python manage.py loaddata fixtures/initial_data.json || {
                warn "Не удалось загрузить начальные данные"
            }
        fi
        
        # Создаём категории дефектов по умолчанию
        python manage.py shell << EOF
from apps.defects.models import DefectCategory
categories = [
    {'name': 'Строительные работы', 'order': 1},
    {'name': 'Электромонтажные работы', 'order': 2},
    {'name': 'Сантехнические работы', 'order': 3},
    {'name': 'Отделочные работы', 'order': 4},
    {'name': 'Прочие', 'order': 5},
]
for cat_data in categories:
    DefectCategory.objects.get_or_create(name=cat_data['name'], defaults=cat_data)
print('Базовые категории созданы')
EOF
    fi
}

# Проверка здоровья системы
health_check() {
    log "Проверка здоровья системы..."
    cd /app/backend
    
    # Проверяем соединения
    python manage.py check --deploy || {
        error "Проверка системы не пройдена"
        exit 1
    }
    
    log "Система готова к работе"
}

# Запуск Gunicorn
start_gunicorn() {
    log "Запуск Gunicorn сервера..."
    cd /app/backend
    
    exec gunicorn config.wsgi:application \
        --bind 0.0.0.0:8000 \
        --workers ${GUNICORN_WORKERS:-3} \
        --worker-class ${GUNICORN_WORKER_CLASS:-sync} \
        --worker-connections ${GUNICORN_WORKER_CONNECTIONS:-1000} \
        --max-requests ${GUNICORN_MAX_REQUESTS:-1000} \
        --max-requests-jitter ${GUNICORN_MAX_REQUESTS_JITTER:-50} \
        --timeout ${GUNICORN_TIMEOUT:-120} \
        --keep-alive ${GUNICORN_KEEPALIVE:-2} \
        --preload \
        --access-logfile - \
        --error-logfile - \
        --log-level ${GUNICORN_LOG_LEVEL:-info}
}

# Запуск Celery Worker
start_celery_worker() {
    log "Запуск Celery Worker..."
    cd /app/backend
    
    exec celery -A config worker \
        --loglevel=${CELERY_LOG_LEVEL:-info} \
        --concurrency=${CELERY_WORKER_CONCURRENCY:-2} \
        --max-tasks-per-child=${CELERY_WORKER_MAX_TASKS_PER_CHILD:-1000} \
        --time-limit=${CELERY_TASK_TIME_LIMIT:-300} \
        --soft-time-limit=${CELERY_TASK_SOFT_TIME_LIMIT:-240}
}

# Запуск Celery Beat
start_celery_beat() {
    log "Запуск Celery Beat..."
    cd /app/backend
    
    # Удаляем старый PID файл если есть
    rm -f /tmp/celerybeat.pid
    
    exec celery -A config beat \
        --loglevel=${CELERY_LOG_LEVEL:-info} \
        --pidfile=/tmp/celerybeat.pid \
        --schedule=/tmp/celerybeat-schedule
}

# Запуск Celery Flower (мониторинг)
start_flower() {
    log "Запуск Celery Flower..."
    cd /app/backend
    
    exec celery -A config flower \
        --port=5555 \
        --basic_auth=${FLOWER_USER:-admin}:${FLOWER_PASSWORD:-admin}
}

# Главная функция
main() {
    log "Запуск контейнера defect-management-system"
    log "Команда: $1"
    
    case "$1" in
        gunicorn)
            wait_for_db
            wait_for_redis
            run_migrations
            collect_static
            create_superuser
            load_fixtures
            health_check
            start_gunicorn
            ;;
        celery-worker)
            wait_for_db
            wait_for_redis
            start_celery_worker
            ;;
        celery-beat)
            wait_for_db
            wait_for_redis
            start_celery_beat
            ;;
        flower)
            wait_for_redis
            start_flower
            ;;
        migrate)
            wait_for_db
            run_migrations
            ;;
        collectstatic)
            collect_static
            ;;
        shell)
            wait_for_db
            cd /app/backend
            exec python manage.py shell
            ;;
        manage)
            wait_for_db
            cd /app/backend
            shift
            exec python manage.py "$@"
            ;;
        bash)
            exec /bin/bash
            ;;
        *)
            error "Неизвестная команда: $1"
            echo "Доступные команды: gunicorn, celery-worker, celery-beat, flower, migrate, collectstatic, shell, manage, bash"
            exit 1
            ;;
    esac
}

# Обработка сигналов
trap 'echo "Получен сигнал завершения, останавливаем сервис..."; exit 0' SIGTERM SIGINT

# Запуск
main "$@"
