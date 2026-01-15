# Скрипт для запуска MongoDB через Docker для тестов
# Использование: .\start_mongodb_test.ps1

Write-Host "Проверка статуса MongoDB..." -ForegroundColor Cyan

# Проверяем, запущен ли контейнер
$containerName = "hh_analyzer_mongodb"
$container = docker ps -a --filter "name=$containerName" --format "{{.Names}}"

if ($container -eq $containerName) {
    $running = docker ps --filter "name=$containerName" --format "{{.Names}}"
    if ($running -eq $containerName) {
        Write-Host "MongoDB уже запущен!" -ForegroundColor Green
        exit 0
    } else {
        Write-Host "Контейнер существует, но не запущен. Запускаем..." -ForegroundColor Yellow
        docker start $containerName
    }
} else {
    Write-Host "Контейнер не найден. Запускаем через docker-compose..." -ForegroundColor Yellow
    
    # Переходим в корневую директорию проекта
    $projectRoot = Split-Path -Parent (Split-Path -Parent $PSScriptRoot)
    Push-Location $projectRoot
    
    try {
        # Запускаем только MongoDB сервис
        docker-compose up -d mongodb
        
        if ($LASTEXITCODE -ne 0) {
            Write-Host "Ошибка при запуске MongoDB через docker-compose" -ForegroundColor Red
            exit 1
        }
    } finally {
        Pop-Location
    }
}

Write-Host "Ожидание готовности MongoDB..." -ForegroundColor Cyan

# Ждем, пока MongoDB станет доступен (максимум 30 секунд)
$maxAttempts = 30
$attempt = 0
$ready = $false

while ($attempt -lt $maxAttempts -and -not $ready) {
    Start-Sleep -Seconds 1
    $attempt++
    
    try {
        $health = docker exec $containerName mongosh --eval "db.adminCommand('ping')" --quiet 2>&1
        if ($LASTEXITCODE -eq 0 -or $health -match "ok.*1") {
            $ready = $true
            Write-Host "MongoDB готов!" -ForegroundColor Green
        } else {
            Write-Host "." -NoNewline -ForegroundColor Gray
        }
    } catch {
        Write-Host "." -NoNewline -ForegroundColor Gray
    }
}

if (-not $ready) {
    Write-Host "`nMongoDB не стал доступен за $maxAttempts секунд" -ForegroundColor Red
    Write-Host "Проверьте логи: docker logs $containerName" -ForegroundColor Yellow
    exit 1
}

Write-Host "`nMongoDB успешно запущен и готов к использованию!" -ForegroundColor Green
Write-Host "Подключение: mongodb://localhost:27017" -ForegroundColor Cyan
