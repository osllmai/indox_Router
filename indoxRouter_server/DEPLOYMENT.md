# IndoxRouter Server Deployment Guide

This guide provides instructions for deploying IndoxRouter Server in different environments.

## Overview

IndoxRouter Server can run in two deployment modes:

- **Development Mode**: Uses development.env, suitable for development and testing
- **Production Mode**: Uses production.env, optimized for production deployment

## System Requirements

- **OS**: Ubuntu 20.04 LTS or newer
- **RAM**: 4GB minimum (8GB recommended)
- **CPU**: 2 cores minimum
- **Storage**: 20GB minimum
- **Network**: Public IP address with open ports 80 and 443
- **Python**: 3.9 or higher (3.9, 3.10, 3.11, 3.12 supported)

## Environment Configuration

IndoxRouter uses a simplified environment configuration approach:

- **production.env**: Settings for production deployment
- **development.env**: Settings for development with Docker

To use either configuration, simply copy the appropriate file to `.env`:

```bash
# For development mode
cp development.env .env

# For production mode
cp production.env .env
```

## Local Development Environment

For local development and testing, follow these steps:

### 1. Set Up Python Environment

```bash
# Create and activate a virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements-dev.txt
```

### 2. Set Up Local Databases

```bash
# Start PostgreSQL and MongoDB containers
./run_local_db.sh
```

### 3. Configure Environment

```bash
# Set up the development environment
cp development.env .env
```

### 4. Run the Application

```bash
# Start the local server with auto-reload
uvicorn indoxrouter_server.main:app --reload --port 8000
```

### 5. Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=indoxrouter_server
```

## Integrated Production Deployment (Recommended)

This approach deploys the application, PostgreSQL, MongoDB, and Redis as interconnected Docker containers on a single server.

### 1. Connect to Your Production Server

```bash
ssh root@91.107.253.133
```

### 2. Clone the Repository

```bash
mkdir -p /opt/indoxrouter
cd /opt/indoxrouter
git clone https://github.com/your-username/indoxrouter.git .
cd indoxrouter_server
```

### 3. Configure Production Environment

```bash
# Set up the production environment
cp production.env .env

# Edit .env to update API keys and security settings
nano .env
```

### 4. Run the Integrated Deployment Script

This script automates the entire deployment process:

```bash
chmod +x scripts/deploy_integrated.sh
./scripts/deploy_integrated.sh
```

The script will:

- Install necessary dependencies
- Configure Docker
- Start all services with Docker Compose
- Configure basic security settings

### 5. Set Up a Domain and SSL (Optional but Recommended)

If you have a domain name pointing to your server, run:

```bash
chmod +x scripts/setup_nginx.sh
./scripts/setup_nginx.sh yourdomain.com
```

This will set up Nginx as a reverse proxy and configure SSL with Let's Encrypt.

### 6. Verify the Deployment

Access your API at:

- With domain: https://yourdomain.com
- Without domain: http://91.107.253.133:8000

## Manual Production Deployment

For manual deployment or customized setups, follow these steps:

### 1. Prepare the Server

Connect to your production server and install dependencies:

```bash
ssh root@91.107.253.133
apt-get update && apt-get upgrade -y
apt-get install -y docker.io docker-compose git curl
```

### 2. Set Up the Application

```bash
mkdir -p /opt/indoxrouter
cd /opt/indoxrouter
git clone https://github.com/your-username/indoxrouter.git .
cd indoxrouter_server
```

### 3. Configure Environment Variables

```bash
cp production.env .env
```

Edit the `.env` file and set secure values:

```bash
# Generate a secure key
SECRET_KEY=$(openssl rand -hex 32)
sed -i "s/change_this_to_a_secure_secret_in_production/$SECRET_KEY/" .env
```

### 4. Start the Services

```bash
docker-compose up -d
```

## Managing Your Deployment

### Viewing Logs

```bash
# View all container logs
docker-compose logs

# Follow logs in real-time
docker-compose logs -f

# View logs for a specific service
docker-compose logs -f indoxrouter-server
```

### Updating the Application

```bash
# Pull latest changes
cd /opt/indoxrouter/indoxrouter_server
git pull

# Rebuild and restart containers
docker-compose down
docker-compose build
docker-compose up -d
```

### Database Backups

For integrated deployments, you can back up your data directly from the Docker volumes:

```bash
# PostgreSQL backup
docker exec indoxrouter-postgres pg_dump -U postgres indoxrouter > /opt/indoxrouter/backups/postgres_backup_$(date +%Y%m%d).sql

# MongoDB backup
docker exec indoxrouter-mongodb mongodump --db indoxrouter --out /dump
docker cp indoxrouter-mongodb:/dump /opt/indoxrouter/backups/mongodb_backup_$(date +%Y%m%d)
```

For detailed backup and restore procedures, refer to the `DATABASE_SETUP.md` document.

## Production vs Local Settings

The following settings differ between production and local environments:

| Setting                       | Local Testing | Production                            |
| ----------------------------- | ------------- | ------------------------------------- |
| `INDOXROUTER_PRODUCTION_MODE` | `false`       | `true`                                |
| `INDOXROUTER_LOCAL_MODE`      | `true`        | `false` (or `true` for integrated DB) |
| `POSTGRES_HOST`               | `localhost`   | Database container name or IP         |
| `MONGO_HOST`                  | `localhost`   | Database container name or IP         |
| `REDIS_HOST`                  | `localhost`   | Database container name or IP         |
| `SECRET_KEY`                  | Can be simple | Must be secure, generated value       |
| `LOG_LEVEL`                   | `DEBUG`       | `INFO` or `WARNING`                   |
| `CORS_ORIGINS`                | `*`           | Specific domains only                 |

## Dependency Management

The project uses different requirement files for different environments:

- **requirements.txt**: Core dependencies needed for production
- **requirements-dev.txt**: Additional tools for development and testing

For local development, install with:

```bash
pip install -r requirements-dev.txt
```

For production deployments, the Docker setup uses:

```bash
pip install -r requirements.txt
```

The project now also uses `pyproject.toml` for modern Python package configuration, including tool settings for black, isort, mypy, and pytest.

## Common Deployment Issues

### Database Connection Problems

If you encounter database connection issues:

1. Check if databases are running: `docker ps`
2. Verify connection settings in `.env`
3. For local testing, run `scripts/db_test.py` to validate connections
4. Check logs: `docker-compose logs indoxrouter-postgres` or `docker-compose logs indoxrouter-mongodb`

### Permission Issues

If you encounter permission issues:

1. For Docker deployments: `chmod -R 755 /opt/indoxrouter`
2. For local environment: Ensure proper file permissions on scripts

## Security Considerations

1. **API Keys**: Never commit API keys to version control
2. **Firewall**: Configure a firewall to restrict access
3. **Rate Limiting**: Enable and configure rate limiting
4. **Regular Updates**: Keep the system and dependencies updated
5. **SSL/TLS**: Always use HTTPS in production

For specific security questions, refer to the security documentation or consult with a security professional.

## Maintenance Tools and Scripts

The following tools are useful for maintaining your IndoxRouter deployment:

### Production Deployment

- **scripts/deploy_integrated.sh**: Main script for setting up the integrated deployment
- **scripts/setup_nginx.sh**: Script for configuring Nginx and SSL
- **production.env**: Template for production environment variables

### Database Management

- **scripts/db_clear.py**: Script to reset all databases (PostgreSQL and MongoDB)
- **scripts/db_test.py**: Script to test database connections and create test data
- **scripts/migrate_to_mongodb.py**: Script for migrating data to MongoDB

### Testing

- **tests/unit/**: Contains unit tests for individual components
- **tests/integration/**: Contains integration tests that test multiple components together
- **tests/conftest.py**: Shared pytest fixtures and configuration

### Development Tools

- **run_local_db.sh**: Script to start local database containers for development

### Documentation

- **DEPLOYMENT.md**: This deployment guide
- **DATABASE_SETUP.md**: Database setup instructions
- **README.md**: General project documentation
- **scripts/README.md**: Documentation for utility scripts
