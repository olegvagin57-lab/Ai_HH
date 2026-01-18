# Test script for Docker build locally (PowerShell)
# Usage: .\scripts\test-docker-build.ps1

param(
    [string]$DockerUsername = $env:DOCKER_USERNAME,
    [string]$DockerPassword = $env:DOCKER_PASSWORD
)

if (-not $DockerUsername) {
    Write-Host "❌ Error: DOCKER_USERNAME environment variable is not set!" -ForegroundColor Red
    Write-Host "Set it with: `$env:DOCKER_USERNAME='your-username'" -ForegroundColor Yellow
    exit 1
}

if (-not $DockerPassword) {
    Write-Host "❌ Error: DOCKER_PASSWORD environment variable is not set!" -ForegroundColor Red
    Write-Host "Set it with: `$env:DOCKER_PASSWORD='your-password'" -ForegroundColor Yellow
    exit 1
}

Write-Host "✅ Docker Hub credentials are configured" -ForegroundColor Green
Write-Host "Username: $DockerUsername"
Write-Host "Username length: $($DockerUsername.Length)"

# Test login
Write-Host "Logging in to Docker Hub..." -ForegroundColor Cyan
echo $DockerPassword | docker login -u $DockerUsername --password-stdin

# Test tag format
$ShortSha = "test123"
$BackendTag = "${DockerUsername}/hh-analyzer-backend:latest"
$FrontendTag = "${DockerUsername}/hh-analyzer-frontend:latest"

Write-Host ""
Write-Host "Tags that will be used:" -ForegroundColor Cyan
Write-Host "Backend: $BackendTag"
Write-Host "Frontend: $FrontendTag"

# Validate tag format (Docker tags must be lowercase and contain only [a-z0-9._-])
$TagPattern = '^[a-z0-9._-]+/[a-z0-9._-]+:[a-z0-9._-]+$'

if ($BackendTag -notmatch $TagPattern) {
    Write-Host "❌ Error: Invalid tag format for backend: $BackendTag" -ForegroundColor Red
    Write-Host "Tags must be lowercase and contain only: [a-z0-9._-]" -ForegroundColor Yellow
    exit 1
}

if ($FrontendTag -notmatch $TagPattern) {
    Write-Host "❌ Error: Invalid tag format for frontend: $FrontendTag" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "✅ All tag formats are valid!" -ForegroundColor Green
Write-Host ""
Write-Host "To test build locally, run:" -ForegroundColor Cyan
Write-Host "  docker build -t $BackendTag ./backend"
Write-Host "  docker build -t $FrontendTag ./frontend"
