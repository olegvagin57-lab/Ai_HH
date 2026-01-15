# Скрипт для остановки MongoDB контейнера
# Использование: .\stop_mongodb_test.ps1

Write-Host "Остановка MongoDB..." -ForegroundColor Cyan

$containerName = "hh_analyzer_mongodb"
$container = docker ps --filter "name=$containerName" --format "{{.Names}}"

if ($container -eq $containerName) {
    docker stop $containerName
    if ($LASTEXITCODE -eq 0) {
        Write-Host "MongoDB остановлен!" -ForegroundColor Green
    } else {
        Write-Host "Ошибка при остановке MongoDB" -ForegroundColor Red
        exit 1
    }
} else {
    Write-Host "MongoDB не запущен" -ForegroundColor Yellow
}
