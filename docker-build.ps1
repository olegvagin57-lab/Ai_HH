# Скрипт для сборки Docker образов с подробными логами

param(
    [switch]$Watch = $false
)

# Добавляем Docker Toolbox в PATH
$env:PATH += ";C:\Program Files\Docker Toolbox"

# Настраиваем окружение Docker
docker-machine env default | Invoke-Expression

Write-Host "=========================================" -ForegroundColor Cyan
Write-Host "  Сборка Docker образов HH_AI" -ForegroundColor Cyan
Write-Host "=========================================" -ForegroundColor Cyan
Write-Host ""

if ($Watch) {
    Write-Host "Режим мониторинга: логи будут обновляться в реальном времени" -ForegroundColor Yellow
    Write-Host "Нажмите Ctrl+C для остановки" -ForegroundColor Yellow
    Write-Host ""
    
    # Запускаем сборку в фоне и показываем логи
    $buildJob = Start-Job -ScriptBlock {
        Set-Location $using:PWD
        $env:PATH += ";C:\Program Files\Docker Toolbox"
        docker-machine env default | Invoke-Expression
        docker-compose build --progress=plain 2>&1
    }
    
    # Показываем логи в реальном времени
    while ($buildJob.State -eq "Running") {
        $output = Receive-Job -Job $buildJob
        if ($output) {
            $output | ForEach-Object {
                if ($_ -match "Step \d+/\d+") {
                    Write-Host $_ -ForegroundColor Green
                } elseif ($_ -match "ERROR|FAILED|error|failed") {
                    Write-Host $_ -ForegroundColor Red
                } elseif ($_ -match "Installing|Building|Downloading") {
                    Write-Host $_ -ForegroundColor Yellow
                } else {
                    Write-Host $_
                }
            }
        }
        Start-Sleep -Milliseconds 500
    }
    
    # Получаем оставшиеся логи
    $finalOutput = Receive-Job -Job $buildJob
    if ($finalOutput) {
        $finalOutput | ForEach-Object { Write-Host $_ }
    }
    
    Remove-Job -Job $buildJob
    
    if ($buildJob.State -eq "Completed") {
        Write-Host ""
        Write-Host "Сборка завершена!" -ForegroundColor Green
    } else {
        Write-Host ""
        Write-Host "Сборка завершена с ошибками!" -ForegroundColor Red
    }
} else {
    Write-Host "Запуск сборки с подробными логами..." -ForegroundColor Yellow
    Write-Host ""
    
    # Собираем образы с подробным выводом
    docker-compose build --progress=plain
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host ""
        Write-Host "Сборка завершена успешно!" -ForegroundColor Green
        Write-Host "Запуск контейнеров..." -ForegroundColor Yellow
        docker-compose up -d
    } else {
        Write-Host ""
        Write-Host "Ошибка при сборке!" -ForegroundColor Red
        exit 1
    }
}
