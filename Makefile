# Makefile для системы управления дефектами

.PHONY: help install dev prod test clean backup migrate collectstatic

# Переменные
PYTHON = python
MANAGE = $(PYTHON) manage.py
CELERY = celery -A config

# Цвета для вывода
RED = \033[0;31m
GREEN = \033[0;32m
YELLOW = \033[1;33m
BLUE = \033[0;34m
NC = \033[0m # No Color

help: ## Показать справку
	@echo "$(BLUE)Система управления дефектами$(NC)"
	@echo "$(BLUE)==============================$(NC)"
	@echo ""
	@echo "$(GREEN)Доступные команды:$(NC)"
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "  $(YELLOW)%-20s$(NC) %s\n", $$1, $$2}' $(MAKEFILE_LIST)

install: ## Установить зависимости
	@echo "$(BLUE)Установка зависимостей...$(NC)"
	pip install -r requirements/development.txt
	@echo "$(GREEN)Зависимости установлены$(NC)"

dev: ## Запустить в режиме разработки
	@echo "$(BLUE)Запуск в режиме разработки...$(NC)"
	$(MANAGE) runserver 0.0.0.0:8000

prod: ## Запустить в режиме продакшена
	@echo "$(BLUE)Запуск в режиме продакшена...$(NC)"
	$(MANAGE) collectstatic --noinput
	$(MANAGE) migrate
	gunicorn config.wsgi:application --bind 0.0.0.0:8000 --workers 4

test: ## Запустить тесты
	@echo "$(BLUE)Запуск тестов...$(NC)"
	$(MANAGE) test
	@echo "$(GREEN)Тесты завершены$(NC)"

migrate: ## Применить миграции
	@echo "$(BLUE)Применение миграций...$(NC)"
	$(MANAGE) makemigrations
	$(MANAGE) migrate
	@echo "$(GREEN)Миграции применены$(NC)"

collectstatic: ## Собрать статические файлы
	@echo "$(BLUE)Сбор статических файлов...$(NC)"
	$(MANAGE) collectstatic --noinput
	@echo "$(GREEN)Статические файлы собраны$(NC)"

backup: ## Создать резервную копию базы данных
	@echo "$(BLUE)Создание резервной копии...$(NC)"
	$(MANAGE) backup_database --compress
	@echo "$(GREEN)Резервная копия создана$(NC)"

celery-worker: ## Запустить Celery worker
	@echo "$(BLUE)Запуск Celery worker...$(NC)"
	$(CELERY) worker --loglevel=info --concurrency=4

celery-beat: ## Запустить Celery beat
	@echo "$(BLUE)Запуск Celery beat...$(NC)"
	$(CELERY) beat --loglevel=info --scheduler=django_celery_beat.schedulers:DatabaseScheduler

celery-flower: ## Запустить Celery Flower
	@echo "$(BLUE)Запуск Celery Flower...$(NC)"
	$(CELERY) flower --port=5555

celery-all: ## Запустить все сервисы Celery
	@echo "$(BLUE)Запуск всех сервисов Celery...$(NC)"
	@echo "$(YELLOW)Для полного запуска выполните в разных терминалах:$(NC)"
	@echo "  make celery-worker"
	@echo "  make celery-beat"
	@echo "  make celery-flower"

docker-dev: ## Запустить в Docker (разработка)
	@echo "$(BLUE)Запуск в Docker (разработка)...$(NC)"
	docker-compose -f docker-compose.yml up --build

docker-prod: ## Запустить в Docker (продакшен)
	@echo "$(BLUE)Запуск в Docker (продакшен)...$(NC)"
	docker-compose -f docker-compose.prod.yml up --build -d

docker-celery: ## Запустить Celery в Docker
	@echo "$(BLUE)Запуск Celery в Docker...$(NC)"
	docker-compose -f docker-compose.celery.yml up --build -d

clean: ## Очистить временные файлы
	@echo "$(BLUE)Очистка временных файлов...$(NC)"
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	rm -rf .pytest_cache/
	rm -rf htmlcov/
	@echo "$(GREEN)Очистка завершена$(NC)"

logs: ## Показать логи Django
	@echo "$(BLUE)Логи Django:$(NC)"
	tail -f logs/django.log

logs-celery: ## Показать логи Celery
	@echo "$(BLUE)Логи Celery:$(NC)"
	$(CELERY) events

shell: ## Открыть Django shell
	@echo "$(BLUE)Открытие Django shell...$(NC)"
	$(MANAGE) shell

superuser: ## Создать суперпользователя
	@echo "$(BLUE)Создание суперпользователя...$(NC)"
	$(MANAGE) createsuperuser

check: ## Проверить конфигурацию Django
	@echo "$(BLUE)Проверка конфигурации...$(NC)"
	$(MANAGE) check
	@echo "$(GREEN)Конфигурация корректна$(NC)"

lint: ## Проверить код линтерами
	@echo "$(BLUE)Проверка кода...$(NC)"
	flake8 .
	black --check .
	@echo "$(GREEN)Проверка завершена$(NC)"

format: ## Форматировать код
	@echo "$(BLUE)Форматирование кода...$(NC)"
	black .
	isort .
	@echo "$(GREEN)Код отформатирован$(NC)"

security: ## Проверить безопасность
	@echo "$(BLUE)Проверка безопасности...$(NC)"
	bandit -r .
	safety check
	@echo "$(GREEN)Проверка безопасности завершена$(NC)"

coverage: ## Запустить тесты с покрытием
	@echo "$(BLUE)Запуск тестов с покрытием...$(NC)"
	coverage run --source='.' manage.py test
	coverage report
	coverage html
	@echo "$(GREEN)Отчет о покрытии создан в htmlcov/$(NC)"

load-test: ## Запустить нагрузочное тестирование
	@echo "$(BLUE)Запуск нагрузочного тестирования...$(NC)"
	$(MANAGE) test tests.test_load
	@echo "$(GREEN)Нагрузочное тестирование завершено$(NC)"

monitor: ## Мониторинг системы
	@echo "$(BLUE)Мониторинг системы:$(NC)"
	@echo "$(YELLOW)Django:$(NC) http://localhost:8000"
	@echo "$(YELLOW)Flower:$(NC) http://localhost:5555"
	@echo "$(YELLOW)Admin:$(NC) http://localhost:8000/admin"
	@echo "$(YELLOW)API:$(NC) http://localhost:8000/api/v1/"

# Команды для разработки
dev-setup: install migrate superuser ## Полная настройка для разработки
	@echo "$(GREEN)Настройка для разработки завершена$(NC)"
	@echo "$(YELLOW)Запустите: make dev$(NC)"

# Команды для продакшена
prod-setup: install migrate collectstatic ## Полная настройка для продакшена
	@echo "$(GREEN)Настройка для продакшена завершена$(NC)"
	@echo "$(YELLOW)Запустите: make prod$(NC)"