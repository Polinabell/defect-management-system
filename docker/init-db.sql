-- Инициализация базы данных
-- Создание дополнительных схем если необходимо

-- Установка временной зоны
SET TIME ZONE 'UTC';

-- Создание расширений
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";