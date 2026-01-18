#!/bin/bash
# Schedule MongoDB Backup Script
# This script sets up a cron job for automatic MongoDB backups

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BACKUP_SCRIPT="$SCRIPT_DIR/backup_mongodb.sh"
CRON_SCHEDULE="${1:-0 2 * * *}"  # Default: 2 AM daily

echo "Setting up scheduled MongoDB backup..."
echo "Schedule: $CRON_SCHEDULE"
echo "Script: $BACKUP_SCRIPT"

# Make backup script executable
chmod +x "$BACKUP_SCRIPT"

# Create cron job
CRON_JOB="$CRON_SCHEDULE $BACKUP_SCRIPT >> /var/log/mongodb_backup.log 2>&1"

# Check if cron job already exists
if crontab -l 2>/dev/null | grep -q "$BACKUP_SCRIPT"; then
    echo "Cron job already exists. Updating..."
    crontab -l 2>/dev/null | grep -v "$BACKUP_SCRIPT" | crontab -
fi

# Add new cron job
(crontab -l 2>/dev/null; echo "$CRON_JOB") | crontab -

echo "Scheduled backup has been set up successfully!"
echo ""
echo "To view scheduled jobs: crontab -l"
echo "To remove scheduled backup: crontab -e (then delete the line)"
echo "To view backup logs: tail -f /var/log/mongodb_backup.log"
