# IndoxRouter Deployment Guide

This guide provides comprehensive instructions for deploying the IndoxRouter application in various environments, from development to production.

## Table of Contents

1. [Local Development Setup](#1-local-development-setup)
2. [Configuration Options](#2-configuration-options)
3. [Database Setup](#3-database-setup)
4. [Production Deployment Options](#4-production-deployment-options)
5. [Nginx Configuration](#5-nginx-configuration-reverse-proxy)
6. [Monitoring and Maintenance](#6-monitoring-and-maintenance)
7. [Scaling Strategies](#7-scaling-strategies)
8. [Security Best Practices](#8-security-best-practices)
9. [Troubleshooting](#9-troubleshooting)
10. [Deployment Checklist](#10-deployment-checklist)
11. [Windows Compatibility](#11-windows-compatibility)

## 1. Local Development Setup

### Prerequisites

- Python 3.8 or higher
- PostgreSQL 12+ (recommended for production)
- Redis (optional, for caching)

### Step-by-Step Setup

1. **Clone the repository**:

   ```bash
   git clone https://github.com/yourusername/indoxRouter.git
   cd indoxRouter
   ```

2. **Create a virtual environment**:

   ```bash
   python -m venv venv

   # On Windows
   venv\Scripts\activate

   # On macOS/Linux
   source venv/bin/activate
   ```

3. **Install dependencies**:

   ```bash
   pip install -r indoxRouter/requirements.txt
   ```

4. **Set up environment variables**:

   ```bash
   # Copy the example file
   cp indoxRouter/.env.example indoxRouter/.env

   # Edit the file with your provider API keys
   # On Windows
   notepad indoxRouter/.env

   # On macOS/Linux
   nano indoxRouter/.env
   ```

5. **Initialize the database**:

   ```bash
   python -m indoxRouter.utils.migrations init
   python -m indoxRouter.utils.migrations create "initial_schema"
   python -m indoxRouter.utils.migrations upgrade
   ```

6. **Run the application**:

   ```bash
   uvicorn indoxRouter.main:app --reload
   ```

7. **Test with the dashboard**:
   ```bash
   python indoxRouter/run_dashboard.py
   ```
   Access the dashboard at http://localhost:7860 (login: admin/admin)

## 2. Configuration Options

### Configuration File (config.json)

Create a `config.json` file in the root directory:

```json
{
  "api": {
    "host": "0.0.0.0",
    "port": 8000,
    "debug": false,
    "workers": 4,
    "timeout": 60
  },
  "database": {
    "type": "postgresql",
    "host": "localhost",
    "port": 5432,
    "user": "indoxuser",
    "password": "your_password",
    "database": "indoxrouter"
  },
  "cache": {
    "type": "redis",
    "host": "localhost",
    "port": 6379,
    "password": null,
    "db": 0,
    "ttl": 3600
  },
  "security": {
    "api_key_prefix": "indox",
    "jwt_secret": "your_jwt_secret",
    "jwt_algorithm": "HS256",
    "jwt_expiration": 86400
  },
  "providers": {
    "default_timeout": 30,
    "retry_attempts": 3
  }
}
```

### Environment Variables

Alternatively, configure using environment variables:

```bash
# API configuration
export INDOX_API_HOST=0.0.0.0
export INDOX_API_PORT=8000
export INDOX_API_DEBUG=false
export INDOX_API_WORKERS=4
export INDOX_API_TIMEOUT=60

# Database configuration
export INDOX_DATABASE_TYPE=postgresql
export INDOX_DATABASE_HOST=localhost
export INDOX_DATABASE_PORT=5432
export INDOX_DATABASE_USER=indoxuser
export INDOX_DATABASE_PASSWORD=your_password
export INDOX_DATABASE_DATABASE=indoxrouter

# Cache configuration
export INDOX_CACHE_TYPE=redis
export INDOX_CACHE_HOST=localhost
export INDOX_CACHE_PORT=6379
export INDOX_CACHE_PASSWORD=
export INDOX_CACHE_DB=0
export INDOX_CACHE_TTL=3600

# Security configuration
export INDOX_SECURITY_API_KEY_PREFIX=indox
export INDOX_SECURITY_JWT_SECRET=your_jwt_secret
export INDOX_SECURITY_JWT_ALGORITHM=HS256
export INDOX_SECURITY_JWT_EXPIRATION=86400

# Provider API keys
export OPENAI_API_KEY=sk-...
export ANTHROPIC_API_KEY=sk-...
export MISTRAL_API_KEY=...
export COHERE_API_KEY=...
export GOOGLE_API_KEY=...
export META_API_KEY=...
export AI21_API_KEY=...
```

## 3. Database Setup

### PostgreSQL Setup (Recommended for Production)

1. **Install PostgreSQL**:

   - Windows: Download from https://www.postgresql.org/download/windows/
   - macOS: `brew install postgresql`
   - Ubuntu: `sudo apt install postgresql postgresql-contrib`

2. **Create a database and user**:

   ```bash
   sudo -u postgres psql
   ```

   ```sql
   CREATE USER indoxuser WITH PASSWORD 'your_password';
   CREATE DATABASE indoxrouter;
   GRANT ALL PRIVILEGES ON DATABASE indoxrouter TO indoxuser;
   \q
   ```

3. **Update configuration**:
   Edit your config.json or environment variables to match these settings.

### SQLite Setup (Development Only)

For development, you can use SQLite by setting:

```json
"database": {
  "type": "sqlite",
  "database": "indoxrouter.db"
}
```

## 4. Production Deployment Options

### Option 1: Standalone Server with Gunicorn

1. **Install Gunicorn**:

   ```bash
   pip install gunicorn
   ```

2. **Create a systemd service** (Linux):

   ```bash
   sudo nano /etc/systemd/system/indoxrouter.service
   ```

   Add the following content:

   ```
   [Unit]
   Description=IndoxRouter API
   After=network.target

   [Service]
   User=yourusername
   WorkingDirectory=/path/to/indoxRouter
   ExecStart=/path/to/venv/bin/gunicorn indoxRouter.main:app -w 4 -k uvicorn.workers.UvicornWorker -b 0.0.0.0:8000
   Restart=on-failure

   [Install]
   WantedBy=multi-user.target
   ```

3. **Start the service**:

   ```bash
   sudo systemctl enable indoxrouter
   sudo systemctl start indoxrouter
   ```

4. **Check status**:
   ```bash
   sudo systemctl status indoxrouter
   ```

### Option 2: Docker Deployment

1. **Build the Docker image**:

   ```bash
   docker build -t indoxrouter -f indoxRouter/Dockerfile .
   ```

2. **Run with Docker**:

   ```bash
   docker run -d \
     --name indoxrouter \
     -p 8000:8000 \
     -v $(pwd)/config.json:/app/config.json \
     -e OPENAI_API_KEY=sk-... \
     -e ANTHROPIC_API_KEY=sk-... \
     indoxrouter
   ```

3. **Run with Docker Compose** (recommended):
   ```bash
   docker-compose -f indoxRouter/docker-compose.yml up -d
   ```

### Option 3: Cloud Deployment

#### AWS Elastic Beanstalk

1. **Install EB CLI**:

   ```bash
   pip install awsebcli
   ```

2. **Initialize EB application**:

   ```bash
   eb init -p python-3.8 indoxrouter
   ```

3. **Create an environment**:

   ```bash
   eb create indoxrouter-prod
   ```

4. **Deploy**:
   ```bash
   eb deploy
   ```

#### Heroku

1. **Install Heroku CLI**:

   ```bash
   # Follow instructions at https://devcenter.heroku.com/articles/heroku-cli
   ```

2. **Login and create app**:

   ```bash
   heroku login
   heroku create indoxrouter
   ```

3. **Add PostgreSQL**:

   ```bash
   heroku addons:create heroku-postgresql:hobby-dev
   ```

4. **Set environment variables**:

   ```bash
   heroku config:set OPENAI_API_KEY=sk-...
   heroku config:set ANTHROPIC_API_KEY=sk-...
   # Set other environment variables
   ```

5. **Deploy**:
   ```bash
   git push heroku main
   ```

## 5. Nginx Configuration (Reverse Proxy)

For production, use Nginx as a reverse proxy:

1. **Install Nginx**:

   ```bash
   # Ubuntu
   sudo apt install nginx

   # CentOS
   sudo yum install nginx
   ```

2. **Create a configuration file**:

   ```bash
   sudo nano /etc/nginx/sites-available/indoxrouter
   ```

   Add the following content:

   ```nginx
   server {
       listen 80;
       server_name your-domain.com;

       location / {
           proxy_pass http://localhost:8000;
           proxy_set_header Host $host;
           proxy_set_header X-Real-IP $remote_addr;
           proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
           proxy_set_header X-Forwarded-Proto $scheme;
       }
   }
   ```

3. **Enable the site**:

   ```bash
   sudo ln -s /etc/nginx/sites-available/indoxrouter /etc/nginx/sites-enabled/
   sudo nginx -t
   sudo systemctl restart nginx
   ```

4. **Set up SSL with Certbot**:
   ```bash
   sudo apt install certbot python3-certbot-nginx
   sudo certbot --nginx -d your-domain.com
   ```

## 6. Monitoring and Maintenance

### Logging

Configure logging in your config.json:

```json
"logging": {
  "level": "INFO",
  "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
  "file": "/var/log/indoxrouter/app.log"
}
```

### Monitoring Tools

1. **Prometheus and Grafana**:

   - Add the `prometheus-client` package to requirements.txt
   - Set up a Prometheus endpoint in your application
   - Configure Grafana dashboards

2. **Sentry for Error Tracking**:
   - Add `sentry-sdk[fastapi]` to requirements.txt
   - Initialize Sentry in your application

### Backup Strategy

1. **Database Backups**:

   ```bash
   # PostgreSQL backup
   pg_dump -U indoxuser indoxrouter > backup_$(date +%Y%m%d).sql

   # Automate with cron
   echo "0 2 * * * pg_dump -U indoxuser indoxrouter > /path/to/backups/backup_\$(date +\%Y\%m\%d).sql" | crontab -
   ```

2. **Configuration Backups**:
   Regularly back up your config.json and .env files.

## 7. Scaling Strategies

### Horizontal Scaling

1. **Load Balancer Setup**:

   - Use Nginx as a load balancer
   - Deploy multiple instances of the application
   - Configure sticky sessions if needed

2. **Database Scaling**:
   - Set up PostgreSQL replication
   - Consider read replicas for heavy read workloads

### Vertical Scaling

1. **Increase resources** on your server (CPU, RAM)
2. **Optimize database queries** and add indexes
3. **Implement caching** with Redis

## 8. Security Best Practices

1. **API Key Management**:

   - Rotate API keys regularly
   - Use the dashboard to manage and monitor API keys

2. **Rate Limiting**:

   - Configure rate limits in your config.json:

   ```json
   "rate_limiting": {
     "enabled": true,
     "requests_per_minute": 60,
     "requests_per_hour": 1000
   }
   ```

3. **Firewall Configuration**:

   ```bash
   # Allow only necessary ports
   sudo ufw allow 22
   sudo ufw allow 80
   sudo ufw allow 443
   sudo ufw enable
   ```

4. **Regular Updates**:

   ```bash
   # Update dependencies
   pip install -U -r indoxRouter/requirements.txt

   # Update system packages
   sudo apt update && sudo apt upgrade
   ```

## 9. Troubleshooting

### Common Issues and Solutions

1. **Database Connection Issues**:

   - Check database credentials
   - Ensure PostgreSQL is running: `sudo systemctl status postgresql`
   - Verify network connectivity: `telnet localhost 5432`

2. **API Provider Issues**:

   - Verify API keys are valid
   - Check provider status pages
   - Review rate limits

3. **Performance Problems**:
   - Enable caching
   - Optimize database queries
   - Scale resources

### Debugging Tools

1. **Application Logs**:

   ```bash
   # View logs
   tail -f /var/log/indoxrouter/app.log

   # For Docker
   docker logs -f indoxrouter
   ```

2. **Database Debugging**:

   ```bash
   # Connect to PostgreSQL
   psql -U indoxuser -d indoxrouter

   # Check connections
   SELECT * FROM pg_stat_activity;
   ```

3. **Network Debugging**:

   ```bash
   # Check if port is open
   netstat -tuln | grep 8000

   # Test API endpoint
   curl -v http://localhost:8000/api/v1/models
   ```

## 10. Deployment Checklist

Before going live, ensure you've completed these steps:

- [ ] Database migrations are applied
- [ ] Environment variables or config.json is properly set
- [ ] API keys for all providers are valid
- [ ] Security measures are in place (HTTPS, firewall)
- [ ] Monitoring and logging are configured
- [ ] Backup strategy is implemented
- [ ] Load testing has been performed
- [ ] Documentation is up-to-date

## Quick Reference Commands

### Development

```bash
# Start development server
uvicorn indoxRouter.main:app --reload

# Run dashboard
python indoxRouter/run_dashboard.py

# Run tests
pytest
```

### Database Management

```bash
# Initialize migrations
python -m indoxRouter.utils.migrations init

# Create migration
python -m indoxRouter.utils.migrations create "migration_name"

# Apply migrations
python -m indoxRouter.utils.migrations upgrade

# Rollback migration
python -m indoxRouter.utils.migrations downgrade
```

### Docker

```bash
# Build image
docker build -t indoxrouter -f indoxRouter/Dockerfile .

# Run with Docker Compose
docker-compose -f indoxRouter/docker-compose.yml up -d

# View logs
docker-compose -f indoxRouter/docker-compose.yml logs -f
```

### Production

```bash
# Start with Gunicorn
gunicorn indoxRouter.main:app -w 4 -k uvicorn.workers.UvicornWorker -b 0.0.0.0:8000

# Manage systemd service
sudo systemctl start|stop|restart|status indoxrouter
```

## 11. Windows Compatibility

IndoxRouter can be run on Windows with a few considerations:

### Installation on Windows

When installing dependencies on Windows, you may encounter issues with packages like `uvloop` which are not compatible with Windows. The `requirements.txt` file has been modified to comment out these dependencies.

### Running on Windows

1. **Install dependencies**:

   ```bash
   pip install -r indoxRouter/requirements.txt
   ```

2. **Run the application**:

   ```bash
   # The application will automatically detect Windows and use appropriate settings
   uvicorn indoxRouter.main:app --reload
   ```

3. **Run the dashboard**:

   ```bash
   python indoxRouter/run_dashboard.py
   ```

### Performance Considerations

On Windows, the application will run without `uvloop`, which may result in slightly lower performance compared to Unix-based systems. For production deployments, consider using:

- Windows Subsystem for Linux (WSL2)
- Docker for Windows
- A Linux-based server

### Database Setup on Windows

For PostgreSQL on Windows:

1. Download and install PostgreSQL from the [official website](https://www.postgresql.org/download/windows/)
2. During installation, set a password for the postgres user
3. Use pgAdmin (included with the installation) to create a new database and user

For SQLite (development only):

```json
"database": {
  "type": "sqlite",
  "database": "indoxrouter.db"
}
```
