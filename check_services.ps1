# Quick service status check
Write-Host "`n=== HH Resume Analyzer - Service Status ===" -ForegroundColor Cyan

# Check Backend
try {
    $response = Invoke-WebRequest -Uri "http://localhost:8000/health" -TimeoutSec 2 -UseBasicParsing
    Write-Host "[OK] Backend API: http://localhost:8000" -ForegroundColor Green
} catch {
    Write-Host "[WARN] Backend: Not responding yet (may be starting)" -ForegroundColor Yellow
    Write-Host "       Check: http://localhost:8000" -ForegroundColor Gray
}

# Check Frontend
try {
    $response = Invoke-WebRequest -Uri "http://localhost:3000" -TimeoutSec 2 -UseBasicParsing
    Write-Host "[OK] Frontend: http://localhost:3000" -ForegroundColor Green
} catch {
    Write-Host "[WARN] Frontend: Not responding" -ForegroundColor Yellow
}

# Check processes
$backend = Get-Process | Where-Object { (Get-CimInstance Win32_Process -Filter "ProcessId = $($_.Id)").CommandLine -like "*uvicorn*" } | Measure-Object
$celery = Get-Process | Where-Object { (Get-CimInstance Win32_Process -Filter "ProcessId = $($_.Id)").CommandLine -like "*celery*" } | Measure-Object
$frontend = Get-Process | Where-Object { (Get-CimInstance Win32_Process -Filter "ProcessId = $($_.Id)").CommandLine -like "*vite*" -or (Get-CimInstance Win32_Process -Filter "ProcessId = $($_.Id)").CommandLine -like "*node*dev*" } | Measure-Object

Write-Host "`nProcess Status:" -ForegroundColor Cyan
Write-Host "  Backend processes: $($backend.Count)" -ForegroundColor $(if ($backend.Count -gt 0) { "Green" } else { "Red" })
Write-Host "  Celery workers: $($celery.Count)" -ForegroundColor $(if ($celery.Count -gt 0) { "Green" } else { "Yellow" })
Write-Host "  Frontend processes: $($frontend.Count)" -ForegroundColor $(if ($frontend.Count -gt 0) { "Green" } else { "Red" })

Write-Host "`n========================================`n" -ForegroundColor Cyan
