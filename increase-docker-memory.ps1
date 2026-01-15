# Скрипт для увеличения памяти Docker Machine

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Увеличение памяти Docker Machine" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

$env:PATH += ";C:\Program Files\Docker Toolbox"

# Проверка текущей памяти
Write-Host "Текущая память:" -ForegroundColor Yellow
docker-machine inspect default --format "{{.Driver.Memory}}" 2>$null

Write-Host ""
Write-Host "Остановка Docker Machine..." -ForegroundColor Yellow
docker-machine stop default

Write-Host ""
Write-Host "========================================" -ForegroundColor Green
Write-Host "  ИНСТРУКЦИЯ:" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""
Write-Host "1. Откройте VirtualBox Manager" -ForegroundColor White
Write-Host "2. Найдите машину 'default'" -ForegroundColor White
Write-Host "3. Правый клик -> Settings -> System -> Motherboard" -ForegroundColor White
Write-Host "4. Увеличьте Base Memory до 4096 MB (4 GB)" -ForegroundColor White
Write-Host "5. Нажмите OK" -ForegroundColor White
Write-Host ""
Write-Host "После изменения нажмите Enter для продолжения..." -ForegroundColor Yellow
Read-Host

Write-Host ""
Write-Host "Запуск Docker Machine..." -ForegroundColor Yellow
docker-machine start default

Write-Host ""
Write-Host "Настройка окружения..." -ForegroundColor Yellow
docker-machine env default | Invoke-Expression

Write-Host ""
Write-Host "Проверка новой памяти:" -ForegroundColor Yellow
$newMemory = docker-machine inspect default --format "{{.Driver.Memory}}"
Write-Host "Память: $newMemory MB" -ForegroundColor Green

if ([int]$newMemory -ge 3072) {
    Write-Host ""
    Write-Host "Отлично! Память увеличена. Можно запускать сборку." -ForegroundColor Green
} else {
    Write-Host ""
    Write-Host "Внимание: Память все еще меньше 3GB. Рекомендуется увеличить до 4GB." -ForegroundColor Yellow
}
