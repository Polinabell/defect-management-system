-- Инициализация базы данных для системы управления дефектами
-- Этот скрипт выполняется при первом запуске PostgreSQL контейнера

-- Создание базы данных (уже создается через POSTGRES_DB)
-- CREATE DATABASE defect_management;

-- Создание пользователя для приложения (если нужно отдельно от postgres)
-- CREATE USER defect_user WITH PASSWORD 'defect_password';
-- GRANT ALL PRIVILEGES ON DATABASE defect_management TO defect_user;

-- Установка расширений PostgreSQL
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";
CREATE EXTENSION IF NOT EXISTS "unaccent";

-- Настройка для полнотекстового поиска
CREATE TEXT SEARCH CONFIGURATION russian_simple (COPY = simple);

-- Комментарий о том, что база готова
COMMENT ON DATABASE defect_management IS 'База данных системы управления дефектами';

-- Логирование инициализации
\echo 'База данных defect_management успешно инициализирована'

