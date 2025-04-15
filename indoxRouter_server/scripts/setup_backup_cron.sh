#!/bin/bash

# IndoxRouter Server - Set up database backup cron job
# This script sets up a daily cron job to back up all databases

# Make sure the backup script is executable
chmod +x /opt/indoxrouter/scripts/backup_databases.sh

# Create a temporary cron file
cat > /tmp/indoxrouter_backup_cron << EOF
# Run IndoxRouter database backup daily at 2:00 AM
0 2 * * * /opt/indoxrouter/scripts/backup_databases.sh >> /opt/indoxrouter/logs/backup.log 2>&1
EOF

# Install the cron job
crontab -u root /tmp/indoxrouter_backup_cron

# Verify cron job was installed
echo "Cron job installed. Current crontab:"
crontab -l

# Clean up temp file
rm /tmp/indoxrouter_backup_cron

echo "Backup cron job has been set up successfully."
echo "Backups will run daily at 2:00 AM."
echo "Backup logs will be written to /opt/indoxrouter/logs/backup.log" 