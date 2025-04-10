#!/bin/bash

# IndoxRouter Server - Integrated Deployment Script
# This script deploys IndoxRouter with integrated databases on a single server

echo "IndoxRouter Server - Integrated Deployment Script"
echo "================================================"

# Check if running as root
if [ "$EUID" -ne 0 ]; then
  echo "Please run as root"
  exit 1
fi

# Update system packages
echo "Updating system packages..."
apt-get update && apt-get upgrade -y

# Install Docker and dependencies
echo "Installing Docker and dependencies..."
apt-get install -y docker.io docker-compose git curl ufw

# Enable and start Docker service
systemctl enable docker
systemctl start docker

# Create application directory
echo "Creating application directory..."
mkdir -p /opt/indoxrouter
cd /opt/indoxrouter

# Clone the repository (replace with your actual repository)
echo "Cloning the repository..."
git clone https://github.com/yourusername/indoxrouter.git .
cd indoxrouter_server

# Copy production environment file
echo "Setting up environment file..."
cp production.env .env

# Create data directories with proper permissions
echo "Creating data directories..."
mkdir -p ./logs
mkdir -p ./data/postgres
mkdir -p ./data/mongodb
mkdir -p ./data/redis
chmod 755 -R ./logs ./data

# Set up firewall
echo "Configuring firewall..."
ufw allow 22/tcp
ufw allow 80/tcp
ufw allow 443/tcp
ufw --force enable

# Create a secure secret key
echo "Generating secure secret key..."
SECRET_KEY=$(openssl rand -hex 32)
sed -i "s/change_this_to_a_secure_secret_in_production/$SECRET_KEY/" .env

# Start the services
echo "Starting IndoxRouter services..."
docker-compose up -d

# Print status information
echo ""
echo "IndoxRouter deployed successfully!"
echo "=================================="
echo ""
echo "API Server: http://91.107.253.133:8000"
echo ""
echo "To check the status, run: docker-compose ps"
echo "To view logs, run: docker-compose logs -f"
echo ""
echo "Next steps:"
echo "1. Set up a domain name"
echo "2. Configure Nginx as a reverse proxy"
echo "3. Set up SSL with Let's Encrypt"
echo ""
echo "Run this command to set up Nginx + SSL:"
echo "bash scripts/setup_nginx.sh yourdomain.com" 