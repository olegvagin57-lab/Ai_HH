# SSL Certificate Setup Script for Windows
# This script helps set up SSL certificates for production

param(
    [string]$Domain = "yourdomain.com",
    [string]$Email = "admin@yourdomain.com"
)

Write-Host "Setting up SSL certificates for domain: $Domain" -ForegroundColor Green
Write-Host "Email: $Email" -ForegroundColor Green

# Check if certbot is available
$certbotPath = Get-Command certbot -ErrorAction SilentlyContinue

if (-not $certbotPath) {
    Write-Host "Certbot is not installed." -ForegroundColor Yellow
    Write-Host "Please install certbot using one of the following methods:" -ForegroundColor Yellow
    Write-Host "1. Install via WSL: wsl sudo apt-get install certbot" -ForegroundColor Yellow
    Write-Host "2. Install via Docker: docker run -it --rm certbot/certbot certonly --standalone -d $Domain" -ForegroundColor Yellow
    Write-Host "3. Use Windows Subsystem for Linux (WSL)" -ForegroundColor Yellow
    exit 1
}

# Create directories
New-Item -ItemType Directory -Force -Path "nginx\ssl" | Out-Null
New-Item -ItemType Directory -Force -Path "nginx\logs" | Out-Null

Write-Host "`nTo generate SSL certificates, run one of the following:" -ForegroundColor Cyan
Write-Host "`nOption 1: Using Docker (Recommended for Windows):" -ForegroundColor Yellow
Write-Host "docker run -it --rm -v `"${PWD}\nginx\ssl:/etc/letsencrypt`" certbot/certbot certonly --standalone -d $Domain -d www.$Domain --email $Email --agree-tos" -ForegroundColor White

Write-Host "`nOption 2: Using WSL:" -ForegroundColor Yellow
Write-Host "wsl sudo certbot certonly --standalone -d $Domain -d www.$Domain --email $Email --agree-tos" -ForegroundColor White

Write-Host "`nAfter generating certificates:" -ForegroundColor Cyan
Write-Host "1. Copy fullchain.pem, privkey.pem, and chain.pem to nginx\ssl\" -ForegroundColor White
Write-Host "2. Update nginx\nginx.prod.conf with your domain name" -ForegroundColor White
Write-Host "3. Update docker-compose.prod.yml with your domain name" -ForegroundColor White

Write-Host "`nFor Let's Encrypt certificates, they expire every 90 days." -ForegroundColor Yellow
Write-Host "Set up automatic renewal using a scheduled task or cron job." -ForegroundColor Yellow
