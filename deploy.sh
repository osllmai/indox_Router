#!/bin/bash

# Set variables
SERVER_IP="91.107.253.133"
SERVER_USER="root"
APP_DIR="/opt/indoxrouter"

# Build the Docker image locally
echo "Building Docker image..."
docker-compose build

# Create a deployment package
echo "Creating deployment package..."
tar -czf deploy.tar.gz Dockerfile docker-compose.yml indoxRouter/ scripts/ examples/ tests/ pytest.ini requirements-dev.txt setup.py README.md

# Copy the deployment package to the server
echo "Copying deployment package to server..."
scp deploy.tar.gz $SERVER_USER@$SERVER_IP:~

# SSH into the server and deploy
echo "Deploying to server..."
ssh $SERVER_USER@$SERVER_IP << 'EOF'
    # Create application directory if it doesn't exist
    mkdir -p /opt/indoxrouter
    
    # Extract the deployment package
    tar -xzf ~/deploy.tar.gz -C /opt/indoxrouter
    
    # Navigate to the application directory
    cd /opt/indoxrouter
    
    # Make sure Docker and Docker Compose are installed
    if ! command -v docker &> /dev/null; then
        echo "Docker not found, installing..."
        curl -fsSL https://get.docker.com -o get-docker.sh
        sh get-docker.sh
    fi
    
    if ! command -v docker-compose &> /dev/null; then
        echo "Docker Compose not found, installing..."
        curl -L "https://github.com/docker/compose/releases/download/v2.20.3/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
        chmod +x /usr/local/bin/docker-compose
    fi
    
    # Start the application
    docker-compose up -d
    
    # Clean up
    rm ~/deploy.tar.gz
    
    echo "Deployment completed successfully!"
EOF

# Clean up local deployment package
rm deploy.tar.gz

echo "Deployment process completed!" 