# 🚀 Быстрый запуск проекта

## Автоматический запуск (рекомендуется)

```powershell
.\start-project.ps1
```

Этот скрипт автоматически откроет два терминала:
- Backend Django (порт 8000)
- Frontend React (порт 3000)

## Ручной запуск

### 1. Запуск Backend (Django)
```powershell
cd backend
python manage.py runserver --settings=config.settings.local
```

### 2. Запуск Frontend (React)
```powershell
cd frontend
npm start
```

## 🌐 Доступ к приложению

- **Frontend**: http://localhost:3000
- **API**: http://localhost:8000/api/v1/
- **Admin панель**: http://localhost:8000/admin/

## ✅ Проект готов к использованию!

Система управления дефектами полностью настроена и готова к работе.

### Основные возможности:
- 🏠 Дашборд
- 🐛 Управление дефектами  
- 🏢 Управление проектами
- 📊 Отчёты и аналитика
- 👥 Управление пользователями
- 🔐 Аутентификация

### Технологии:
- **Backend**: Django 5.2 + DRF + SQLite
- **Frontend**: React 18 + TypeScript + Material-UI + Redux Toolkit

