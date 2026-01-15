# Скрипт для запуска тестов с автоматическим управлением MongoDB
# Использование: .\run_tests_with_mongodb.ps1 [опции pytest]

param(
    [switch]$StopAfterTests = $false,
    [string[]]$TestPaths = @("tests/")
)

$ErrorActionPreference = "Stop"

Write-Host "=== Запуск тестов с MongoDB ===" -ForegroundColor Cyan

# Получаем путь к скрипту запуска MongoDB
$startScript = Join-Path $PSScriptRoot "start_mongodb_test.ps1"

# Запускаем MongoDB
Write-Host "`n[1/3] Запуск MongoDB..." -ForegroundColor Yellow
& $startScript

if ($LASTEXITCODE -ne 0) {
    Write-Host "Не удалось запустить MongoDB. Тесты не будут запущены." -ForegroundColor Red
    exit 1
}

# Переходим в директорию backend
$backendDir = Split-Path -Parent $PSScriptRoot
Push-Location $backendDir

try {
    # Запускаем тесты
    Write-Host "`n[2/3] Запуск тестов..." -ForegroundColor Yellow
    
    $testArgs = @()
    if ($TestPaths.Count -gt 0) {
        $testArgs += $TestPaths
    }
    $testArgs += "-v"
    $testArgs += "--tb=short"
    
    python -m pytest $testArgs
    
    $testExitCode = $LASTEXITCODE
    
    Write-Host "`n[3/3] Завершение..." -ForegroundColor Yellow
    
    # Останавливаем MongoDB, если указан флаг
    if ($StopAfterTests) {
        $stopScript = Join-Path $PSScriptRoot "stop_mongodb_test.ps1"
        & $stopScript
    } else {
        Write-Host "MongoDB оставлен запущенным. Для остановки используйте: .\stop_mongodb_test.ps1" -ForegroundColor Cyan
    }
    
    exit $testExitCode
} catch {
    Write-Host "Ошибка при выполнении тестов: $_" -ForegroundColor Red
    exit 1
} finally {
    Pop-Location
}
