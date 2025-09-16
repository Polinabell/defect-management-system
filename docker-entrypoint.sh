#!/bin/bash
set -e

# Ждем базу данных
echo "Ожидание подключения к базе данных..."
while ! nc -z db 5432; do
    sleep 1
done
echo "База данных доступна!"

# Переходим в директорию backend
cd /app/backend

# Выполняем миграции
echo "Выполнение миграций..."
python manage.py migrate --noinput

# Собираем статические файлы
echo "Сборка статических файлов..."
python manage.py collectstatic --noinput

# Определяем команду для запуска
case "$1" in
    web)
        echo "Запуск Django сервера..."
        exec python manage.py runserver 0.0.0.0:8000
        ;;
    celery-worker)
        echo "Запуск Celery worker..."
        exec celery -A config worker -l info
        ;;
    celery-beat)
        echo "Запуск Celery beat..."
        exec celery -A config beat -l info --scheduler django_celery_beat.schedulers:DatabaseScheduler
        ;;
    *)
        echo "Неизвестная команда: $1"
        echo "Доступные команды: web, celery-worker, celery-beat"
        exit 1
        ;;
esac