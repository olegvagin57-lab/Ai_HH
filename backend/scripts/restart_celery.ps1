# Restart Celery Worker
Write-Host "Остановка старых процессов Celery..." -ForegroundColor Yellow

# Stop all Celery workers
Get-Process | Where-Object {
    $_.ProcessName -eq "python" -and 
    (Get-WmiObject Win32_Process -Filter "ProcessId = $($_.Id)").CommandLine -like "*celery*worker*"
} | Stop-Process -Force -ErrorAction SilentlyContinue

Start-Sleep -Seconds 2

Write-Host "Запуск нового Celery Worker..." -ForegroundColor Green

# Start new worker in new window
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd C:\Users\Oleg\.cursor\Ai_HH\backend; Write-Host '=== CELERY WORKER ===' -ForegroundColor Cyan; Write-Host ''; celery -A celery_app.celery worker --loglevel=info --concurrency=2"

Write-Host "✅ Celery Worker перезапущен!" -ForegroundColor Green
Write-Host ""
Write-Host "Проверьте новое окно PowerShell с worker'ом" -ForegroundColor Yellow
