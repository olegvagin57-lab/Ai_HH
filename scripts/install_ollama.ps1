# Install Ollama script for Windows
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Ollama Installation for Windows" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Check if Ollama is installed
$ollamaInstalled = Get-Command ollama -ErrorAction SilentlyContinue

if ($ollamaInstalled) {
    Write-Host "Ollama is already installed!" -ForegroundColor Green
    ollama --version
    Write-Host ""
    Write-Host "Installing model..." -ForegroundColor Yellow
} else {
    Write-Host "Ollama is not installed. Please install manually." -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Instructions:" -ForegroundColor Cyan
    Write-Host "1. Open browser: https://ollama.com/download/windows" -ForegroundColor White
    Write-Host "2. Download Ollama installer for Windows" -ForegroundColor White
    Write-Host "3. Run installer and follow instructions" -ForegroundColor White
    Write-Host "4. Restart PowerShell after installation" -ForegroundColor White
    Write-Host ""
    Write-Host "Or use winget (if installed):" -ForegroundColor Cyan
    Write-Host "  winget install Ollama.Ollama" -ForegroundColor White
    Write-Host ""
    
    $install = Read-Host "Open download page in browser? (Y/N)"
    if ($install -eq "Y" -or $install -eq "y") {
        Start-Process "https://ollama.com/download/windows"
    }
    
    Write-Host ""
    Write-Host "After installation, run this script again to install the model." -ForegroundColor Yellow
    exit
}

# Install model
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Installing Mistral 7B model" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "This will take several minutes (model is ~4.1 GB)..." -ForegroundColor Yellow
Write-Host ""

try {
    Write-Host "Downloading mistral model..." -ForegroundColor Yellow
    ollama pull mistral
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host ""
        Write-Host "Model installed successfully!" -ForegroundColor Green
        Write-Host ""
        
        # List installed models
        Write-Host "Installed models:" -ForegroundColor Cyan
        ollama list
        
        Write-Host ""
        Write-Host "Testing model..." -ForegroundColor Cyan
        ollama run mistral "Hello! Answer in one word: working?"
        
        Write-Host ""
        Write-Host "========================================" -ForegroundColor Green
        Write-Host "Ollama is ready to use!" -ForegroundColor Green
        Write-Host "========================================" -ForegroundColor Green
        Write-Host ""
        Write-Host "Now you can test hybrid approach:" -ForegroundColor Cyan
        Write-Host "  cd backend" -ForegroundColor White
        Write-Host "  python scripts/test_hybrid_ai.py" -ForegroundColor White
    } else {
        Write-Host "Error installing model" -ForegroundColor Red
    }
} catch {
    Write-Host "Error: $_" -ForegroundColor Red
}
