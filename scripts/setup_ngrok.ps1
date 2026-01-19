# Скрипт для настройки ngrok на Windows

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Настройка ngrok для HH Resume Analyzer" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Проверка наличия ngrok
$ngrokPath = "C:\ngrok\ngrok.exe"
if (-not (Test-Path $ngrokPath)) {
    Write-Host "❌ ngrok не найден по пути: $ngrokPath" -ForegroundColor Red
    Write-Host ""
    Write-Host "Установка ngrok:" -ForegroundColor Yellow
    Write-Host "1. Скачайте ngrok с https://ngrok.com/download" -ForegroundColor Yellow
    Write-Host "2. Распакуйте в C:\ngrok\" -ForegroundColor Yellow
    Write-Host "3. Зарегистрируйтесь на https://dashboard.ngrok.com" -ForegroundColor Yellow
    Write-Host "4. Получите токен авторизации" -ForegroundColor Yellow
    Write-Host ""
    exit 1
}

Write-Host "✅ ngrok найден" -ForegroundColor Green
Write-Host ""

# Запрос токена авторизации
$authToken = Read-Host "Введите ваш ngrok auth token (или нажмите Enter, если уже настроен)"

if ($authToken) {
    Write-Host "Настройка ngrok..." -ForegroundColor Yellow
    & $ngrokPath authtoken $authToken
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ ngrok настроен успешно" -ForegroundColor Green
    } else {
        Write-Host "❌ Ошибка настройки ngrok" -ForegroundColor Red
        exit 1
    }
} else {
    Write-Host "Пропущена настройка токена (уже настроен)" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "Выберите порт для туннеля:" -ForegroundColor Cyan
Write-Host "1. Frontend (порт 3000)" -ForegroundColor White
Write-Host "2. Backend API (порт 8000)" -ForegroundColor White
Write-Host "3. Оба (в отдельных окнах)" -ForegroundColor White
Write-Host ""

$choice = Read-Host "Ваш выбор (1-3)"

switch ($choice) {
    "1" {
        Write-Host ""
        Write-Host "Запуск ngrok для Frontend (порт 3000)..." -ForegroundColor Yellow
        Write-Host "URL будет показан в консоли ngrok" -ForegroundColor Yellow
        Write-Host ""
        & $ngrokPath http 3000
    }
    "2" {
        Write-Host ""
        Write-Host "Запуск ngrok для Backend API (порт 8000)..." -ForegroundColor Yellow
        Write-Host "URL будет показан в консоли ngrok" -ForegroundColor Yellow
        Write-Host ""
        & $ngrokPath http 8000
    }
    "3" {
        Write-Host ""
        Write-Host "Запуск ngrok для Frontend в новом окне..." -ForegroundColor Yellow
        Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd C:\ngrok; .\ngrok.exe http 3000"
        
        Write-Host "Запуск ngrok для Backend в новом окне..." -ForegroundColor Yellow
        Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd C:\ngrok; .\ngrok.exe http 8000"
        
        Write-Host ""
        Write-Host "✅ Оба туннеля запущены в отдельных окнах" -ForegroundColor Green
        Write-Host "Скопируйте URL из консоли ngrok и добавьте в CORS_ORIGINS в .env файле" -ForegroundColor Yellow
    }
    default {
        Write-Host "❌ Неверный выбор" -ForegroundColor Red
        exit 1
    }
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Важно:" -ForegroundColor Yellow
Write-Host "1. Скопируйте ngrok URL из консоли" -ForegroundColor White
Write-Host "2. Добавьте его в CORS_ORIGINS в .env файле" -ForegroundColor White
Write-Host "3. Перезапустите backend после изменения .env" -ForegroundColor White
Write-Host "========================================" -ForegroundColor Cyan
