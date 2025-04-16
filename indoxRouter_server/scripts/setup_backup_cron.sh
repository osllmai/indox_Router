#!/bin/bash

useradd -m -s /bin/bash indoxbackup || true
usermod -aG docker indoxbackup
cat > /tmp/indoxbackup.cron << EOF
0 2 * * * . /opt/indoxrouter/.env && /opt/indoxrouter/scripts/backup_databases.sh >> /opt/indoxrouter/logs/backup.log 2>&1
EOF
mkdir -p /opt/indoxrouter/backups/{postgres,mongodb,redis}
chown -R indoxbackup:indoxbackup /opt/indoxrouter/backups

su - indoxbackup -c "echo "*:*:*:${POSTGRES_USER}:$POSTGRES_PASSWORD" > ~/.pgpass"
su - indoxbackup -c "chmod 600 ~/.pgpass"

su - indoxbackup -c "echo \"password = $MONGO_APP_PASSWORD\" > ~/.mongorc.js"
su - indoxbackup -c "chmod 600 ~/.mongorc.js"

cat > /tmp/indoxbackup.cron << EOF
0 2 * * * /opt/indoxrouter/scripts/backup_databases.sh >> /opt/indoxrouter/logs/backup.log 2>&1
EOF

crontab -u indoxbackup /tmp/indoxbackup.cron
rm /tmp/indoxbackup.cron

echo "Backup cron configured for user indoxbackup"