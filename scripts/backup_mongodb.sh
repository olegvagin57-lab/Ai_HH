#!/bin/bash
# MongoDB Backup Script
# This script creates a backup of MongoDB database

set -e

# Configuration
BACKUP_DIR="${BACKUP_DIR:-./backups}"
RETENTION_DAYS="${RETENTION_DAYS:-30}"
MONGODB_URL="${MONGODB_URL:-mongodb://localhost:27017}"
MONGODB_DATABASE="${MONGODB_DATABASE:-hh_analyzer}"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_NAME="mongodb_backup_${MONGODB_DATABASE}_${TIMESTAMP}"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}Starting MongoDB backup...${NC}"

# Create backup directory if it doesn't exist
mkdir -p "$BACKUP_DIR"

# Extract host and port from MONGODB_URL
if [[ $MONGODB_URL == mongodb://* ]]; then
    # Remove mongodb:// prefix
    HOST_PORT=$(echo $MONGODB_URL | sed 's|mongodb://||' | cut -d'/' -f1)
    HOST=$(echo $HOST_PORT | cut -d':' -f1)
    PORT=$(echo $HOST_PORT | cut -d':' -f2)
    PORT=${PORT:-27017}
else
    echo -e "${RED}Invalid MONGODB_URL format. Expected: mongodb://host:port${NC}"
    exit 1
fi

# Check if mongodump is available
if ! command -v mongodump &> /dev/null; then
    echo -e "${RED}mongodump is not installed. Please install MongoDB database tools.${NC}"
    exit 1
fi

# Perform backup
echo -e "${YELLOW}Backing up database: $MONGODB_DATABASE${NC}"
echo -e "${YELLOW}Host: $HOST:$PORT${NC}"

if mongodump \
    --host "$HOST:$PORT" \
    --db "$MONGODB_DATABASE" \
    --out "$BACKUP_DIR/$BACKUP_NAME" \
    --gzip; then
    echo -e "${GREEN}Backup completed successfully!${NC}"
    echo -e "${GREEN}Backup location: $BACKUP_DIR/$BACKUP_NAME${NC}"
else
    echo -e "${RED}Backup failed!${NC}"
    exit 1
fi

# Create archive
echo -e "${YELLOW}Creating archive...${NC}"
cd "$BACKUP_DIR"
tar -czf "${BACKUP_NAME}.tar.gz" "$BACKUP_NAME"
rm -rf "$BACKUP_NAME"
echo -e "${GREEN}Archive created: ${BACKUP_NAME}.tar.gz${NC}"

# Calculate backup size
BACKUP_SIZE=$(du -h "${BACKUP_NAME}.tar.gz" | cut -f1)
echo -e "${GREEN}Backup size: $BACKUP_SIZE${NC}"

# Cleanup old backups
echo -e "${YELLOW}Cleaning up backups older than $RETENTION_DAYS days...${NC}"
find "$BACKUP_DIR" -name "mongodb_backup_*.tar.gz" -type f -mtime +$RETENTION_DAYS -delete
echo -e "${GREEN}Cleanup completed${NC}"

# List remaining backups
echo -e "${YELLOW}Remaining backups:${NC}"
ls -lh "$BACKUP_DIR"/mongodb_backup_*.tar.gz 2>/dev/null || echo "No backups found"

echo -e "${GREEN}Backup process completed!${NC}"
