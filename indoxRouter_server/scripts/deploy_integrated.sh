#!/bin/bash
# IndoxRouter Server - Integrated Deployment Script

echo "IndoxRouter Server - Integrated Deployment"
echo "========================================="

# Check root
if [ "$EUID" -ne 0 ]; then
  echo "❗ Please run as root"
  exit 1
fi

# System updates
echo "🔄 Updating system packages..."
apt-get update -qq && apt-get upgrade -y -qq

# Install dependencies
echo "🔧 Installing dependencies..."
apt-get install -y -qq \
  docker.io \
  docker-compose \
  curl \
  ufw \
  git \
  openssl

# Docker setup
echo "🐳 Configuring Docker..."
systemctl enable --now docker
usermod -aG docker $SUDO_USER

# Application directory setup
echo "📁 Creating application structure..."
APP_DIR="/opt/indoxrouter"
mkdir -p $APP_DIR/{data,logs,backups}
mkdir -p $APP_DIR/data/{postgres,mongodb,redis}
chmod -R 755 $APP_DIR
chown -R $SUDO_USER:$SUDO_USER $APP_DIR
chown -R indoxbackup:indoxbackup $APP_DIR
# Firewall configuration
echo "🔥 Configuring firewall..."
ufw allow 22/tcp
ufw allow 80/tcp
ufw allow 443/tcp
ufw --force enable

# # Clone repository
# echo "📦 Cloning application code..."
# git clone https://github.com/yourusername/indoxrouter.git $APP_DIR
cd $APP_DIR

# Build services
echo "🏗️  Building containers..."
docker-compose --env-file .env up -d --build

# Verification
echo ""
echo "✅ Deployment complete!"
echo "======================"
echo ""
echo "Application URL: http://$(hostname -I | awk '{print $1}')"
echo ""
echo "Management commands:"
echo "  docker-compose ps      # Check service status"
echo "  docker-compose logs    # View service logs"
echo ""
echo "Next steps:"
echo "1. Run setup_nginx.sh to configure reverse proxy"
echo "2. Set up monitoring with setup_monitoring.sh"
echo "3. Review backup configuration in scripts/"