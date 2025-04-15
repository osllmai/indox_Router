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

2. Set up SSH key authentication (recommended for all users, required for Windows):

   ```bash
   # Copy your SSH key to the server
   ssh-copy-id root@91.107.153.195

   # When prompted, enter the server password: mkqMHKMbem4WLNTbfNKV
   ```

   If you're on Windows and don't have ssh-copy-id, use these commands in Git Bash:

   ```bash
   # First check if you have an SSH key
   ls -la ~/.ssh/

   # If id_rsa.pub doesn't exist, generate a key
   ssh-keygen

   # Copy your key to the server
   cat ~/.ssh/id_rsa.pub | ssh root@91.107.153.195 "mkdir -p ~/.ssh && cat >> ~/.ssh/authorized_keys"

   # When prompted, enter the server password: mkqMHKMbem4WLNTbfNKV
   ```

3. Run the remote deployment script:

   ```bash
   # On Linux/Mac/Windows with Git Bash
   bash scripts/remote_deploy.sh

   # On Windows PowerShell (alternative)
   bash -c "./scripts/remote_deploy.sh"
   ```

4. The script will:

   - Copy necessary files to the remote server
   - Install dependencies (Docker, Docker Compose, etc.)
   - Set up the environment
   - Start the application and databases
   - Configure Nginx as a reverse proxy
   - Set up automated daily database backups

5. Once deployed, your IndoxRouter server will be accessible at:
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

10. Set up database backups:

    ```bash
    # Create backup directories
    mkdir -p /opt/indoxrouter/backups/postgres
    mkdir -p /opt/indoxrouter/backups/mongodb
    mkdir -p /opt/indoxrouter/backups/redis

    # Set up the backup cron job
    bash scripts/setup_backup_cron.sh
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

## Database Backups

The deployment includes an automated backup system that:

- Runs daily at 2:00 AM
- Backs up PostgreSQL, MongoDB, and Redis
- Stores backups in `/opt/indoxrouter/backups`
- Keeps backups for 14 days (older backups are automatically removed)

To manually trigger a backup:

```bash
bash /opt/indoxrouter/scripts/backup_databases.sh
```

To view backup logs:

```bash
cat /opt/indoxrouter/logs/backup.log
```

## Next Steps

- [Set up a domain name and SSL](indoxrouter_server/DEPLOYMENT.md)
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
- Windows deployment: If deployment fails, make sure you've properly copied your SSH key to the server
