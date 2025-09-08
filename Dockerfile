# Multi-stage Dockerfile для системы управления дефектами

# Стадия сборки frontend
FROM node:18-alpine as frontend-builder

WORKDIR /app/frontend

# Копируем package.json и package-lock.json
COPY frontend/package*.json ./

# Устанавливаем зависимости
RUN npm ci --only=production

# Копируем исходный код frontend
COPY frontend/ ./

# Собираем production версию
RUN npm run build

# Стадия backend
FROM python:3.11-slim as backend

# Устанавливаем системные зависимости
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    postgresql-client \
    gettext \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Создаем пользователя для безопасности
RUN groupadd -r appuser && useradd -r -g appuser appuser

# Устанавливаем рабочую директорию
WORKDIR /app

# Копируем requirements
COPY backend/requirements/ requirements/

# Обновляем pip и устанавливаем Python зависимости
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements/production.txt

# Копируем backend код
COPY backend/ ./backend/

# Копируем собранный frontend
COPY --from=frontend-builder /app/frontend/build ./frontend/build/

# Создаем необходимые директории
RUN mkdir -p /app/media /app/static /app/logs && \
    chown -R appuser:appuser /app

# Копируем скрипты
COPY docker/entrypoint.sh /entrypoint.sh
COPY docker/wait-for-it.sh /wait-for-it.sh

RUN chmod +x /entrypoint.sh /wait-for-it.sh

# Переключаемся на пользователя appuser
USER appuser

# Собираем статические файлы
RUN cd backend && python manage.py collectstatic --noinput --settings=config.settings.production

# Открываем порт
EXPOSE 8000

# Устанавливаем точку входа
ENTRYPOINT ["/entrypoint.sh"]

# Команда по умолчанию
CMD ["gunicorn"]
