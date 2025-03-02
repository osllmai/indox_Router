# IndoxRouter Deployment Guide

This guide provides detailed instructions for deploying the IndoxRouter application in both local and Docker environments.

## Table of Contents

- [Prerequisites](#prerequisites)
- [Local Deployment](#local-deployment)
- [Docker Deployment](#docker-deployment)
- [Production Deployment](#production-deployment)
- [Troubleshooting](#troubleshooting)

## Prerequisites

Before deploying IndoxRouter, ensure you have the following:

- Python 3.10 or higher
- PostgreSQL 12 or higher
- Redis (optional, for caching)
- API keys for the LLM providers you want to use

## Local Deployment

### 1. Clone the Repository

```bash
git clone https://github.com/yourusername/indoxRouter.git
cd indoxRouter
```

### 2. Create and Activate a Virtual Environment

```bash
# On Windows
python -m venv venv
venv\Scripts\activate

# On macOS/Linux
python -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure the Application

Create configuration files from the examples:

```bash
cp .env.example .env
cp indoxRouter/config.json.example indoxRouter/config.json
```

Edit the `.env` file to add your LLM provider API keys:

```
# Provider API Keys
OPENAI_API_KEY=your_openai_api_key
ANTHROPIC_API_KEY=your_anthropic_api_key
MISTRAL_API_KEY=your_mistral_api_key
# Add other provider keys as needed
```

Edit the `indoxRouter/config.json` file to configure your database connection:

```json
{
  "database": {
    "type": "postgres",
    "host": "localhost",
    "port": 5432,
    "user": "indoxuser",
    "password": "indoxpassword",
    "database": "indoxrouter"
  }
}
```

### 5. Set Up the Database

Create a PostgreSQL database and user:

```sql
CREATE DATABASE indoxrouter;
CREATE USER indoxuser WITH PASSWORD 'indoxpassword';
GRANT ALL PRIVILEGES ON DATABASE indoxrouter TO indoxuser;
```

Initialize the database:

```bash
python -m indoxRouter.init_db
```

For custom admin credentials:

```bash
python -m indoxRouter.init_db --admin-email admin@yourdomain.com --admin-password secure_password
```

### 6. Run the Application

Run both the API and dashboard:

```bash
python run.py
```

To run only the API:

```bash
python run.py --api-only
```

To run only the dashboard:

```bash
python run.py --dashboard-only
```

### 7. Access the Application

- API: http://localhost:8000
- API Documentation: http://localhost:8000/docs
- Dashboard: http://localhost:7860

## Docker Deployment

Docker deployment is recommended for production environments as it simplifies the setup process and ensures consistency across different environments.

### 1. Clone the Repository

```bash
git clone https://github.com/yourusername/indoxRouter.git
cd indoxRouter
```

### 2. Configure the Application

Create a `.env` file from the example:

```bash
cp .env.example .env
```

Edit the `.env` file to add your LLM provider API keys:

```
# Provider API Keys
OPENAI_API_KEY=your_openai_api_key
ANTHROPIC_API_KEY=your_anthropic_api_key
MISTRAL_API_KEY=your_mistral_api_key
# Add other provider keys as needed

# JWT Configuration
JWT_SECRET=your_secure_jwt_secret_key
```

### 3. Build and Start the Docker Containers

```bash
docker-compose up -d
```

This command will:

- Build the IndoxRouter application image
- Start the PostgreSQL database
- Start the Redis cache
- Start the pgAdmin interface (for database management)
- Initialize the database and run migrations
- Start the API and dashboard

### 4. Access the Application

- API: http://localhost:8000
- API Documentation: http://localhost:8000/docs
- Dashboard: http://localhost:7860
- pgAdmin: http://localhost:5050 (login with admin@example.com / admin)

### 5. View Logs

```bash
# View all logs
docker-compose logs

# View logs for a specific service
docker-compose logs app

# Follow logs in real-time
docker-compose logs -f
```

### 6. Stop the Application

```bash
docker-compose down
```

To remove all data (including database volumes):

```bash
docker-compose down -v
```

## Production Deployment

For production environments, additional steps are recommended to ensure security, reliability, and performance.

### 1. Security Considerations

- Use a strong, unique JWT secret key
- Set up SSL/TLS for encrypted connections
- Configure proper authentication and authorization
- Implement rate limiting to prevent abuse
- Use a firewall to restrict access to your servers

### 2. Reverse Proxy Setup

It's recommended to use a reverse proxy like Nginx or Traefik in front of IndoxRouter for SSL termination, load balancing, and additional security.

#### Example Nginx Configuration

```nginx
server {
    listen 80;
    server_name indoxrouter.yourdomain.com;
    return 301 https://$host$request_uri;
}

server {
    listen 443 ssl;
    server_name indoxrouter.yourdomain.com;

    ssl_certificate /path/to/cert.pem;
    ssl_certificate_key /path/to/key.pem;

    # API
    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # Dashboard
    location /dashboard/ {
        proxy_pass http://localhost:7860/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }
}
```

### 3. Database Backups

Set up regular database backups to prevent data loss:

```bash
# Create a backup
docker-compose exec postgres pg_dump -U indoxuser indoxrouter > backup.sql

# Restore from a backup
cat backup.sql | docker-compose exec -T postgres psql -U indoxuser indoxrouter
```

### 4. Monitoring and Logging

For production environments, consider setting up:

- Prometheus for metrics collection
- Grafana for visualization
- ELK stack (Elasticsearch, Logstash, Kibana) for log management
- Sentry for error tracking

### 5. Scaling

For high-traffic deployments, consider:

- Increasing the number of API workers
- Setting up a load balancer
- Using a managed PostgreSQL service
- Implementing caching with Redis

## Troubleshooting

### Database Connection Issues

If you encounter database connection issues:

1. Verify your database credentials in `config.json`
2. Ensure PostgreSQL is running and accessible
3. Check if the database and user exist with correct permissions

```bash
# Test database connection
python -m indoxRouter.test_db_connection
```

### API Startup Issues

If the API fails to start:

1. Check the logs for error messages:
   ```bash
   cat logs/api.log
   ```
2. Verify that all required environment variables are set
3. Ensure all dependencies are installed correctly

### Dashboard Startup Issues

If the dashboard fails to start:

1. Check the logs for error messages:
   ```bash
   cat logs/dashboard.log
   ```
2. Verify that Gradio is installed correctly
3. Ensure the API is running and accessible

### Docker Issues

If you encounter issues with Docker deployment:

1. Check the container logs:
   ```bash
   docker-compose logs app
   ```
2. Verify that all services are running:
   ```bash
   docker-compose ps
   ```
3. Ensure Docker and Docker Compose are up to date

For additional help, please open an issue on the GitHub repository.
