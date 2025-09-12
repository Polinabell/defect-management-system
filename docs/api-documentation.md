# API Документация системы управления дефектами

## Содержание

1. [Введение](#введение)
2. [Аутентификация](#аутентификация)
3. [Базовые принципы](#базовые-принципы)
4. [Endpoints](#endpoints)
5. [Коды ошибок](#коды-ошибок)
6. [Примеры использования](#примеры-использования)

## Введение

REST API системы управления дефектами предоставляет программный доступ ко всем основным функциям системы. API использует JSON для обмена данными и JWT токены для аутентификации.

### Базовый URL

```
https://yourdomain.com/api/v1/
```

### Версионирование

API использует версионирование через URL. Текущая версия: `v1`

## Аутентификация

### JWT Токены

API использует JSON Web Tokens (JWT) для аутентификации. После успешного входа вы получите access и refresh токены.

#### Получение токенов

```http
POST /api/v1/auth/token/
Content-Type: application/json

{
    "email": "user@example.com",
    "password": "password123"
}
```

**Ответ:**
```json
{
    "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
    "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
    "user": {
        "id": 1,
        "email": "user@example.com",
        "first_name": "Иван",
        "last_name": "Петров",
        "role": "engineer"
    }
}
```

#### Обновление токена

```http
POST /api/v1/auth/token/refresh/
Content-Type: application/json

{
    "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
}
```

#### Использование токена

Добавьте токен в заголовок Authorization:

```http
Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...
```

## Базовые принципы

### Формат данных

- **Content-Type**: `application/json`
- **Accept**: `application/json`

### Пагинация

Списки данных поддерживают пагинацию:

```json
{
    "count": 100,
    "next": "https://api.example.com/defects/?page=2",
    "previous": null,
    "results": [...]
}
```

### Фильтрация

Поддерживаются следующие параметры фильтрации:

- `search` - поиск по тексту
- `ordering` - сортировка
- `page` - номер страницы
- `page_size` - размер страницы

### Форматы дат

Все даты передаются в формате ISO 8601:

```
2024-12-15T10:30:00Z
```

## Endpoints

### Аутентификация

#### POST /auth/token/
Получение JWT токенов

**Параметры:**
```json
{
    "email": "string",
    "password": "string"
}
```

#### POST /auth/token/refresh/
Обновление access токена

**Параметры:**
```json
{
    "refresh": "string"
}
```

#### POST /auth/logout/
Выход из системы

### Пользователи

#### GET /users/
Получение списка пользователей

**Параметры запроса:**
- `search` - поиск по имени или email
- `role` - фильтр по роли
- `is_active` - фильтр по активности

**Ответ:**
```json
{
    "count": 10,
    "results": [
        {
            "id": 1,
            "email": "user@example.com",
            "first_name": "Иван",
            "last_name": "Петров",
            "role": "engineer",
            "is_active": true,
            "date_joined": "2024-01-15T10:30:00Z"
        }
    ]
}
```

#### GET /users/{id}/
Получение информации о пользователе

#### PUT /users/{id}/
Обновление пользователя

#### POST /users/
Создание нового пользователя

### Проекты

#### GET /projects/
Получение списка проектов

**Параметры запроса:**
- `search` - поиск по названию
- `manager` - фильтр по менеджеру
- `status` - фильтр по статусу

**Ответ:**
```json
{
    "count": 5,
    "results": [
        {
            "id": 1,
            "name": "Веб-приложение",
            "description": "Разработка веб-приложения",
            "manager": {
                "id": 1,
                "first_name": "Анна",
                "last_name": "Сидорова"
            },
            "status": "active",
            "start_date": "2024-01-01",
            "end_date": "2024-06-30",
            "created_at": "2024-01-01T00:00:00Z"
        }
    ]
}
```

#### GET /projects/{id}/
Получение информации о проекте

#### POST /projects/
Создание нового проекта

**Параметры:**
```json
{
    "name": "string",
    "description": "string",
    "start_date": "2024-01-01",
    "end_date": "2024-06-30"
}
```

#### PUT /projects/{id}/
Обновление проекта

#### DELETE /projects/{id}/
Удаление проекта

### Дефекты

#### GET /defects/
Получение списка дефектов

**Параметры запроса:**
- `project` - фильтр по проекту
- `status` - фильтр по статусу
- `assignee` - фильтр по исполнителю
- `author` - фильтр по автору
- `priority` - фильтр по приоритету
- `severity` - фильтр по серьезности
- `category` - фильтр по категории

**Ответ:**
```json
{
    "count": 25,
    "results": [
        {
            "id": 1,
            "title": "Ошибка входа в систему",
            "description": "Пользователь не может войти в систему",
            "status": "new",
            "priority": "high",
            "severity": "critical",
            "project": {
                "id": 1,
                "name": "Веб-приложение"
            },
            "author": {
                "id": 2,
                "first_name": "Петр",
                "last_name": "Иванов"
            },
            "assignee": null,
            "category": {
                "id": 1,
                "name": "Функциональные ошибки"
            },
            "created_at": "2024-12-15T10:30:00Z",
            "updated_at": "2024-12-15T10:30:00Z"
        }
    ]
}
```

#### GET /defects/{id}/
Получение информации о дефекте

#### POST /defects/
Создание нового дефекта

**Параметры:**
```json
{
    "title": "string",
    "description": "string",
    "project": 1,
    "category": 1,
    "priority": "low",
    "severity": "minor"
}
```

#### PUT /defects/{id}/
Обновление дефекта

#### DELETE /defects/{id}/
Удаление дефекта

#### POST /defects/{id}/assign/
Назначение исполнителя

**Параметры:**
```json
{
    "assignee": 1
}
```

#### POST /defects/{id}/status/
Изменение статуса дефекта

**Параметры:**
```json
{
    "status": "in_progress",
    "comment": "Начинаю работу над дефектом"
}
```

### Комментарии

#### GET /defects/{defect_id}/comments/
Получение комментариев к дефекту

#### POST /defects/{defect_id}/comments/
Добавление комментария

**Параметры:**
```json
{
    "text": "string"
}
```

### Файлы

#### GET /defects/{defect_id}/files/
Получение списка файлов дефекта

#### POST /defects/{defect_id}/files/
Загрузка файла

**Параметры:**
- `file` - файл (multipart/form-data)
- `description` - описание файла

#### DELETE /defects/{defect_id}/files/{file_id}/
Удаление файла

### Уведомления

#### GET /notifications/
Получение списка уведомлений

**Параметры запроса:**
- `is_read` - фильтр по статусу прочтения
- `type` - фильтр по типу

#### GET /notifications/{id}/
Получение уведомления

#### PATCH /notifications/{id}/
Отметка уведомления как прочитанного

#### POST /notifications/mark-all-read/
Отметка всех уведомлений как прочитанных

### Отчеты

#### GET /reports/defects/
Отчет по дефектам

**Параметры запроса:**
- `project` - ID проекта
- `start_date` - дата начала
- `end_date` - дата окончания
- `format` - формат отчета (json, pdf, excel)

#### GET /reports/performance/
Отчет по производительности

#### GET /reports/categories/
Отчет по категориям дефектов

## Коды ошибок

### HTTP статус коды

- `200` - OK
- `201` - Created
- `400` - Bad Request
- `401` - Unauthorized
- `403` - Forbidden
- `404` - Not Found
- `405` - Method Not Allowed
- `429` - Too Many Requests
- `500` - Internal Server Error

### Формат ошибок

```json
{
    "error": "string",
    "message": "string",
    "details": {
        "field_name": ["Ошибка валидации"]
    }
}
```

### Примеры ошибок

#### 400 Bad Request
```json
{
    "error": "validation_error",
    "message": "Ошибка валидации данных",
    "details": {
        "title": ["Это поле обязательно для заполнения"],
        "email": ["Введите корректный email адрес"]
    }
}
```

#### 401 Unauthorized
```json
{
    "error": "authentication_failed",
    "message": "Неверные учетные данные"
}
```

#### 403 Forbidden
```json
{
    "error": "permission_denied",
    "message": "У вас нет прав для выполнения этого действия"
}
```

#### 404 Not Found
```json
{
    "error": "not_found",
    "message": "Ресурс не найден"
}
```

## Примеры использования

### Создание дефекта

```bash
curl -X POST https://api.example.com/api/v1/defects/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Ошибка входа в систему",
    "description": "Пользователь не может войти в систему после ввода правильных данных",
    "project": 1,
    "category": 1,
    "priority": "high",
    "severity": "critical"
  }'
```

### Получение списка дефектов с фильтрацией

```bash
curl -X GET "https://api.example.com/api/v1/defects/?project=1&status=new&priority=high" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

### Назначение исполнителя

```bash
curl -X POST https://api.example.com/api/v1/defects/1/assign/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "assignee": 2
  }'
```

### Загрузка файла

```bash
curl -X POST https://api.example.com/api/v1/defects/1/files/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -F "file=@screenshot.png" \
  -F "description=Скриншот ошибки"
```

### Получение отчета

```bash
curl -X GET "https://api.example.com/api/v1/reports/defects/?project=1&start_date=2024-01-01&end_date=2024-12-31&format=excel" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -o report.xlsx
```

### Обработка ошибок в коде

```python
import requests

def create_defect(title, description, project_id):
    url = "https://api.example.com/api/v1/defects/"
    headers = {
        "Authorization": "Bearer YOUR_ACCESS_TOKEN",
        "Content-Type": "application/json"
    }
    data = {
        "title": title,
        "description": description,
        "project": project_id
    }
    
    try:
        response = requests.post(url, json=data, headers=headers)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 400:
            error_data = e.response.json()
            print(f"Ошибка валидации: {error_data['message']}")
            for field, errors in error_data.get('details', {}).items():
                print(f"{field}: {', '.join(errors)}")
        elif e.response.status_code == 401:
            print("Ошибка аутентификации. Проверьте токен.")
        elif e.response.status_code == 403:
            print("Недостаточно прав для выполнения операции.")
        else:
            print(f"Ошибка сервера: {e.response.status_code}")
        raise
```

---

**Версия API**: 1.0  
**Дата обновления**: Декабрь 2024  
**Автор**: Команда разработки системы управления дефектами
