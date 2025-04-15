# IndoxRouter Deployment Guide - Quick Start

This guide provides quick steps to deploy IndoxRouter to your remote server at 91.107.153.195.

## Prerequisites

- SSH access to your remote server (root user)
- Git installed on your local machine
- Docker and Docker Compose installed on your server (will be installed by the deployment script if not present)

## Option 1: Using the Remote Deployment Script (Easiest)

The remote deployment script automates the entire deployment process:

1. On your local machine, navigate to the project directory:

   ```bash
   cd indoxrouter_server
   ```

2. Run the remote deployment script:

   ```bash
   # On Linux/Mac
   bash scripts/remote_deploy.sh

   # On Windows (PowerShell)
   bash -c "./scripts/remote_deploy.sh"
   ```

3. The script will:

   - Copy necessary files to the remote server
   - Install dependencies (Docker, Docker Compose, etc.)
   - Set up the environment
   - Start the application and databases
   - Configure Nginx as a reverse proxy

4. Once deployed, your IndoxRouter server will be accessible at:
   ```
   http://91.107.153.195
   ```

## Option 2: Manual Deployment

If you prefer a manual approach, follow these steps:

1. SSH into your server:

   ```bash
   ssh root@91.107.153.195
   ```

2. Install dependencies:

   ```bash
   apt-get update && apt-get upgrade -y
   apt-get install -y docker.io docker-compose git curl
   ```

3. Create the application directory:

   ```bash
   mkdir -p /opt/indoxrouter
   cd /opt/indoxrouter
   ```

4. Clone or copy the repository:

   ```bash
   # If using Git
   git clone https://github.com/your-username/indoxrouter.git .

   # Or manually copy files to this directory
   ```

5. Navigate to the server directory:

   ```bash
   cd indoxrouter_server
   ```

6. Set up the environment:

   ```bash
   cp production.env .env
   ```

7. Edit the environment file to set your API keys:

   ```bash
   nano .env
   ```

8. Start the services:

   ```bash
   docker-compose up -d
   ```

9. Set up Nginx (optional):

   ```bash
   # Install Nginx
   apt-get install -y nginx

   # Configure Nginx
   bash scripts/setup_nginx.sh
   ```

## Checking the Deployment

Check if all services are running:

```bash
docker-compose ps
```

View the logs:

```bash
docker-compose logs
```

Follow logs in real-time:

```bash
docker-compose logs -f
```

## Next Steps

- [Set up a domain name and SSL](indoxrouter_server/DEPLOYMENT.md)
- [Configure backups](indoxrouter_server/DATABASE_SETUP.md)
- [Configure LLM provider API keys](indoxrouter_server/production.env)

## Troubleshooting

If you encounter any issues, check the logs:

```bash
# Check all logs
docker-compose logs

# Check specific service logs
docker-compose logs indoxrouter-server
docker-compose logs indoxrouter-postgres
docker-compose logs indoxrouter-mongodb
```

Common issues:

- Port conflicts: Make sure ports 80, 443, and 8000 are not in use
- Database connection: Check if all services are healthy
- API keys: Ensure you've set valid API keys in the .env file
