#!/bin/bash

# IndoxRouter Server - Remote Deployment Script
# This script deploys IndoxRouter to a remote server at 91.107.153.195

# Server credentials
SERVER_IP="91.107.153.195"
SERVER_USER="root"
REMOTE_DIR="/opt/indoxrouter"

# Prompt for passwords if not set in environment - with appropriate warnings
if [ -z "$SERVER_PASSWORD" ]; then
  echo "⚠️ WARNING: SERVER_PASSWORD is not set in the environment."
  read -sp "Enter server password (leave empty to prompt for it during SSH): " SERVER_PASSWORD
  echo
fi

echo "IndoxRouter Server - Remote Deployment Script"
echo "============================================="
echo "Target server: $SERVER_IP"
echo "Remote directory: $REMOTE_DIR"
echo

# Security check for credentials
echo "Checking security credentials..."
NEED_CREDENTIALS=false

if [ -z "$SECRET_KEY" ]; then
  echo "⚠️ WARNING: SECRET_KEY is not set in the environment."
  NEED_CREDENTIALS=true
fi

if [ -z "$POSTGRES_PASSWORD" ]; then
  echo "⚠️ WARNING: POSTGRES_PASSWORD is not set in the environment."
  NEED_CREDENTIALS=true
fi

if [ -z "$MONGO_PASSWORD" ]; then
  echo "⚠️ WARNING: MONGO_PASSWORD is not set in the environment."
  NEED_CREDENTIALS=true
fi

if [ -z "$REDIS_PASSWORD" ]; then
  echo "⚠️ WARNING: REDIS_PASSWORD is not set in the environment."
  NEED_CREDENTIALS=true
fi

# If any credentials are missing, ask what to do
if [ "$NEED_CREDENTIALS" = true ]; then
  echo
  echo "Some security credentials are missing. You have these options:"
  echo "1. Generate secure random credentials (recommended for new deployments)"
  echo "2. Enter credentials manually"
  echo "3. Abort deployment to set them in your environment"
  echo
  read -p "Enter your choice (1/2/3): " CRED_CHOICE
  
  case $CRED_CHOICE in
    1)
      echo "Generating secure random credentials..."
      if [ -z "$SECRET_KEY" ]; then
        SECRET_KEY=$(openssl rand -hex 32)
        echo "✓ Generated SECRET_KEY"
      fi
      
      if [ -z "$POSTGRES_PASSWORD" ]; then
        POSTGRES_PASSWORD=$(openssl rand -base64 24)
        echo "✓ Generated POSTGRES_PASSWORD"
      fi
      
      if [ -z "$MONGO_PASSWORD" ]; then
        MONGO_PASSWORD=$(openssl rand -base64 24)
        echo "✓ Generated MONGO_PASSWORD"
      fi
      
      if [ -z "$REDIS_PASSWORD" ]; then
        REDIS_PASSWORD=$(openssl rand -base64 24)
        echo "✓ Generated REDIS_PASSWORD"
      fi
      ;;
      
    2)
      if [ -z "$SECRET_KEY" ]; then
        read -p "Enter SECRET_KEY (or leave empty to generate): " SECRET_KEY
        if [ -z "$SECRET_KEY" ]; then
          SECRET_KEY=$(openssl rand -hex 32)
          echo "✓ Generated SECRET_KEY"
        fi
      fi
      
      if [ -z "$POSTGRES_PASSWORD" ]; then
        read -sp "Enter POSTGRES_PASSWORD (or leave empty to generate): " POSTGRES_PASSWORD
        echo
        if [ -z "$POSTGRES_PASSWORD" ]; then
          POSTGRES_PASSWORD=$(openssl rand -base64 24)
          echo "✓ Generated POSTGRES_PASSWORD"
        fi
      fi
      
      if [ -z "$MONGO_PASSWORD" ]; then
        read -sp "Enter MONGO_PASSWORD (or leave empty to generate): " MONGO_PASSWORD
        echo
        if [ -z "$MONGO_PASSWORD" ]; then
          MONGO_PASSWORD=$(openssl rand -base64 24)
          echo "✓ Generated MONGO_PASSWORD"
        fi
      fi
      
      if [ -z "$REDIS_PASSWORD" ]; then
        read -sp "Enter REDIS_PASSWORD (or leave empty to generate): " REDIS_PASSWORD
        echo
        if [ -z "$REDIS_PASSWORD" ]; then
          REDIS_PASSWORD=$(openssl rand -base64 24)
          echo "✓ Generated REDIS_PASSWORD"
        fi
      fi
      ;;
      
    3)
      echo "Deployment aborted. Please set the following environment variables:"
      [ -z "$SECRET_KEY" ] && echo "- SECRET_KEY"
      [ -z "$POSTGRES_PASSWORD" ] && echo "- POSTGRES_PASSWORD"
      [ -z "$MONGO_PASSWORD" ] && echo "- MONGO_PASSWORD" 
      [ -z "$REDIS_PASSWORD" ] && echo "- REDIS_PASSWORD"
      exit 1
      ;;
      
    *)
      echo "Invalid choice. Aborting deployment."
      exit 1
      ;;
  esac
  
  # Show a summary of the credentials that will be used
  echo
  echo "The following credentials will be used for deployment:"
  echo "- SECRET_KEY: ${SECRET_KEY:0:5}... (${#SECRET_KEY} characters)"
  echo "- POSTGRES_PASSWORD: ${POSTGRES_PASSWORD:0:3}... (${#POSTGRES_PASSWORD} characters)"
  echo "- MONGO_PASSWORD: ${MONGO_PASSWORD:0:3}... (${#MONGO_PASSWORD} characters)"
  echo "- REDIS_PASSWORD: ${REDIS_PASSWORD:0:3}... (${#REDIS_PASSWORD} characters)"
  echo
  
  read -p "Do you want to continue with these credentials? (y/n): " CONFIRM
  if [[ ! $CONFIRM =~ ^[Yy]$ ]]; then
    echo "Deployment aborted."
    exit 1
  fi
fi

# Use SSH keys instead of sshpass
USE_SSH_KEYS=true

# Check if ssh-copy-id has been run
if [ "$USE_SSH_KEYS" = false ]; then
  # Check if sshpass is installed
  if ! command -v sshpass &> /dev/null; then
    echo "sshpass is not installed. Please install it for password-based SSH."
    echo "On Ubuntu/Debian: sudo apt-get install sshpass"
    echo "On macOS with Homebrew: brew install hudochenkov/sshpass/sshpass"
    echo
    echo "Alternatively, you can manually copy your SSH key to the server:"
    echo "ssh-copy-id $SERVER_USER@$SERVER_IP"
    echo
    echo "Or set USE_SSH_KEYS=true in this script to use SSH keys instead."
    exit 1
  fi
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
cp DEPLOYMENT.md $TEMP_DIR/indoxrouter_server/ 2>/dev/null || echo "No DEPLOYMENT.md found"
cp DATABASE_SETUP.md $TEMP_DIR/indoxrouter_server/ 2>/dev/null || echo "No DATABASE_SETUP.md found"
cp main.py $TEMP_DIR/indoxrouter_server/
cp -r migrations $TEMP_DIR/indoxrouter_server/ 2>/dev/null || echo "No migrations directory found"

# Create .env file for credentials but don't include it in the repository
cat > $TEMP_DIR/credentials.env << EOF
# Generated credentials file - DO NOT COMMIT TO REPOSITORY
# Generated on: $(date)
SECRET_KEY=$SECRET_KEY
POSTGRES_PASSWORD=$POSTGRES_PASSWORD
MONGO_PASSWORD=$MONGO_PASSWORD
REDIS_PASSWORD=$REDIS_PASSWORD
SERVER_PASSWORD=$SERVER_PASSWORD
EOF

# Set permissions on credentials file
chmod 600 $TEMP_DIR/credentials.env

# Create deployment script
cat > $TEMP_DIR/deploy.sh << 'EOF'
#!/bin/bash

# Source credentials
if [ -f credentials.env ]; then
  source credentials.env
  echo "Loaded credentials from environment file"
else
  echo "ERROR: credentials.env file not found!"
  exit 1
fi

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

# Set up environment with secure credentials
cp production.env .env

# Replace placeholders with actual values
sed -i "s|\${SECRET_KEY}|$SECRET_KEY|g" .env
sed -i "s|\${POSTGRES_PASSWORD}|$POSTGRES_PASSWORD|g" .env
sed -i "s|\${MONGO_PASSWORD}|$MONGO_PASSWORD|g" .env
sed -i "s|\${REDIS_PASSWORD}|$REDIS_PASSWORD|g" .env

# Update docker-compose.yml with credentials
sed -i "s|SECRET_KEY:-.*}|SECRET_KEY:-$SECRET_KEY}|g" docker-compose.yml
sed -i "s|POSTGRES_PASSWORD=.*|POSTGRES_PASSWORD=$POSTGRES_PASSWORD|g" docker-compose.yml
sed -i "s|DATABASE_URL=postgresql://.*@|DATABASE_URL=postgresql://indoxrouter_admin:$POSTGRES_PASSWORD@|g" docker-compose.yml
sed -i "s|MONGO_INITDB_ROOT_PASSWORD=.*|MONGO_INITDB_ROOT_PASSWORD=$MONGO_PASSWORD|g" docker-compose.yml
sed -i "s|MONGODB_URI=mongodb://.*@|MONGODB_URI=mongodb://indoxrouter_admin:$MONGO_PASSWORD@|g" docker-compose.yml
sed -i "s|redis-server --requirepass .*|redis-server --requirepass $REDIS_PASSWORD|g" docker-compose.yml
sed -i "s|\[\"CMD\", \"redis-cli\", \"-a\", \".*\", \"ping\"\]|[\"CMD\", \"redis-cli\", \"-a\", \"$REDIS_PASSWORD\", \"ping\"]|g" docker-compose.yml

# Update backup script with credentials
sed -i "s|POSTGRES_PASSWORD=.*|POSTGRES_PASSWORD=\"$POSTGRES_PASSWORD\"|g" scripts/backup_databases.sh
sed -i "s|MONGO_PASSWORD=.*|MONGO_PASSWORD=\"$MONGO_PASSWORD\"|g" scripts/backup_databases.sh
sed -i "s|REDIS_PASSWORD=.*|REDIS_PASSWORD=\"$REDIS_PASSWORD\"|g" scripts/backup_databases.sh

# Save credentials locally (protected file)
cat > /opt/indoxrouter/CREDENTIALS.md << EOC
# IndoxRouter Server Credentials

**IMPORTANT: Keep this file secure and do not commit it to version control!**

## Server Details

- **IP Address**: 91.107.153.195
- **SSH Access**: \`ssh root@91.107.153.195\`

## Database Credentials

### PostgreSQL

- **User**: \`indoxrouter_admin\`
- **Password**: \`$POSTGRES_PASSWORD\`
- **Database**: \`indoxrouter\`
- **Port**: \`5432\` (inside Docker), \`15432\` (host mapping)
- **Connection URL**: \`postgresql://indoxrouter_admin:$POSTGRES_PASSWORD@indoxrouter-postgres:5432/indoxrouter\`

### MongoDB

- **User**: \`indoxrouter_admin\`
- **Password**: \`$MONGO_PASSWORD\`
- **Database**: \`indoxrouter\`
- **Port**: \`27017\` (inside Docker), \`27018\` (host mapping)
- **Connection URL**: \`mongodb://indoxrouter_admin:$MONGO_PASSWORD@indoxrouter-mongodb:27017/indoxrouter?authSource=admin\`

### Redis

- **Password**: \`$REDIS_PASSWORD\`
- **Port**: \`6379\` (inside Docker), \`6380\` (host mapping)

## Application Secrets

- **SECRET_KEY**: \`$SECRET_KEY\`

## Database Backups

- **Backup Directory**: \`/opt/indoxrouter/backups\`
- **Schedule**: Daily at 2:00 AM
- **Retention**: 14 days (older backups are automatically deleted)
- **Backup Formats**:
  - PostgreSQL: SQL dump (gzipped)
  - MongoDB: Archive format (gzipped)
  - Redis: RDB files
- **Manual Backup**: Run \`bash /opt/indoxrouter/scripts/backup_databases.sh\` to create a manual backup
- **Logs**: Backup logs are stored in \`/opt/indoxrouter/logs/backup.log\`
EOC

# Make the credentials file readable only by root
chmod 600 /opt/indoxrouter/CREDENTIALS.md

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

# Clean up sensitive data
echo "Cleaning up sensitive deployment data..."
rm -f /root/credentials.env
echo "Secure cleanup complete."
EOF

# Make deployment script executable
chmod +x $TEMP_DIR/deploy.sh

# Final confirmation before deployment
echo
echo "Ready to deploy IndoxRouter to server: $SERVER_IP"
echo "All necessary files have been prepared."
echo
read -p "Do you want to proceed with the deployment? (y/n): " FINAL_CONFIRM
if [[ ! $FINAL_CONFIRM =~ ^[Yy]$ ]]; then
  echo "Deployment aborted."
  rm -rf $TEMP_DIR
  exit 1
fi

# Transfer files to the server
echo "Transferring files to $SERVER_IP..."
if [ "$USE_SSH_KEYS" = true ]; then
  scp -o StrictHostKeyChecking=no -r $TEMP_DIR/* $SERVER_USER@$SERVER_IP:/root/
else
  sshpass -p "$SERVER_PASSWORD" scp -o StrictHostKeyChecking=no -r $TEMP_DIR/* $SERVER_USER@$SERVER_IP:/root/
fi

# Execute deployment script
echo "Executing deployment script on remote server..."
if [ "$USE_SSH_KEYS" = true ]; then
  ssh -o StrictHostKeyChecking=no $SERVER_USER@$SERVER_IP "bash /root/deploy.sh"
else
  sshpass -p "$SERVER_PASSWORD" ssh -o StrictHostKeyChecking=no $SERVER_USER@$SERVER_IP "bash /root/deploy.sh"
fi

# Clean up temporary directory
echo "Cleaning up local temporary files..."
rm -rf $TEMP_DIR

echo
echo "Deployment completed!"
echo "====================="
echo
echo "To check the status of your deployment:"
if [ "$USE_SSH_KEYS" = true ]; then
  echo "ssh $SERVER_USER@$SERVER_IP 'cd $REMOTE_DIR && docker-compose ps'"
else
  echo "sshpass -p \"$SERVER_PASSWORD\" ssh -o StrictHostKeyChecking=no $SERVER_USER@$SERVER_IP 'cd $REMOTE_DIR && docker-compose ps'"
fi
echo
echo "To view the logs:"
if [ "$USE_SSH_KEYS" = true ]; then
  echo "ssh $SERVER_USER@$SERVER_IP 'cd $REMOTE_DIR && docker-compose logs -f'"
else
  echo "sshpass -p \"$SERVER_PASSWORD\" ssh -o StrictHostKeyChecking=no $SERVER_USER@$SERVER_IP 'cd $REMOTE_DIR && docker-compose logs -f'"
fi
echo
echo "Your IndoxRouter server should be accessible at:"
echo "http://$SERVER_IP"
echo
echo "Important:"
echo "1. Make sure to update your API keys in /opt/indoxrouter/.env"
echo "2. For better security, set up a domain name and SSL"
echo "3. All credentials are saved in /opt/indoxrouter/CREDENTIALS.md - keep this file secure!"
echo "4. Database backups will run daily at 2:00 AM and be stored in /opt/indoxrouter/backups"
echo

# Also save credentials locally for reference (but don't push to git)
mkdir -p ~/.indoxrouter
cat > ~/.indoxrouter/credentials.txt << EOF
# IndoxRouter Deployment Credentials (${SERVER_IP})
# Created: $(date)
# IMPORTANT: Keep this file secure and do not share it!

SECRET_KEY=${SECRET_KEY}
POSTGRES_PASSWORD=${POSTGRES_PASSWORD}
MONGO_PASSWORD=${MONGO_PASSWORD}
REDIS_PASSWORD=${REDIS_PASSWORD}
SERVER_PASSWORD=${SERVER_PASSWORD}
EOF

chmod 600 ~/.indoxrouter/credentials.txt
echo "Credentials saved locally to ~/.indoxrouter/credentials.txt for future reference" 