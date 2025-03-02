# IndoxRouter Deployment Guide

This guide provides instructions for deploying IndoxRouter in a production environment.

## Prerequisites

- Python 3.8 or higher
- PostgreSQL 12 or higher (recommended for production)
- Docker (optional, for containerized deployment)

## Installation

1. Clone the repository:

```bash
git clone https://github.com/yourusername/indoxRouter.git
cd indoxRouter
```

2. Install dependencies:

```bash
pip install -r requirements.txt
```

## Database Setup

IndoxRouter supports multiple database backends, but PostgreSQL is recommended for production deployments.

### PostgreSQL Setup

1. Install PostgreSQL:

```bash
# Ubuntu/Debian
sudo apt update
sudo apt install postgresql postgresql-contrib

# CentOS/RHEL
sudo dnf install postgresql-server postgresql-contrib
sudo postgresql-setup --initdb
sudo systemctl start postgresql
```

2. Create a database and user:

```bash
sudo -u postgres psql

postgres=# CREATE DATABASE indoxrouter;
postgres=# CREATE USER indoxuser WITH ENCRYPTED PASSWORD 'your_secure_password';
postgres=# GRANT ALL PRIVILEGES ON DATABASE indoxrouter TO indoxuser;
postgres=# \q
```

3. Configure IndoxRouter to use PostgreSQL:

Create a configuration file (e.g., `config.json`):

```json
{
  "database": {
    "type": "postgres",
    "host": "localhost",
    "port": 5432,
    "user": "indoxuser",
    "password": "your_secure_password",
    "database": "indoxrouter",
    "pool_size": 10,
    "max_overflow": 20,
    "pool_recycle": 3600,
    "pool_pre_ping": true
  }
}
```

Alternatively, you can use environment variables:

```bash
export INDOX_DATABASE_TYPE=postgres
export INDOX_DATABASE_HOST=localhost
export INDOX_DATABASE_PORT=5432
export INDOX_DATABASE_USER=indoxuser
export INDOX_DATABASE_PASSWORD=your_secure_password
export INDOX_DATABASE_DATABASE=indoxrouter
```

### Database Migrations

Initialize and run database migrations:

```bash
# Initialize migrations
python -m indoxRouter.utils.migrations init

# Create initial migration
python -m indoxRouter.utils.migrations create "initial_schema"

# Apply migrations
python -m indoxRouter.utils.migrations upgrade
```

## Configuration

IndoxRouter can be configured using a JSON configuration file or environment variables.

### Configuration File

Create a `config.json` file:

```json
{
  "api": {
    "host": "0.0.0.0",
    "port": 8000,
    "workers": 4,
    "timeout": 60,
    "cors_origins": ["https://yourdomain.com"]
  },
  "auth": {
    "token_expiry": 86400,
    "refresh_token_expiry": 2592000,
    "admin_email": "admin@yourdomain.com"
  },
  "providers": {
    "default_timeout": 30,
    "retry_attempts": 3
  },
  "database": {
    "type": "postgres",
    "host": "localhost",
    "port": 5432,
    "user": "indoxuser",
    "password": "your_secure_password",
    "database": "indoxrouter"
  },
  "logging": {
    "level": "INFO",
    "file": "/var/log/indoxrouter/app.log",
    "rotation": "1 day",
    "retention": "30 days"
  },
  "cache": {
    "type": "redis",
    "url": "redis://localhost:6379/0",
    "ttl": 300
  }
}
```

### Environment Variables

You can also configure IndoxRouter using environment variables:

```bash
# API configuration
export INDOX_API_HOST=0.0.0.0
export INDOX_API_PORT=8000
export INDOX_API_WORKERS=4
export INDOX_API_TIMEOUT=60
export INDOX_API_CORS_ORIGINS=https://yourdomain.com

# Database configuration
export INDOX_DATABASE_TYPE=postgres
export INDOX_DATABASE_HOST=localhost
export INDOX_DATABASE_PORT=5432
export INDOX_DATABASE_USER=indoxuser
export INDOX_DATABASE_PASSWORD=your_secure_password
export INDOX_DATABASE_DATABASE=indoxrouter

# Provider API keys
export OPENAI_API_KEY=sk-...
export ANTHROPIC_API_KEY=sk-...
export MISTRAL_API_KEY=...
export COHERE_API_KEY=...
export GOOGLE_API_KEY=...
```

## Running in Production

### Using Gunicorn

For production deployments, we recommend using Gunicorn:

```bash
pip install gunicorn
gunicorn -w 4 -k uvicorn.workers.UvicornWorker indoxRouter.main:app --bind 0.0.0.0:8000
```

### Using Docker

1. Build the Docker image:

```bash
docker build -t indoxrouter .
```

2. Run the container:

```bash
docker run -d \
  --name indoxrouter \
  -p 8000:8000 \
  -v /path/to/config.json:/app/config.json \
  -e OPENAI_API_KEY=sk-... \
  -e ANTHROPIC_API_KEY=sk-... \
  -e MISTRAL_API_KEY=... \
  -e COHERE_API_KEY=... \
  -e GOOGLE_API_KEY=... \
  indoxrouter
```

### Using Docker Compose

Create a `docker-compose.yml` file:

```yaml
version: "3"

services:
  indoxrouter:
    build: .
    ports:
      - "8000:8000"
    volumes:
      - ./config.json:/app/config.json
    environment:
      - OPENAI_API_KEY=sk-...
      - ANTHROPIC_API_KEY=sk-...
      - MISTRAL_API_KEY=...
      - COHERE_API_KEY=...
      - GOOGLE_API_KEY=...
    depends_on:
      - postgres
      - redis

  postgres:
    image: postgres:14
    environment:
      - POSTGRES_USER=indoxuser
      - POSTGRES_PASSWORD=your_secure_password
      - POSTGRES_DB=indoxrouter
    volumes:
      - postgres_data:/var/lib/postgresql/data

  redis:
    image: redis:7
    volumes:
      - redis_data:/data

volumes:
  postgres_data:
  redis_data:
```

Run with Docker Compose:

```bash
docker-compose up -d
```

## Nginx Configuration

For production deployments, we recommend using Nginx as a reverse proxy:

```nginx
server {
    listen 80;
    server_name api.yourdomain.com;

    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

## SSL Configuration

For secure deployments, configure SSL with Let's Encrypt:

```bash
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d api.yourdomain.com
```

## Monitoring

For production monitoring, consider using:

1. **Prometheus** for metrics collection
2. **Grafana** for visualization
3. **Sentry** for error tracking

## Backup Strategy

### Database Backups

Set up regular PostgreSQL backups:

```bash
# Create a backup script
cat > /usr/local/bin/backup-indoxrouter.sh << 'EOF'
#!/bin/bash
BACKUP_DIR="/var/backups/indoxrouter"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
mkdir -p $BACKUP_DIR
pg_dump -U indoxuser indoxrouter | gzip > "$BACKUP_DIR/indoxrouter_$TIMESTAMP.sql.gz"
find $BACKUP_DIR -type f -name "indoxrouter_*.sql.gz" -mtime +7 -delete
EOF

# Make it executable
chmod +x /usr/local/bin/backup-indoxrouter.sh

# Add to crontab
(crontab -l 2>/dev/null; echo "0 2 * * * /usr/local/bin/backup-indoxrouter.sh") | crontab -
```

## Scaling

For high-traffic deployments, consider:

1. **Horizontal scaling** with multiple IndoxRouter instances behind a load balancer
2. **Database connection pooling** with PgBouncer
3. **Caching** with Redis for frequently accessed data

## Troubleshooting

### Database Connection Issues

If you encounter database connection issues:

1. Check PostgreSQL is running: `sudo systemctl status postgresql`
2. Verify connection settings in your configuration
3. Ensure the database user has proper permissions
4. Check PostgreSQL logs: `sudo tail -f /var/log/postgresql/postgresql-14-main.log`

### Migration Issues

If you encounter migration issues:

1. Check the current migration state: `python -m indoxRouter.utils.migrations current`
2. View migration history: `python -m indoxRouter.utils.migrations history`
3. For serious issues, you may need to manually fix the database schema

## Security Considerations

1. **API Keys**: Store provider API keys securely using environment variables or a secrets manager
2. **Database Credentials**: Use strong passwords and limit database user permissions
3. **Network Security**: Use a firewall to restrict access to your database and Redis instances
4. **Regular Updates**: Keep all dependencies updated to patch security vulnerabilities
