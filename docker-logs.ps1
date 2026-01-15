# Скрипт для просмотра логов контейнеров в реальном времени

param(
    [string]$Service = "",
    [switch]$Follow = $true
)

# Добавляем Docker Toolbox в PATH
$env:PATH += ";C:\Program Files\Docker Toolbox"

# Настраиваем окружение Docker
docker-machine env default | Invoke-Expression

if ($Service) {
    Write-Host "Просмотр логов сервиса: $Service" -ForegroundColor Cyan
    if ($Follow) {
        docker-compose logs -f $Service
    } else {
        docker-compose logs --tail=100 $Service
    }
} else {
    Write-Host "Просмотр логов всех сервисов" -ForegroundColor Cyan
    if ($Follow) {
        docker-compose logs -f
    } else {
        docker-compose logs --tail=100
    }
}
