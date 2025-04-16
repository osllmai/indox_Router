#!/bin/bash
set -euo pipefail

BACKUP_DIR="/opt/indoxrouter/backups"
DATE=$(date +%Y-%m-%d_%H-%M-%S)
POSTGRES_USER="${POSTGRES_USER}"
POSTGRES_PASSWORD="${POSTGRES_PASSWORD}"
MONGO_USER="${MONGO_APP_USER}"
MONGO_PASSWORD="${MONGO_APP_PASSWORD}"
REDIS_PASSWORD="${REDIS_PASSWORD}"
RETENTION_DAYS=14
LOG_FILE="/opt/indoxrouter/logs/backup.log"

handle_error() {
  local exit_code=$1
  local error_message=$2
  echo "ERROR: $error_message (exit code: $exit_code)" | tee -a "$LOG_FILE"
  exit "$exit_code"
}

mkdir -p "$BACKUP_DIR"/{postgres,mongodb,redis}
mkdir -p "$(dirname "$LOG_FILE")"

echo "Starting backups at $(date)" | tee -a "$LOG_FILE"

# PostgreSQL Backup
docker exec indoxrouter-postgres pg_dump -U ${POSTGRES_USER} -d indoxrouter | gzip > "$BACKUP_DIR/postgres/indoxrouter_postgres_$DATE.sql.gz" || handle_error 1 "PostgreSQL backup failed"

# MongoDB Backup
docker exec indoxrouter-mongodb mongodump -u appuser -p "$MONGO_APP_PASSWORD" \
  --authenticationDatabase admin --db indoxrouter --archive | gzip > "$BACKUP_DIR/mongodb/indoxrouter_mongodb_$DATE.archive.gz" || handle_error 2 "MongoDB backup failed"

# Redis Backup
docker exec indoxrouter-redis redis-cli --no-auth-warning -a "$REDIS_PASSWORD" SAVE || handle_error 3 "Redis SAVE failed"
docker cp indoxrouter-redis:/data/dump.rdb "$BACKUP_DIR/redis/indoxrouter_redis_$DATE.rdb" || handle_error 4 "Redis copy failed"

find "$BACKUP_DIR/postgres" -name "*.sql.gz" -mtime +$RETENTION_DAYS -delete
find "$BACKUP_DIR/mongodb" -name "*.archive.gz" -mtime +$RETENTION_DAYS -delete
find "$BACKUP_DIR/redis" -name "*.rdb" -mtime +$RETENTION_DAYS -delete

echo "Backups completed at $(date)" | tee -a "$LOG_FILE"
exit 0