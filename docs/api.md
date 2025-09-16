# API Документация

## Обзор API

REST API системы управления дефектами предоставляет доступ к основным функциям системы.

### Базовый URL
```
http://localhost:8000/api/v1/
```

### Аутентификация
API использует JWT токены для аутентификации:
```
Authorization: Bearer <token>
```

## Основные эндпоинты

### Проекты

#### Получить список проектов
```http
GET /api/v1/projects/
```

#### Создать новый проект
```http
POST /api/v1/projects/
Content-Type: application/json

{
  "name": "Название проекта",
  "description": "Описание проекта",
  "status": "active"
}
```

### Дефекты

#### Получить список дефектов
```http
GET /api/v1/defects/
```

#### Создать новый дефект
```http
POST /api/v1/defects/
Content-Type: application/json

{
  "title": "Название дефекта",
  "description": "Описание дефекта",
  "priority": "high",
  "status": "new",
  "project": 1
}
```

### Отчеты

#### Получить аналитику
```http
GET /api/v1/reports/analytics/
```

## Коды ответов

- `200` - Успешный запрос
- `201` - Ресурс создан
- `400` - Ошибка в запросе
- `401` - Не авторизован
- `403` - Доступ запрещен
- `404` - Ресурс не найден
- `500` - Ошибка сервера