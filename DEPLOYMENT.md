# Deployment Guide for indoxRouter

This guide explains how to deploy the indoxRouter application to your server using Docker.

## Prerequisites

- Docker and Docker Compose installed on your local machine
- SSH access to your server
- Server IP: 91.107.253.133
- Server user: root
- Your indoxRouter API key

## Deployment Options

### Option 1: Using the Deployment Script (Recommended)

1. Make sure the deployment script is executable:

   ```bash
   # On Linux/Mac
   chmod +x deploy.sh

   # On Windows
   # The script should already be executable
   ```

2. **Important**: Before running the deployment script, update your indoxRouter API key in the `docker-compose.yml` file:

   ```yaml
   environment:
     - INDOXROUTER_API_KEY=your_api_key_here
   ```

3. Run the deployment script:

   ```bash
   ./deploy.sh
   ```

   This script will:

   - Build the Docker image locally
   - Create a deployment package
   - Copy the package to your server
   - Install Docker and Docker Compose on the server if needed
   - Deploy and start the application

### Option 2: Manual Deployment

If you prefer to deploy manually, follow these steps:

1. **Important**: First, update your indoxRouter API key in the `docker-compose.yml` file as shown above.

2. Build and package the application:

   ```bash
   # Create a deployment package
   tar -czf deploy.tar.gz Dockerfile docker-compose.yml indoxRouter/ scripts/ examples/ tests/ pytest.ini requirements-dev.txt setup.py README.md
   ```

3. Copy the package to your server:

   ```bash
   scp deploy.tar.gz root@91.107.253.133:~
   ```

4. SSH into your server:

   ```bash
   ssh root@91.107.253.133
   ```

5. On the server, extract and deploy:

   ```bash
   # Create application directory
   mkdir -p /opt/indoxrouter

   # Extract the deployment package
   tar -xzf ~/deploy.tar.gz -C /opt/indoxrouter

   # Navigate to the application directory
   cd /opt/indoxrouter

   # Install Docker if needed
   curl -fsSL https://get.docker.com -o get-docker.sh
   sh get-docker.sh

   # Install Docker Compose if needed
   curl -L "https://github.com/docker/compose/releases/download/v2.20.3/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
   chmod +x /usr/local/bin/docker-compose

   # Start the application
   docker-compose up -d
   ```

## Configuration

Before deploying, you must update the following in the `docker-compose.yml` file:

1. **indoxRouter API Key**:

   - `INDOXROUTER_API_KEY`: Your indoxRouter API key for accessing the service

2. Other configuration options in the Dockerfile if needed.

## Accessing the Application

After deployment, the application will be accessible at:

- HTTP: http://91.107.253.133:8000

## Troubleshooting

If you encounter any issues during deployment:

1. Check Docker container logs:

   ```bash
   docker logs indoxrouter
   ```

2. Check Docker Compose status:

   ```bash
   docker-compose ps
   ```

3. Restart the application:

   ```bash
   docker-compose restart
   ```

4. Rebuild and redeploy:
   ```bash
   docker-compose down
   docker-compose up -d --build
   ```
