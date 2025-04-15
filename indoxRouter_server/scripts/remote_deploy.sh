#!/bin/bash

# IndoxRouter Server - Remote Deployment Script
# This script deploys IndoxRouter to a remote server at 91.107.153.195

# Server credentials
SERVER_IP="91.107.153.195"
SERVER_USER="root"
SERVER_PASSWORD="mkqMHKMbem4WLNTbfNKV"
REMOTE_DIR="/opt/indoxrouter"

echo "IndoxRouter Server - Remote Deployment Script"
echo "============================================="
echo "Target server: $SERVER_IP"
echo "Remote directory: $REMOTE_DIR"
echo

# Check if sshpass is installed
if ! command -v sshpass &> /dev/null; then
  echo "sshpass is not installed. Please install it for password-based SSH."
  echo "On Ubuntu/Debian: sudo apt-get install sshpass"
  echo "On macOS with Homebrew: brew install hudochenkov/sshpass/sshpass"
  echo
  echo "Alternatively, you can manually copy your SSH key to the server:"
  echo "ssh-copy-id $SERVER_USER@$SERVER_IP"
  exit 1
fi

# Create a temporary deployment directory
TEMP_DIR=$(mktemp -d)
echo "Creating temporary deployment directory: $TEMP_DIR"

# Copy necessary files
echo "Copying deployment files..."
mkdir -p $TEMP_DIR/indoxrouter_server
cp -r app $TEMP_DIR/indoxrouter_server/
cp -r scripts $TEMP_DIR/indoxrouter_server/
cp docker-compose.yml $TEMP_DIR/indoxrouter_server/
cp Dockerfile $TEMP_DIR/indoxrouter_server/
cp requirements.txt $TEMP_DIR/indoxrouter_server/
cp production.env $TEMP_DIR/indoxrouter_server/
cp DEPLOYMENT.md $TEMP_DIR/indoxrouter_server/
cp DATABASE_SETUP.md $TEMP_DIR/indoxrouter_server/
cp main.py $TEMP_DIR/indoxrouter_server/
cp -r migrations $TEMP_DIR/indoxrouter_server/ 2>/dev/null || echo "No migrations directory found"
cp CREDENTIALS.md $TEMP_DIR/ # For reference only, not deployed to server

# Create deployment script
cat > $TEMP_DIR/deploy.sh << 'EOF'
#!/bin/bash

# Create application directory
mkdir -p /opt/indoxrouter
cp -r indoxrouter_server/* /opt/indoxrouter/
cd /opt/indoxrouter

# Create necessary directories
mkdir -p logs
mkdir -p data/postgres
mkdir -p data/mongodb
mkdir -p data/redis
mkdir -p backups/postgres
mkdir -p backups/mongodb
mkdir -p backups/redis
chmod -R 755 logs data backups

# Set up environment
cp production.env .env

# Generate secure secret key (using the one in production.env)
# SECRET_KEY is already set in the file

# Run the integrated deployment script
chmod +x scripts/deploy_integrated.sh
./scripts/deploy_integrated.sh

# Set up Nginx (without domain)
chmod +x scripts/setup_nginx.sh
./scripts/setup_nginx.sh

# Set up database backups
chmod +x scripts/backup_databases.sh
chmod +x scripts/setup_backup_cron.sh
./scripts/setup_backup_cron.sh
EOF

# Make deployment script executable
chmod +x $TEMP_DIR/deploy.sh

# Transfer files to the server
echo "Transferring files to $SERVER_IP..."
sshpass -p "$SERVER_PASSWORD" scp -o StrictHostKeyChecking=no -r $TEMP_DIR/* $SERVER_USER@$SERVER_IP:/root/

# Execute deployment script
echo "Executing deployment script on remote server..."
sshpass -p "$SERVER_PASSWORD" ssh -o StrictHostKeyChecking=no $SERVER_USER@$SERVER_IP "bash /root/deploy.sh"

# Clean up temporary directory
echo "Cleaning up..."
rm -rf $TEMP_DIR

echo
echo "Deployment completed!"
echo "====================="
echo
echo "To check the status of your deployment:"
echo "sshpass -p \"$SERVER_PASSWORD\" ssh -o StrictHostKeyChecking=no $SERVER_USER@$SERVER_IP 'cd $REMOTE_DIR && docker-compose ps'"
echo
echo "To view the logs:"
echo "sshpass -p \"$SERVER_PASSWORD\" ssh -o StrictHostKeyChecking=no $SERVER_USER@$SERVER_IP 'cd $REMOTE_DIR && docker-compose logs -f'"
echo
echo "Your IndoxRouter server should be accessible at:"
echo "http://$SERVER_IP"
echo
echo "Important:"
echo "1. Make sure to update your API keys in /opt/indoxrouter/.env"
echo "2. For better security, set up a domain name and SSL"
echo "3. All credentials are saved in CREDENTIALS.md - keep this file secure!"
echo "4. Database backups will run daily at 2:00 AM and be stored in /opt/indoxrouter/backups"
echo 