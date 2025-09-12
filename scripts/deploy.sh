#!/bin/bash

# Скрипт для деплоя системы управления дефектами
# Использование: ./scripts/deploy.sh [staging|production]

set -e

# Цвета для вывода
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Функция для логирования
log() {
    echo -e "${BLUE}[$(date +'%Y-%m-%d %H:%M:%S')]${NC} $1"
}

error() {
    echo -e "${RED}[ERROR]${NC} $1" >&2
}

success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

# Проверка аргументов
ENVIRONMENT=${1:-staging}

if [[ "$ENVIRONMENT" != "staging" && "$ENVIRONMENT" != "production" ]]; then
    error "Неверное окружение. Используйте: staging или production"
    exit 1
fi

log "Начинаем деплой в окружение: $ENVIRONMENT"

# Проверка наличия необходимых файлов
if [[ ! -f ".env.$ENVIRONMENT" ]]; then
    error "Файл .env.$ENVIRONMENT не найден"
    exit 1
fi

# Загрузка переменных окружения
export $(cat .env.$ENVIRONMENT | grep -v '^#' | xargs)

# Проверка наличия Docker
if ! command -v docker &> /dev/null; then
    error "Docker не установлен"
    exit 1
fi

if ! command -v docker-compose &> /dev/null; then
    error "Docker Compose не установлен"
    exit 1
fi

# Функция для проверки здоровья сервисов
check_health() {
    local service=$1
    local max_attempts=30
    local attempt=1
    
    log "Проверяем здоровье сервиса: $service"
    
    while [ $attempt -le $max_attempts ]; do
        if docker-compose -f docker-compose.prod.yml ps $service | grep -q "healthy"; then
            success "Сервис $service здоров"
            return 0
        fi
        
        log "Попытка $attempt/$max_attempts - ожидаем..."
        sleep 10
        ((attempt++))
    done
    
    error "Сервис $service не прошел проверку здоровья"
    return 1
}

# Функция для создания резервной копии
create_backup() {
    log "Создаем резервную копию перед деплоем"
    
    if [[ "$ENVIRONMENT" == "production" ]]; then
        # Создаем резервную копию базы данных
        docker-compose -f docker-compose.prod.yml exec -T db pg_dump -U $DB_USER $DB_NAME > "backup_$(date +%Y%m%d_%H%M%S).sql"
        
        # Создаем резервную копию медиа файлов
        tar -czf "media_backup_$(date +%Y%m%d_%H%M%S).tar.gz" -C backend media/
        
        success "Резервные копии созданы"
    fi
}

# Функция для миграций
run_migrations() {
    log "Выполняем миграции базы данных"
    
    docker-compose -f docker-compose.prod.yml exec web python manage.py migrate --noinput
    
    success "Миграции выполнены"
}

# Функция для сбора статических файлов
collect_static() {
    log "Собираем статические файлы"
    
    docker-compose -f docker-compose.prod.yml exec web python manage.py collectstatic --noinput
    
    success "Статические файлы собраны"
}

# Функция для создания суперпользователя
create_superuser() {
    log "Проверяем наличие суперпользователя"
    
    if ! docker-compose -f docker-compose.prod.yml exec -T web python manage.py shell -c "from django.contrib.auth import get_user_model; User = get_user_model(); print('SUPERUSER_EXISTS' if User.objects.filter(is_superuser=True).exists() else 'NO_SUPERUSER')" | grep -q "SUPERUSER_EXISTS"; then
        warning "Суперпользователь не найден. Создайте его вручную после деплоя"
    else
        success "Суперпользователь существует"
    fi
}

# Функция для очистки старых образов
cleanup_images() {
    log "Очищаем старые Docker образы"
    
    # Удаляем неиспользуемые образы
    docker image prune -f
    
    # Удаляем старые образы приложения
    docker images | grep "defect-management" | grep -v "latest" | awk '{print $3}' | xargs -r docker rmi -f
    
    success "Очистка образов завершена"
}

# Основной процесс деплоя
main() {
    log "=== НАЧАЛО ДЕПЛОЯ ==="
    
    # 1. Создание резервной копии
    create_backup
    
    # 2. Остановка старых контейнеров
    log "Останавливаем старые контейнеры"
    docker-compose -f docker-compose.prod.yml down
    
    # 3. Сборка новых образов
    log "Собираем новые образы"
    docker-compose -f docker-compose.prod.yml build --no-cache
    
    # 4. Запуск сервисов
    log "Запускаем сервисы"
    docker-compose -f docker-compose.prod.yml up -d
    
    # 5. Ожидание готовности базы данных
    check_health "db"
    
    # 6. Ожидание готовности Redis
    check_health "redis"
    
    # 7. Выполнение миграций
    run_migrations
    
    # 8. Сбор статических файлов
    collect_static
    
    # 9. Ожидание готовности веб-сервиса
    check_health "web"
    
    # 10. Проверка суперпользователя
    create_superuser
    
    # 11. Очистка старых образов
    cleanup_images
    
    # 12. Финальная проверка
    log "Выполняем финальную проверку"
    
    # Проверяем доступность API
    if curl -f http://localhost/api/v1/health/ > /dev/null 2>&1; then
        success "API доступен"
    else
        error "API недоступен"
        exit 1
    fi
    
    # Проверяем доступность фронтенда
    if curl -f http://localhost/ > /dev/null 2>&1; then
        success "Фронтенд доступен"
    else
        error "Фронтенд недоступен"
        exit 1
    fi
    
    success "=== ДЕПЛОЙ ЗАВЕРШЕН УСПЕШНО ==="
    
    # Выводим информацию о сервисах
    log "Статус сервисов:"
    docker-compose -f docker-compose.prod.yml ps
    
    # Выводим логи
    log "Последние логи:"
    docker-compose -f docker-compose.prod.yml logs --tail=20
}

# Обработка сигналов
trap 'error "Деплой прерван"; exit 1' INT TERM

# Запуск основного процесса
main "$@"
