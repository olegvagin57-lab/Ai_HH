# MongoDB Restore Script for Windows
# This script restores a MongoDB database from a backup

param(
    [Parameter(Mandatory=$true)]
    [string]$BackupFile,
    [string]$BackupDir = "./backups",
    [string]$MongoDBUrl = $env:MONGODB_URL,
    [string]$MongoDBDatabase = $env:MONGODB_DATABASE
)

if (-not $MongoDBUrl) {
    $MongoDBUrl = "mongodb://localhost:27017"
}

if (-not $MongoDBDatabase) {
    $MongoDBDatabase = "hh_analyzer"
}

# Check if backup file exists
if (-not (Test-Path $BackupFile)) {
    Write-Host "Backup file not found: $BackupFile" -ForegroundColor Red
    Write-Host "`nAvailable backups:" -ForegroundColor Yellow
    Get-ChildItem -Path $BackupDir -Filter "mongodb_backup_*.*" | Format-Table Name, LastWriteTime -AutoSize
    exit 1
}

Write-Host "WARNING: This will restore the database and may overwrite existing data!" -ForegroundColor Yellow
$confirm = Read-Host "Are you sure you want to continue? (yes/no)"

if ($confirm -ne "yes") {
    Write-Host "Restore cancelled" -ForegroundColor Yellow
    exit 0
}

# Parse MongoDB URL
if ($MongoDBUrl -match "^mongodb://(.+?)(?::(\d+))?(?:/(.+))?$") {
    $Host = $matches[1]
    $Port = if ($matches[2]) { $matches[2] } else { "27017" }
} else {
    Write-Host "Invalid MONGODB_URL format. Expected: mongodb://host:port" -ForegroundColor Red
    exit 1
}

# Check if mongorestore is available
$mongorestorePath = Get-Command mongorestore -ErrorAction SilentlyContinue
if (-not $mongorestorePath) {
    Write-Host "mongorestore is not installed." -ForegroundColor Red
    Write-Host "Please install MongoDB Database Tools from: https://www.mongodb.com/try/download/database-tools" -ForegroundColor Yellow
    exit 1
}

# Create temporary directory
$TempDir = Join-Path $env:TEMP "mongodb_restore_$(Get-Date -Format 'yyyyMMdd_HHmmss')"
New-Item -ItemType Directory -Path $TempDir | Out-Null

try {
    Write-Host "Extracting backup..." -ForegroundColor Green
    
    # Extract based on file extension
    if ($BackupFile -match "\.tar\.gz$") {
        $tarPath = Get-Command tar -ErrorAction SilentlyContinue
        if ($tarPath) {
            & tar -xzf $BackupFile -C $TempDir
        } else {
            Write-Host "tar is not available. Please extract the archive manually." -ForegroundColor Red
            exit 1
        }
    } elseif ($BackupFile -match "\.zip$") {
        Expand-Archive -Path $BackupFile -DestinationPath $TempDir -Force
    } else {
        Write-Host "Unsupported backup format. Expected .tar.gz or .zip" -ForegroundColor Red
        exit 1
    }
    
    # Find the backup directory
    $BackupPath = Get-ChildItem -Path $TempDir -Directory -Filter "mongodb_backup_*" | Select-Object -First 1
    
    if (-not $BackupPath) {
        Write-Host "Could not find backup directory in archive" -ForegroundColor Red
        exit 1
    }
    
    # Find the database directory
    $DbBackupPath = Get-ChildItem -Path $BackupPath.FullName -Directory -Filter $MongoDBDatabase | Select-Object -First 1
    
    if (-not $DbBackupPath) {
        Write-Host "Could not find database directory in backup" -ForegroundColor Red
        exit 1
    }
    
    Write-Host "Restoring database: $MongoDBDatabase" -ForegroundColor Green
    Write-Host "Host: ${Host}:${Port}" -ForegroundColor Yellow
    
    # Restore database
    & mongorestore --host "${Host}:${Port}" --db $MongoDBDatabase --drop --gzip $DbBackupPath.FullName
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "Restore completed successfully!" -ForegroundColor Green
    } else {
        Write-Host "Restore failed!" -ForegroundColor Red
        exit 1
    }
} finally {
    # Cleanup
    Remove-Item -Recurse -Force $TempDir -ErrorAction SilentlyContinue
}

Write-Host "Database restore completed!" -ForegroundColor Green
