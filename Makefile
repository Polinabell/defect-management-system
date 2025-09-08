# Makefile для системы управления дефектами

.PHONY: help build up down logs clean test lint format install migrate collectstatic backup restore deploy

# Переменные
COMPOSE_FILE=docker-compose.yml
COMPOSE_FILE_PROD=docker-compose.prod.yml
COMPOSE_FILE_TEST=docker-compose.test.yml

# Цвета для вывода
GREEN=\033[0;32m
YELLOW=\033[0;33m
RED=\033[0;31m
NC=\033[0m # No Color

# По умолчанию показываем help
help: ## Показать справку
	@echo "${GREEN}Система управления дефектами - Makefile команды:${NC}"
	@echo
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

# === ОСНОВНЫЕ КОМАНДЫ ===

build: ## Собрать Docker образы
	@echo "${GREEN}Сборка Docker образов...${NC}"
	docker-compose -f $(COMPOSE_FILE) build

build-prod: ## Собрать production образы
	@echo "${GREEN}Сборка production образов...${NC}"
	docker-compose -f $(COMPOSE_FILE_PROD) build

up: ## Запустить все сервисы в разработке
	@echo "${GREEN}Запуск сервисов в режиме разработки...${NC}"
	docker-compose -f $(COMPOSE_FILE) up -d
	@echo "${GREEN}Сервисы запущены! Приложение доступно на http://localhost${NC}"

up-prod: ## Запустить в production режиме
	@echo "${GREEN}Запуск production окружения...${NC}"
	docker-compose -f $(COMPOSE_FILE_PROD) up -d
	@echo "${GREEN}Production окружение запущено!${NC}"

down: ## Остановить все сервисы
	@echo "${YELLOW}Остановка сервисов...${NC}"
	docker-compose -f $(COMPOSE_FILE) down

down-prod: ## Остановить production сервисы
	@echo "${YELLOW}Остановка production сервисов...${NC}"
	docker-compose -f $(COMPOSE_FILE_PROD) down

restart: down up ## Перезапустить сервисы

logs: ## Показать логи всех сервисов
	docker-compose -f $(COMPOSE_FILE) logs -f

logs-web: ## Показать логи web сервиса
	docker-compose -f $(COMPOSE_FILE) logs -f web

logs-celery: ## Показать логи Celery
	docker-compose -f $(COMPOSE_FILE) logs -f celery

logs-db: ## Показать логи базы данных
	docker-compose -f $(COMPOSE_FILE) logs -f db

status: ## Показать статус сервисов
	@echo "${GREEN}Статус сервисов:${NC}"
	docker-compose -f $(COMPOSE_FILE) ps

# === РАЗРАБОТКА ===

shell: ## Войти в shell Django контейнера
	docker-compose -f $(COMPOSE_FILE) exec web bash

shell-db: ## Войти в shell базы данных
	docker-compose -f $(COMPOSE_FILE) exec db psql -U postgres -d defect_management

django-shell: ## Запустить Django shell
	docker-compose -f $(COMPOSE_FILE) exec web python manage.py shell

manage: ## Выполнить Django команду (use: make manage cmd="migrate")
	docker-compose -f $(COMPOSE_FILE) exec web python manage.py $(cmd)

migrate: ## Выполнить миграции БД
	@echo "${GREEN}Выполнение миграций...${NC}"
	docker-compose -f $(COMPOSE_FILE) exec web python manage.py migrate

makemigrations: ## Создать миграции
	@echo "${GREEN}Создание миграций...${NC}"
	docker-compose -f $(COMPOSE_FILE) exec web python manage.py makemigrations

collectstatic: ## Собрать статические файлы
	@echo "${GREEN}Сборка статических файлов...${NC}"
	docker-compose -f $(COMPOSE_FILE) exec web python manage.py collectstatic --noinput

createsuperuser: ## Создать суперпользователя
	docker-compose -f $(COMPOSE_FILE) exec web python manage.py createsuperuser

loaddata: ## Загрузить начальные данные
	@echo "${GREEN}Загрузка начальных данных...${NC}"
	docker-compose -f $(COMPOSE_FILE) exec web python manage.py loaddata fixtures/initial_data.json

# === ТЕСТИРОВАНИЕ ===

test: ## Запустить все тесты
	@echo "${GREEN}Запуск тестов...${NC}"
	docker-compose -f $(COMPOSE_FILE_TEST) up --build --abort-on-container-exit
	docker-compose -f $(COMPOSE_FILE_TEST) down -v

test-backend: ## Запустить backend тесты
	@echo "${GREEN}Запуск backend тестов...${NC}"
	docker-compose -f $(COMPOSE_FILE) exec web pytest -v --cov=. --cov-report=html

test-frontend: ## Запустить frontend тесты
	@echo "${GREEN}Запуск frontend тестов...${NC}"
	cd frontend && npm test -- --coverage --watchAll=false

test-coverage: ## Показать покрытие тестами
	@echo "${GREEN}Генерация отчёта покрытия...${NC}"
	docker-compose -f $(COMPOSE_FILE) exec web pytest --cov=. --cov-report=html --cov-report=term
	@echo "${GREEN}HTML отчёт доступен в backend/htmlcov/index.html${NC}"

test-load: ## Запустить нагрузочные тесты
	@echo "${GREEN}Запуск нагрузочных тестов...${NC}"
	docker-compose -f $(COMPOSE_FILE) exec web pytest tests/test_load.py -v -m slow

# === КАЧЕСТВО КОДА ===

lint: lint-backend lint-frontend ## Проверить качество кода

lint-backend: ## Линтинг Python кода
	@echo "${GREEN}Линтинг Python кода...${NC}"
	docker-compose -f $(COMPOSE_FILE) exec web flake8 .
	docker-compose -f $(COMPOSE_FILE) exec web mypy --config-file=mypy.ini .

lint-frontend: ## Линтинг frontend кода
	@echo "${GREEN}Линтинг frontend кода...${NC}"
	cd frontend && npm run lint

format: format-backend format-frontend ## Форматировать код

format-backend: ## Форматировать Python код
	@echo "${GREEN}Форматирование Python кода...${NC}"
	docker-compose -f $(COMPOSE_FILE) exec web black .
	docker-compose -f $(COMPOSE_FILE) exec web isort .

format-frontend: ## Форматировать frontend код
	@echo "${GREEN}Форматирование frontend кода...${NC}"
	cd frontend && npm run format

security-check: ## Проверка безопасности
	@echo "${GREEN}Проверка безопасности...${NC}"
	docker-compose -f $(COMPOSE_FILE) exec web bandit -r . -f json -o bandit-report.json
	docker-compose -f $(COMPOSE_FILE) exec web safety check
	cd frontend && npm audit

# === УСТАНОВКА ЗАВИСИМОСТЕЙ ===

install: install-backend install-frontend ## Установить все зависимости

install-backend: ## Установить backend зависимости
	@echo "${GREEN}Установка Python зависимостей...${NC}"
	cd backend && pip install -r requirements/development.txt

install-frontend: ## Установить frontend зависимости
	@echo "${GREEN}Установка Node.js зависимостей...${NC}"
	cd frontend && npm install

update-deps: ## Обновить зависимости
	@echo "${GREEN}Обновление зависимостей...${NC}"
	cd backend && pip list --outdated
	cd frontend && npm outdated

# === БАЗА ДАННЫХ ===

db-reset: ## Сбросить базу данных (ВНИМАНИЕ: удалит все данные!)
	@echo "${RED}ВНИМАНИЕ: Это удалит ВСЕ данные в базе!${NC}"
	@read -p "Вы уверены? (y/N): " confirm && [ "$$confirm" = "y" ]
	docker-compose -f $(COMPOSE_FILE) stop web celery celery-beat
	docker-compose -f $(COMPOSE_FILE) exec db dropdb -U postgres defect_management
	docker-compose -f $(COMPOSE_FILE) exec db createdb -U postgres defect_management
	$(MAKE) migrate
	$(MAKE) createsuperuser
	$(MAKE) loaddata
	docker-compose -f $(COMPOSE_FILE) start web celery celery-beat

backup: ## Создать резервную копию БД
	@echo "${GREEN}Создание резервной копии БД...${NC}"
	mkdir -p backups
	docker-compose -f $(COMPOSE_FILE) exec db pg_dump -U postgres defect_management > backups/backup_$(shell date +%Y%m%d_%H%M%S).sql
	@echo "${GREEN}Резервная копия создана в папке backups/${NC}"

restore: ## Восстановить БД из резервной копии (use: make restore file=backup_file.sql)
	@echo "${GREEN}Восстановление БД из резервной копии...${NC}"
	docker-compose -f $(COMPOSE_FILE) exec -T db psql -U postgres defect_management < backups/$(file)

# === МОНИТОРИНГ ===

monitor: ## Открыть мониторинг
	@echo "${GREEN}Мониторинг доступен по адресам:${NC}"
	@echo "Grafana: http://localhost:3000 (admin/admin)"
	@echo "Prometheus: http://localhost:9090"

monitor-logs: ## Просмотр логов мониторинга
	docker-compose -f $(COMPOSE_FILE) logs -f prometheus grafana

health: ## Проверить здоровье сервисов
	@echo "${GREEN}Проверка здоровья сервисов...${NC}"
	@curl -f http://localhost/health/ && echo "${GREEN}✓ Web service OK${NC}" || echo "${RED}✗ Web service FAIL${NC}"
	@curl -f http://localhost:9090/-/healthy && echo "${GREEN}✓ Prometheus OK${NC}" || echo "${RED}✗ Prometheus FAIL${NC}"
	@curl -f http://localhost:3000/api/health && echo "${GREEN}✓ Grafana OK${NC}" || echo "${RED}✗ Grafana FAIL${NC}"

# === ДЕПЛОЙ ===

deploy-staging: ## Деплой в staging
	@echo "${GREEN}Деплой в staging...${NC}"
	git checkout develop
	git pull origin develop
	docker-compose -f docker-compose.staging.yml pull
	docker-compose -f docker-compose.staging.yml up -d
	$(MAKE) health

deploy-prod: ## Деплой в production
	@echo "${GREEN}Деплой в production...${NC}"
	git checkout main
	git pull origin main
	$(MAKE) backup
	docker-compose -f $(COMPOSE_FILE_PROD) pull
	docker-compose -f $(COMPOSE_FILE_PROD) up -d --scale web=2
	sleep 30
	$(MAKE) health
	@echo "${GREEN}Production деплой завершён!${NC}"

rollback: ## Откатить деплой (use: make rollback version=v1.0.0)
	@echo "${YELLOW}Откат к версии $(version)...${NC}"
	docker-compose -f $(COMPOSE_FILE_PROD) pull $(version)
	docker-compose -f $(COMPOSE_FILE_PROD) up -d
	$(MAKE) health

# === ОЧИСТКА ===

clean: ## Очистить неиспользуемые Docker ресурсы
	@echo "${YELLOW}Очистка Docker ресурсов...${NC}"
	docker system prune -f
	docker volume prune -f

clean-all: ## ПОЛНАЯ очистка (удалит все контейнеры и образы)
	@echo "${RED}ВНИМАНИЕ: Это удалит ВСЕ Docker контейнеры и образы!${NC}"
	@read -p "Вы уверены? (y/N): " confirm && [ "$$confirm" = "y" ]
	docker-compose -f $(COMPOSE_FILE) down -v --remove-orphans
	docker system prune -a -f
	docker volume prune -f

clean-logs: ## Очистить логи
	@echo "${YELLOW}Очистка логов...${NC}"
	docker-compose -f $(COMPOSE_FILE) exec web python manage.py cleanup_logs
	find . -name "*.log" -type f -delete

# === УТИЛИТЫ ===

ps: status ## Алиас для status

exec: ## Выполнить команду в контейнере (use: make exec service=web cmd="ls -la")
	docker-compose -f $(COMPOSE_FILE) exec $(service) $(cmd)

scale: ## Масштабировать сервис (use: make scale service=web count=3)
	@echo "${GREEN}Масштабирование $(service) до $(count) реплик...${NC}"
	docker-compose -f $(COMPOSE_FILE) up -d --scale $(service)=$(count)

env-check: ## Проверить переменные окружения
	@echo "${GREEN}Проверка переменных окружения...${NC}"
	@if [ ! -f .env ]; then echo "${RED}Файл .env не найден! Скопируйте env.example в .env${NC}"; exit 1; fi
	@echo "${GREEN}✓ Файл .env найден${NC}"
	@docker-compose -f $(COMPOSE_FILE) config --quiet && echo "${GREEN}✓ Docker Compose конфигурация корректна${NC}" || echo "${RED}✗ Ошибка в Docker Compose конфигурации${NC}"

docs: ## Генерировать документацию
	@echo "${GREEN}Генерация документации...${NC}"
	docker-compose -f $(COMPOSE_FILE) exec web python manage.py spectacular --color --file schema.yml
	@echo "${GREEN}API схема сохранена в schema.yml${NC}"

init: env-check build up migrate createsuperuser loaddata ## Полная инициализация проекта
	@echo "${GREEN}Проект успешно инициализирован!${NC}"
	@echo "${GREEN}Приложение доступно на http://localhost${NC}"
	@echo "${GREEN}Админка доступна на http://localhost/admin${NC}"

# === DEVELOPMENT HELPERS ===

watch-logs: ## Наблюдать за логами в реальном времени
	docker-compose -f $(COMPOSE_FILE) logs -f --tail=100

fix-permissions: ## Исправить права доступа к файлам
	sudo chown -R $(USER):$(USER) .
	chmod -R 755 docker/
	chmod +x docker/*.sh

celery-status: ## Проверить статус Celery воркеров
	docker-compose -f $(COMPOSE_FILE) exec celery celery -A config inspect active
	docker-compose -f $(COMPOSE_FILE) exec celery celery -A config inspect stats

redis-cli: ## Подключиться к Redis CLI
	docker-compose -f $(COMPOSE_FILE) exec redis redis-cli -a redis_password

# === Информационные команды ===

info: ## Показать информацию о проекте
	@echo "${GREEN}Система управления дефектами${NC}"
	@echo "Версия: $(shell cat VERSION 2>/dev/null || echo 'dev')"
	@echo "Python: $(shell python --version 2>/dev/null || echo 'Не установлен')"
	@echo "Node.js: $(shell node --version 2>/dev/null || echo 'Не установлен')"
	@echo "Docker: $(shell docker --version 2>/dev/null || echo 'Не установлен')"
	@echo "Docker Compose: $(shell docker-compose --version 2>/dev/null || echo 'Не установлен')"

version: ## Показать версию
	@cat VERSION 2>/dev/null || echo "dev"

# Добавляем цель по умолчанию
.DEFAULT_GOAL := help
