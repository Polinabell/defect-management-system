#!/bin/bash

# Скрипт для отката системы управления дефектами
# Использование: ./scripts/rollback.sh [staging|production] [backup_file]

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
BACKUP_FILE=${2:-}

if [[ "$ENVIRONMENT" != "staging" && "$ENVIRONMENT" != "production" ]]; then
    error "Неверное окружение. Используйте: staging или production"
    exit 1
fi

log "Начинаем откат в окружении: $ENVIRONMENT"

# Загрузка переменных окружения
if [[ -f ".env.$ENVIRONMENT" ]]; then
    export $(cat .env.$ENVIRONMENT | grep -v '^#' | xargs)
else
    error "Файл .env.$ENVIRONMENT не найден"
    exit 1
fi

# Функция для восстановления базы данных
restore_database() {
    local backup_file=$1
    
    if [[ -z "$backup_file" ]]; then
        # Ищем последний backup файл
        backup_file=$(ls -t backup_*.sql 2>/dev/null | head -n1)
        
        if [[ -z "$backup_file" ]]; then
            error "Резервная копия базы данных не найдена"
            return 1
        fi
        
        warning "Используем последнюю резервную копию: $backup_file"
    fi
    
    if [[ ! -f "$backup_file" ]]; then
        error "Файл резервной копии не найден: $backup_file"
        return 1
    fi
    
    log "Восстанавливаем базу данных из файла: $backup_file"
    
    # Останавливаем веб-сервисы
    docker-compose -f docker-compose.prod.yml stop web celery celery-beat
    
    # Восстанавливаем базу данных
    docker-compose -f docker-compose.prod.yml exec -T db psql -U $DB_USER -d $DB_NAME -c "DROP SCHEMA public CASCADE; CREATE SCHEMA public;"
    docker-compose -f docker-compose.prod.yml exec -T db psql -U $DB_USER -d $DB_NAME < "$backup_file"
    
    success "База данных восстановлена"
}

# Функция для восстановления медиа файлов
restore_media() {
    local media_backup=$1
    
    if [[ -z "$media_backup" ]]; then
        # Ищем последний backup медиа файлов
        media_backup=$(ls -t media_backup_*.tar.gz 2>/dev/null | head -n1)
        
        if [[ -z "$media_backup" ]]; then
            warning "Резервная копия медиа файлов не найдена"
            return 0
        fi
        
        warning "Используем последнюю резервную копию медиа: $media_backup"
    fi
    
    if [[ ! -f "$media_backup" ]]; then
        warning "Файл резервной копии медиа не найден: $media_backup"
        return 0
    fi
    
    log "Восстанавливаем медиа файлы из архива: $media_backup"
    
    # Останавливаем веб-сервисы
    docker-compose -f docker-compose.prod.yml stop web celery celery-beat
    
    # Восстанавливаем медиа файлы
    tar -xzf "$media_backup" -C backend/
    
    success "Медиа файлы восстановлены"
}

# Функция для отката к предыдущей версии образа
rollback_image() {
    log "Откатываем к предыдущей версии образа"
    
    # Получаем список образов
    local images=($(docker images --format "table {{.Repository}}:{{.Tag}}" | grep "defect-management" | grep -v "latest" | head -n 5))
    
    if [[ ${#images[@]} -lt 2 ]]; then
        error "Недостаточно версий для отката"
        return 1
    fi
    
    # Используем вторую по счету версию (предыдущую)
    local previous_image=${images[1]}
    
    log "Откатываем к образу: $previous_image"
    
    # Обновляем docker-compose файл с предыдущей версией
    sed -i "s|defect-management:.*|defect-management:$previous_image|g" docker-compose.prod.yml
    
    # Перезапускаем сервисы
    docker-compose -f docker-compose.prod.yml up -d --force-recreate
    
    success "Откат к предыдущей версии выполнен"
}

# Функция для проверки здоровья после отката
check_health_after_rollback() {
    log "Проверяем здоровье сервисов после отката"
    
    # Ждем запуска сервисов
    sleep 30
    
    # Проверяем доступность API
    local max_attempts=10
    local attempt=1
    
    while [ $attempt -le $max_attempts ]; do
        if curl -f http://localhost/api/v1/health/ > /dev/null 2>&1; then
            success "API доступен после отката"
            break
        fi
        
        log "Попытка $attempt/$max_attempts - ожидаем доступности API..."
        sleep 10
        ((attempt++))
    done
    
    if [ $attempt -gt $max_attempts ]; then
        error "API недоступен после отката"
        return 1
    fi
    
    # Проверяем доступность фронтенда
    if curl -f http://localhost/ > /dev/null 2>&1; then
        success "Фронтенд доступен после отката"
    else
        error "Фронтенд недоступен после отката"
        return 1
    fi
}

# Основной процесс отката
main() {
    log "=== НАЧАЛО ОТКАТА ==="
    
    # Подтверждение от пользователя
    if [[ "$ENVIRONMENT" == "production" ]]; then
        warning "ВНИМАНИЕ: Вы собираетесь выполнить откат в PRODUCTION окружении!"
        read -p "Вы уверены? (yes/no): " confirm
        
        if [[ "$confirm" != "yes" ]]; then
            log "Откат отменен пользователем"
            exit 0
        fi
    fi
    
    # 1. Восстановление базы данных
    if [[ -n "$BACKUP_FILE" ]]; then
        restore_database "$BACKUP_FILE"
    else
        restore_database
    fi
    
    # 2. Восстановление медиа файлов
    restore_media
    
    # 3. Откат к предыдущей версии образа
    rollback_image
    
    # 4. Проверка здоровья
    check_health_after_rollback
    
    success "=== ОТКАТ ЗАВЕРШЕН УСПЕШНО ==="
    
    # Выводим информацию о сервисах
    log "Статус сервисов после отката:"
    docker-compose -f docker-compose.prod.yml ps
    
    # Выводим логи
    log "Последние логи:"
    docker-compose -f docker-compose.prod.yml logs --tail=20
}

# Обработка сигналов
trap 'error "Откат прерван"; exit 1' INT TERM

# Запуск основного процесса
main "$@"
