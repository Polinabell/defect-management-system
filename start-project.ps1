# Скрипт запуска системы управления дефектами
Write-Host "🚀 Запуск системы управления дефектами..." -ForegroundColor Green

# Проверяем, что мы в правильной директории
if (-not (Test-Path "backend\manage.py")) {
    Write-Host "❌ Ошибка: Запустите скрипт из корневой директории проекта" -ForegroundColor Red
    exit 1
}

Write-Host "📦 Запуск Django Backend..." -ForegroundColor Yellow
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$PWD\backend'; python manage.py runserver --settings=config.settings.local"

Start-Sleep 3

Write-Host "⚛️  Запуск React Frontend..." -ForegroundColor Yellow  
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$PWD\frontend'; npm start"

Start-Sleep 5

Write-Host ""
Write-Host "✅ Система запущена!" -ForegroundColor Green
Write-Host "🌐 Frontend: http://localhost:3000" -ForegroundColor Cyan
Write-Host "🔧 Backend API: http://localhost:8000/api/v1/" -ForegroundColor Cyan
Write-Host "⚙️  Admin: http://localhost:8000/admin/" -ForegroundColor Cyan
Write-Host ""
Write-Host "Press any key to exit..." -ForegroundColor Gray
$null = $Host.UI.RawUI.ReadKey('NoEcho,IncludeKeyDown')
