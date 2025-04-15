#!/bin/bash

# IndoxRouter Server - Database Backup Script
# This script creates backups of PostgreSQL, MongoDB, and Redis databases

# Configuration
BACKUP_DIR="/opt/indoxrouter/backups"
DATE=$(date +%Y-%m-%d_%H-%M-%S)
POSTGRES_USER="indoxrouter_admin"
POSTGRES_PASSWORD="Ejpp4gjm2i4Vgnf+abcdoeWrTlSxeSwo"
MONGO_USER="indoxrouter_admin"
MONGO_PASSWORD="/vLiS2JYfb8wm52lsow+hURaI6aa+k+I"
REDIS_PASSWORD="Ejpp4gjm2i4Vgnf+abcdoeWrTlSxeSwo"
RETENTION_DAYS=14

# Create backup directory if it doesn't exist
mkdir -p $BACKUP_DIR
mkdir -p $BACKUP_DIR/postgres
mkdir -p $BACKUP_DIR/mongodb
mkdir -p $BACKUP_DIR/redis

echo "Starting IndoxRouter database backups at $(date)"

# Backup PostgreSQL
echo "Backing up PostgreSQL database..."
docker exec indoxrouter-postgres pg_dump -U $POSTGRES_USER -d indoxrouter | gzip > $BACKUP_DIR/postgres/indoxrouter_postgres_$DATE.sql.gz
if [ $? -eq 0 ]; then
    echo "PostgreSQL backup completed successfully"
else
    echo "PostgreSQL backup failed"
fi

# Backup MongoDB
echo "Backing up MongoDB database..."
docker exec indoxrouter-mongodb mongodump --username $MONGO_USER --password $MONGO_PASSWORD --db indoxrouter --authenticationDatabase admin --archive | gzip > $BACKUP_DIR/mongodb/indoxrouter_mongodb_$DATE.archive.gz
if [ $? -eq 0 ]; then
    echo "MongoDB backup completed successfully"
else
    echo "MongoDB backup failed"
fi

# Backup Redis
echo "Backing up Redis database..."
docker exec indoxrouter-redis redis-cli -a $REDIS_PASSWORD --rdb /data/redis_backup.rdb
docker cp indoxrouter-redis:/data/redis_backup.rdb $BACKUP_DIR/redis/indoxrouter_redis_$DATE.rdb
if [ $? -eq 0 ]; then
    echo "Redis backup completed successfully"
else
    echo "Redis backup failed"
fi

# Clean up old backups
echo "Cleaning up backups older than $RETENTION_DAYS days..."
find $BACKUP_DIR/postgres -name "indoxrouter_postgres_*.sql.gz" -type f -mtime +$RETENTION_DAYS -delete
find $BACKUP_DIR/mongodb -name "indoxrouter_mongodb_*.archive.gz" -type f -mtime +$RETENTION_DAYS -delete
find $BACKUP_DIR/redis -name "indoxrouter_redis_*.rdb" -type f -mtime +$RETENTION_DAYS -delete

echo "Backup process completed at $(date)"
echo "Backups are stored in $BACKUP_DIR"
echo "========================================" 