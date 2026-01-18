# MongoDB Backup Script for Windows
# This script creates a backup of MongoDB database

param(
    [string]$BackupDir = "./backups",
    [int]$RetentionDays = 30,
    [string]$MongoDBUrl = $env:MONGODB_URL,
    [string]$MongoDBDatabase = $env:MONGODB_DATABASE
)

if (-not $MongoDBUrl) {
    $MongoDBUrl = "mongodb://localhost:27017"
}

if (-not $MongoDBDatabase) {
    $MongoDBDatabase = "hh_analyzer"
}

$Timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
$BackupName = "mongodb_backup_${MongoDBDatabase}_${Timestamp}"

Write-Host "Starting MongoDB backup..." -ForegroundColor Green

# Create backup directory
if (-not (Test-Path $BackupDir)) {
    New-Item -ItemType Directory -Path $BackupDir | Out-Null
}

# Parse MongoDB URL
if ($MongoDBUrl -match "^mongodb://(.+?)(?::(\d+))?(?:/(.+))?$") {
    $Host = $matches[1]
    $Port = if ($matches[2]) { $matches[2] } else { "27017" }
} else {
    Write-Host "Invalid MONGODB_URL format. Expected: mongodb://host:port" -ForegroundColor Red
    exit 1
}

# Check if mongodump is available
$mongodumpPath = Get-Command mongodump -ErrorAction SilentlyContinue
if (-not $mongodumpPath) {
    Write-Host "mongodump is not installed." -ForegroundColor Red
    Write-Host "Please install MongoDB Database Tools from: https://www.mongodb.com/try/download/database-tools" -ForegroundColor Yellow
    exit 1
}

# Perform backup
Write-Host "Backing up database: $MongoDBDatabase" -ForegroundColor Yellow
Write-Host "Host: ${Host}:${Port}" -ForegroundColor Yellow

$backupPath = Join-Path $BackupDir $BackupName

try {
    & mongodump --host "${Host}:${Port}" --db $MongoDBDatabase --out $backupPath --gzip
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "Backup completed successfully!" -ForegroundColor Green
        Write-Host "Backup location: $backupPath" -ForegroundColor Green
        
        # Create archive
        Write-Host "Creating archive..." -ForegroundColor Yellow
        $archivePath = Join-Path $BackupDir "${BackupName}.tar.gz"
        
        # Use 7-Zip or tar if available
        $tarPath = Get-Command tar -ErrorAction SilentlyContinue
        if ($tarPath) {
            Set-Location $BackupDir
            & tar -czf "${BackupName}.tar.gz" $BackupName
            Remove-Item -Recurse -Force $BackupName
            Set-Location ..
        } else {
            # Use Compress-Archive (creates .zip instead of .tar.gz)
            $zipPath = Join-Path $BackupDir "${BackupName}.zip"
            Compress-Archive -Path $backupPath -DestinationPath $zipPath -Force
            Remove-Item -Recurse -Force $backupPath
            Write-Host "Note: Created .zip archive instead of .tar.gz (tar not available)" -ForegroundColor Yellow
        }
        
        # Calculate backup size
        $archiveFile = Get-Item (Join-Path $BackupDir "${BackupName}.*") | Select-Object -First 1
        $backupSize = "{0:N2} MB" -f ($archiveFile.Length / 1MB)
        Write-Host "Backup size: $backupSize" -ForegroundColor Green
        
        # Cleanup old backups
        Write-Host "Cleaning up backups older than $RetentionDays days..." -ForegroundColor Yellow
        $cutoffDate = (Get-Date).AddDays(-$RetentionDays)
        Get-ChildItem -Path $BackupDir -Filter "mongodb_backup_*.*" | 
            Where-Object { $_.LastWriteTime -lt $cutoffDate } | 
            Remove-Item -Force
        
        Write-Host "Cleanup completed" -ForegroundColor Green
        
        # List remaining backups
        Write-Host "`nRemaining backups:" -ForegroundColor Yellow
        Get-ChildItem -Path $BackupDir -Filter "mongodb_backup_*.*" | 
            Format-Table Name, Length, LastWriteTime -AutoSize
        
        Write-Host "Backup process completed!" -ForegroundColor Green
    } else {
        Write-Host "Backup failed!" -ForegroundColor Red
        exit 1
    }
} catch {
    Write-Host "Error during backup: $_" -ForegroundColor Red
    exit 1
}
