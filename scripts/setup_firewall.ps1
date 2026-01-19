# Скрипт для настройки Windows Firewall для HH Resume Analyzer

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Настройка Windows Firewall" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Проверка прав администратора
$isAdmin = ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)

if (-not $isAdmin) {
    Write-Host "❌ Этот скрипт требует прав администратора" -ForegroundColor Red
    Write-Host "Запустите PowerShell от имени администратора" -ForegroundColor Yellow
    exit 1
}

Write-Host "✅ Права администратора подтверждены" -ForegroundColor Green
Write-Host ""

# Удаление старых правил (если есть)
Write-Host "Удаление старых правил (если есть)..." -ForegroundColor Yellow
Remove-NetFirewallRule -DisplayName "HH Analyzer Frontend" -ErrorAction SilentlyContinue
Remove-NetFirewallRule -DisplayName "HH Analyzer Backend" -ErrorAction SilentlyContinue
Remove-NetFirewallRule -DisplayName "HH Analyzer MongoDB" -ErrorAction SilentlyContinue
Remove-NetFirewallRule -DisplayName "HH Analyzer Redis" -ErrorAction SilentlyContinue

# Создание правил для Frontend
Write-Host "Создание правила для Frontend (порт 3000)..." -ForegroundColor Yellow
New-NetFirewallRule -DisplayName "HH Analyzer Frontend" `
    -Direction Inbound `
    -LocalPort 3000 `
    -Protocol TCP `
    -Action Allow `
    -Description "Allow inbound connections to HH Resume Analyzer Frontend" | Out-Null

# Создание правил для Backend
Write-Host "Создание правила для Backend API (порт 8000)..." -ForegroundColor Yellow
New-NetFirewallRule -DisplayName "HH Analyzer Backend" `
    -Direction Inbound `
    -LocalPort 8000 `
    -Protocol TCP `
    -Action Allow `
    -Description "Allow inbound connections to HH Resume Analyzer Backend API" | Out-Null

# Создание правил для MongoDB (опционально, если нужен внешний доступ)
$includeMongo = Read-Host "Открыть порт MongoDB (27017) для внешнего доступа? (y/n)"
if ($includeMongo -eq "y" -or $includeMongo -eq "Y") {
    Write-Host "Создание правила для MongoDB (порт 27017)..." -ForegroundColor Yellow
    New-NetFirewallRule -DisplayName "HH Analyzer MongoDB" `
        -Direction Inbound `
        -LocalPort 27017 `
        -Protocol TCP `
        -Action Allow `
        -Description "Allow inbound connections to MongoDB" | Out-Null
    Write-Host "⚠️  ВНИМАНИЕ: MongoDB открыт для внешнего доступа. Убедитесь, что настроена аутентификация!" -ForegroundColor Red
}

# Создание правил для Redis (опционально, если нужен внешний доступ)
$includeRedis = Read-Host "Открыть порт Redis (6379) для внешнего доступа? (y/n)"
if ($includeRedis -eq "y" -or $includeRedis -eq "Y") {
    Write-Host "Создание правила для Redis (порт 6379)..." -ForegroundColor Yellow
    New-NetFirewallRule -DisplayName "HH Analyzer Redis" `
        -Direction Inbound `
        -LocalPort 6379 `
        -Protocol TCP `
        -Action Allow `
        -Description "Allow inbound connections to Redis" | Out-Null
    Write-Host "⚠️  ВНИМАНИЕ: Redis открыт для внешнего доступа. Убедитесь, что настроена аутентификация!" -ForegroundColor Red
}

Write-Host ""
Write-Host "✅ Правила firewall созданы успешно" -ForegroundColor Green
Write-Host ""
Write-Host "Созданные правила:" -ForegroundColor Cyan
Get-NetFirewallRule -DisplayName "HH Analyzer*" | Format-Table DisplayName, Enabled, Direction, Action

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Важно:" -ForegroundColor Yellow
Write-Host "1. Убедитесь, что роутер настроен для проброса портов" -ForegroundColor White
Write-Host "2. Настройте CORS_ORIGINS в .env файле" -ForegroundColor White
Write-Host "3. Используйте сильные пароли для безопасности" -ForegroundColor White
Write-Host "========================================" -ForegroundColor Cyan
