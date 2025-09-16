# Multi-stage build для Django + Node.js приложения
FROM node:18-alpine as frontend-builder

# Устанавливаем рабочую директорию для фронтенда
WORKDIR /app/frontend

# Копируем package.json и package-lock.json
COPY frontend/package*.json ./

# Устанавливаем зависимости
RUN npm ci --only=production

# Копируем исходный код фронтенда
COPY frontend/ .

# Собираем фронтенд приложение
RUN npm run build

# Основной образ для Django
FROM python:3.11-slim

# Устанавливаем системные зависимости
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    libpq-dev \
    libmagic1 \
    curl \
    netcat-traditional \
    && rm -rf /var/lib/apt/lists/*

# Создаем пользователя приложения
RUN groupadd -r appuser && useradd -r -g appuser appuser

# Устанавливаем рабочую директорию
WORKDIR /app

# Копируем requirements и устанавливаем Python зависимости
COPY backend/requirements/ ./requirements/
RUN pip install --no-cache-dir -r requirements/development.txt

# Копируем backend код
COPY backend/ ./backend/

# Копируем собранный фронтенд из предыдущего stage
COPY --from=frontend-builder /app/frontend/build ./frontend/build/

# Создаем необходимые директории
RUN mkdir -p /app/media /app/static /app/logs && \
    chown -R appuser:appuser /app

# Копируем entrypoint скрипт
COPY docker-entrypoint.sh /usr/local/bin/
RUN chmod +x /usr/local/bin/docker-entrypoint.sh && \
    chown appuser:appuser /usr/local/bin/docker-entrypoint.sh

# Переключаемся на пользователя приложения
USER appuser

# Устанавливаем переменные окружения
ENV PYTHONPATH=/app/backend
ENV DJANGO_SETTINGS_MODULE=config.settings.development

# Открываем порт
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD curl -f http://localhost:8000/health/ || exit 1

# Точка входа
ENTRYPOINT ["docker-entrypoint.sh"]

# Команда по умолчанию
CMD ["web"]