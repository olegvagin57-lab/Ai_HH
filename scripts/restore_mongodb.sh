#!/bin/bash
# MongoDB Restore Script
# This script restores a MongoDB database from a backup

set -e

# Configuration
BACKUP_DIR="${BACKUP_DIR:-./backups}"
MONGODB_URL="${MONGODB_URL:-mongodb://localhost:27017}"
MONGODB_DATABASE="${MONGODB_DATABASE:-hh_analyzer}"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if backup file is provided
if [ -z "$1" ]; then
    echo -e "${RED}Usage: $0 <backup_file.tar.gz>${NC}"
    echo -e "${YELLOW}Available backups:${NC}"
    ls -lh "$BACKUP_DIR"/mongodb_backup_*.tar.gz 2>/dev/null || echo "No backups found"
    exit 1
fi

BACKUP_FILE="$1"

# Check if backup file exists
if [ ! -f "$BACKUP_FILE" ]; then
    echo -e "${RED}Backup file not found: $BACKUP_FILE${NC}"
    exit 1
fi

echo -e "${YELLOW}WARNING: This will restore the database and may overwrite existing data!${NC}"
read -p "Are you sure you want to continue? (yes/no): " confirm

if [ "$confirm" != "yes" ]; then
    echo -e "${YELLOW}Restore cancelled${NC}"
    exit 0
fi

# Extract host and port from MONGODB_URL
if [[ $MONGODB_URL == mongodb://* ]]; then
    HOST_PORT=$(echo $MONGODB_URL | sed 's|mongodb://||' | cut -d'/' -f1)
    HOST=$(echo $HOST_PORT | cut -d':' -f1)
    PORT=$(echo $HOST_PORT | cut -d':' -f2)
    PORT=${PORT:-27017}
else
    echo -e "${RED}Invalid MONGODB_URL format. Expected: mongodb://host:port${NC}"
    exit 1
fi

# Check if mongorestore is available
if ! command -v mongorestore &> /dev/null; then
    echo -e "${RED}mongorestore is not installed. Please install MongoDB database tools.${NC}"
    exit 1
fi

# Create temporary directory for extraction
TEMP_DIR=$(mktemp -d)
trap "rm -rf $TEMP_DIR" EXIT

echo -e "${GREEN}Extracting backup...${NC}"
tar -xzf "$BACKUP_FILE" -C "$TEMP_DIR"

# Find the backup directory
BACKUP_PATH=$(find "$TEMP_DIR" -type d -name "mongodb_backup_*" | head -1)

if [ -z "$BACKUP_PATH" ]; then
    echo -e "${RED}Could not find backup directory in archive${NC}"
    exit 1
fi

# Find the database directory
DB_BACKUP_PATH=$(find "$BACKUP_PATH" -type d -name "$MONGODB_DATABASE" | head -1)

if [ -z "$DB_BACKUP_PATH" ]; then
    echo -e "${RED}Could not find database directory in backup${NC}"
    exit 1
fi

echo -e "${GREEN}Restoring database: $MONGODB_DATABASE${NC}"
echo -e "${YELLOW}Host: $HOST:$PORT${NC}"

# Restore database
if mongorestore \
    --host "$HOST:$PORT" \
    --db "$MONGODB_DATABASE" \
    --drop \
    --gzip \
    "$DB_BACKUP_PATH"; then
    echo -e "${GREEN}Restore completed successfully!${NC}"
else
    echo -e "${RED}Restore failed!${NC}"
    exit 1
fi

# Cleanup
rm -rf "$TEMP_DIR"

echo -e "${GREEN}Database restore completed!${NC}"
