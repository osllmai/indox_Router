#!/bin/bash
# IndoxRouter Remote Deployment Script

SERVER_IP="91.107.153.195"
SERVER_USER="root"
REMOTE_DIR="/opt/indoxrouter"
LOG_FILE="/tmp/indox_deploy.log"

# Credential validation
validate_credentials() {
  required_vars=(
    SECRET_KEY
    POSTGRES_PASSWORD
    MONGO_INITDB_ROOT_PASSWORD
    MONGO_APP_PASSWORD
    REDIS_PASSWORD
  )
  
  missing=()
  for var in "${required_vars[@]}"; do
    [ -z "${!var}" ] && missing+=("$var")
  done

  if [ ${#missing[@]} -gt 0 ]; then
    echo "❌ Missing credentials:"
    printf '  - %s\n' "${missing[@]}"
    echo "🛑 Aborting deployment"
    exit 1
  fi
}

# Generate credentials
generate_credentials() {
  # Core application
  export SECRET_KEY=${SECRET_KEY:-$(openssl rand -hex 32)}
  
  # PostgreSQL
  export POSTGRES_USER=${POSTGRES_USER:-indoxrouter_app}
  export POSTGRES_PASSWORD=${POSTGRES_PASSWORD:-$(openssl rand -base64 24)}
  export POSTGRES_DB=${POSTGRES_DB:-indoxrouter}
  export POSTGRES_HOST=${POSTGRES_HOST:-indoxrouter-postgres}
  export POSTGRES_PORT=${POSTGRES_PORT:-5432}

  # MongoDB
  export MONGO_INITDB_ROOT_USERNAME=${MONGO_INITDB_ROOT_USERNAME:-mongo_root_admin}
  export MONGO_INITDB_ROOT_PASSWORD=${MONGO_INITDB_ROOT_PASSWORD:-$(openssl rand -base64 32)}
  export MONGO_APP_USER=${MONGO_APP_USER:-appuser}
  export MONGO_APP_PASSWORD=${MONGO_APP_PASSWORD:-$(openssl rand -base64 32)}
  export MONGO_HOST=${MONGO_HOST:-indoxrouter-mongodb}
  export MONGO_PORT=${MONGO_PORT:-27017}
  export MONGO_INITDB_DATABASE=${MONGO_INITDB_DATABASE:-indoxrouter}

  # Redis
  export REDIS_HOST=${REDIS_HOST:-indoxrouter-redis}
  export REDIS_PORT=${REDIS_PORT:-6379}
  export REDIS_PASSWORD=${REDIS_PASSWORD:-$(openssl rand -base64 24)}

  # Other defaults
  export ACCESS_TOKEN_EXPIRE_MINUTES=${ACCESS_TOKEN_EXPIRE_MINUTES:-60}
  export CACHE_TTL_DAYS=${CACHE_TTL_DAYS:-7}
  export RATE_LIMIT_REQUESTS=${RATE_LIMIT_REQUESTS:-100}
  export RATE_LIMIT_PERIOD_SECONDS=${RATE_LIMIT_PERIOD_SECONDS:-60}
}

# Test SSH connectivity
test_ssh_connectivity() {
  echo "🔄 Testing connection to $SERVER_IP..."
  if ! ssh -o ConnectTimeout=10 -o BatchMode=yes -o StrictHostKeyChecking=accept-new $SERVER_USER@$SERVER_IP "echo 2>&1" >/dev/null; then
    echo "❌ Cannot connect to $SERVER_IP"
    echo "Please check:"
    echo "  1. Server is running and accessible"
    echo "  2. SSH key authentication is set up (or you have password access)"
    echo "  3. Firewall allows SSH connections from your location"
    echo ""
    echo "Try connecting manually: ssh $SERVER_USER@$SERVER_IP"
    return 1
  fi
  echo "✅ SSH connection successful"
  return 0
}

# Deployment package
create_package() {
  TEMP_DIR=$(mktemp -d)
  echo "Created temporary directory: $TEMP_DIR"
  mkdir -p $TEMP_DIR/indoxrouter
  
  # Copy local files instead of git cloning - but exclude unnecessary directories
  echo "Copying local files to deployment package..."
  echo "Source directory: $(dirname "$(dirname "$0")")"
  
  SRC_DIR="$(dirname "$(dirname "$0")")"
  echo "Excluding large/unnecessary directories (venv, __pycache__, etc.)"
  
  # First create directory structure (without files) to ensure all needed dirs exist
  find "$SRC_DIR" -type d -not -path "*/\.*" -not -path "*/venv*" -not -path "*/__pycache__*" | xargs -I{} mkdir -p "$TEMP_DIR/indoxrouter/{}"
  
  # Then copy files, excluding specific directories
  find "$SRC_DIR" -type f -not -path "*/\.*" -not -path "*/venv*" -not -path "*/__pycache__*" -not -path "*/node_modules*" | xargs -I{} cp {} "$TEMP_DIR/indoxrouter/{}"
  
  echo "Files copied to package directory (excluding venv, __pycache__, etc.)"
  
  # Remove sensitive files
  echo "Removing sensitive files from deployment package..."
  rm -f $TEMP_DIR/indoxrouter/CREDENTIALS.md
  rm -f $TEMP_DIR/indoxrouter/.env.local
  echo "Sensitive files removed."
  
  # Copy the local .env file instead of creating a new one
  echo "Copying local .env file to deployment package..."
  if [ -f "$(dirname "$(dirname "$0")")/.env" ]; then
    cp "$(dirname "$(dirname "$0")")/.env" $TEMP_DIR/indoxrouter/.env
    echo "Local .env file copied successfully."
  else
    echo "Warning: No local .env file found. The application may not function correctly without it."
  fi

  # Show what files are in the package
  echo "Files in deployment package:"
  find $TEMP_DIR -type f | sort | head -n 20

  # Create deployment script
  cat > $TEMP_DIR/deploy.sh << 'EOF'
#!/bin/bash
set -e

# Include credentials
if [ -f .env ]; then
  echo "Loading environment variables from .env"
  source .env
fi

# Verify environment
[ -z "$SECRET_KEY" ] && { echo "❌ SECRET_KEY missing"; exit 1; }
[ -z "$POSTGRES_PASSWORD" ] && { echo "❌ POSTGRES_PASSWORD missing"; exit 1; }
[ -z "$MONGO_INITDB_ROOT_PASSWORD" ] && { echo "❌ MONGO_INITDB_ROOT_PASSWORD missing"; exit 1; }
[ -z "$MONGO_APP_PASSWORD" ] && { echo "❌ MONGO_APP_PASSWORD missing"; exit 1; }
[ -z "$REDIS_PASSWORD" ] && { echo "❌ REDIS_PASSWORD missing"; exit 1; }

echo "✓ All required credentials found"

# Install dependencies
echo "📦 Installing dependencies..."
apt-get update -qq
apt-get install -y -qq docker.io docker-compose

# Deploy application
echo "🚢 Starting services with Docker Compose..."
cd /opt/indoxrouter

# Ensure .env file exists and has correct permissions
chmod 600 .env 2>/dev/null || echo "Note: Could not set permissions on .env file"

# Verify docker-compose.yml exists
if [ ! -f "docker-compose.yml" ]; then
  echo "❌ docker-compose.yml not found!"
  echo "Current directory: $(pwd)"
  echo "Files in directory:"
  ls -la
  exit 1
fi
echo "Found docker-compose.yml"

docker-compose down 2>/dev/null || true
docker-compose --env-file .env up -d --build

# Verify deployment
echo "🔍 Verifying deployment..."
sleep 10
docker-compose ps | grep "Up" || { echo "❌ Container failed to start"; exit 1; }

echo "✅ Deployment complete!"
echo "🌐 Your IndoxRouter is now available at: http://91.107.153.195"
EOF

  chmod +x $TEMP_DIR/deploy.sh
}

# Main execution
echo "🚀 Starting IndoxRouter Deployment"
echo "================================="

# Credential handling
if [ "$1" == "--generate" ]; then
  generate_credentials
  echo "Generated credentials:"
  echo "SECRET_KEY=${SECRET_KEY:0:10}..."
  echo "POSTGRES_USER=$POSTGRES_USER"
  echo "POSTGRES_PASSWORD=${POSTGRES_PASSWORD:0:5}..."
  echo "MONGO_INITDB_ROOT_USERNAME=$MONGO_INITDB_ROOT_USERNAME"
  echo "MONGO_INITDB_ROOT_PASSWORD=${MONGO_INITDB_ROOT_PASSWORD:0:5}..."
  echo "MONGO_APP_USER=$MONGO_APP_USER"
  echo "MONGO_APP_PASSWORD=${MONGO_APP_PASSWORD:0:5}..."
  echo "REDIS_PASSWORD=${REDIS_PASSWORD:0:5}..."
else
  validate_credentials
fi

# Test SSH connectivity before proceeding
if ! test_ssh_connectivity; then
  echo "🛑 Aborting deployment due to connection issues."
  exit 1
fi

# Create deployment package
echo "📦 Preparing deployment package..."
create_package

# Ensure target directories exist before transfer
echo "Ensuring target directories exist on server..."
# Check if /opt exists and create it if it doesn't
ssh $SERVER_USER@$SERVER_IP "if [ ! -d /opt ]; then mkdir -p /opt; echo 'Created /opt directory'; fi"
# Now make sure our target directory exists
ssh $SERVER_USER@$SERVER_IP "mkdir -p $REMOTE_DIR"

# Transfer files
echo "📡 Transferring to $SERVER_IP..."
echo "This may take a few minutes depending on your connection speed..."

# Use tar to avoid character encoding issues during transfer
echo "Creating archive for transfer to avoid encoding issues..."
(cd $TEMP_DIR && tar -cf package.tar *)
if [ ! -f "$TEMP_DIR/package.tar" ]; then
  echo "❌ Failed to create deployment package archive"
  rm -rf $TEMP_DIR
  exit 1
fi
echo "Archive created. Size: $(du -h $TEMP_DIR/package.tar | cut -f1)"
echo "Transferring package..."

# Transfer the tar file instead of individual files
echo "Starting SCP transfer to $SERVER_IP:$REMOTE_DIR/package.tar"
if ! scp -o ConnectTimeout=30 $TEMP_DIR/package.tar $SERVER_USER@$SERVER_IP:$REMOTE_DIR/package.tar; then
  echo "❌ File transfer failed!"
  echo "Check your network connection or server status."
  rm -rf $TEMP_DIR
  exit 1
fi

echo "✅ Files transferred successfully!"
echo "📦 Extracting package on the server..."

# Extract the tar file on the server
ssh $SERVER_USER@$SERVER_IP "cd $REMOTE_DIR && tar -xf package.tar && rm package.tar"

# Check the directory structure on the server
echo "Checking directory structure on server..."
ssh $SERVER_USER@$SERVER_IP "ls -la $REMOTE_DIR"

# Move files if needed (if they're in a subdirectory)
echo "Ensuring files are in the correct location..."
ssh $SERVER_USER@$SERVER_IP "
if [ -d \"$REMOTE_DIR/indoxrouter\" ]; then
  echo 'Moving files from indoxrouter subdirectory...'
  mv $REMOTE_DIR/indoxrouter/* $REMOTE_DIR/
  rm -rf $REMOTE_DIR/indoxrouter
fi
"

# Verify docker-compose.yml exists
echo "Verifying docker-compose.yml exists..."
ssh $SERVER_USER@$SERVER_IP "
if [ ! -f \"$REMOTE_DIR/docker-compose.yml\" ]; then
  echo '❌ docker-compose.yml not found!'
  echo 'Available files:'
  ls -la $REMOTE_DIR
  exit 1
else
  echo '✅ docker-compose.yml found'
fi
"

# Ensure Docker Compose file exists by creating it directly on the server
echo "Ensuring docker-compose.yml exists on server..."
ssh $SERVER_USER@$SERVER_IP "cat > $REMOTE_DIR/docker-compose.yml << 'EOF'
version: \"3.8\"

services:
  indoxrouter-server:
    build: .
    container_name: indoxrouter-server
    ports:
      - \"8000:8000\"
    environment:
      - HOST=0.0.0.0
      - PORT=8000
      - DEBUG=false
      - SECRET_KEY=\${SECRET_KEY}
      - POSTGRES_USER=\${POSTGRES_USER}
      - POSTGRES_PASSWORD=\${POSTGRES_PASSWORD}
      - MONGO_ROOT_USER=\${MONGO_ROOT_USER}
      - MONGO_ROOT_PASSWORD=\${MONGO_ROOT_PASSWORD}
      - MONGO_APP_USER=\${MONGO_APP_USER}
      - MONGO_APP_PASSWORD=\${MONGO_APP_PASSWORD}
      - REDIS_PASSWORD=\${REDIS_PASSWORD}
    volumes:
      - ./logs:/app/logs
    depends_on:
      - postgres
      - mongodb
      - redis
    restart: unless-stopped

  postgres:
    image: postgres:15-alpine
    container_name: indoxrouter-postgres
    environment:
      - POSTGRES_DB=indoxrouter
      - POSTGRES_USER=\${POSTGRES_USER}
      - POSTGRES_PASSWORD=\${POSTGRES_PASSWORD}
    volumes:
      - postgres-data:/var/lib/postgresql/data
    restart: unless-stopped

  mongodb:
    image: mongo:6
    container_name: indoxrouter-mongodb
    environment:
      - MONGO_INITDB_ROOT_USERNAME=\${MONGO_INITDB_ROOT_USERNAME}
      - MONGO_INITDB_ROOT_PASSWORD=\${MONGO_INITDB_ROOT_PASSWORD}
      - MONGO_INITDB_DATABASE=indoxrouter
    volumes:
      - mongo-data:/data/db
    restart: unless-stopped

  redis:
    image: redis:7-alpine
    container_name: indoxrouter-redis
    command: redis-server --requirepass \${REDIS_PASSWORD}
    volumes:
      - redis-data:/data
    restart: unless-stopped

volumes:
  postgres-data:
  mongo-data:
  redis-data:
EOF"

# Ensure Dockerfile exists
echo "Ensuring Dockerfile exists on server..."
ssh $SERVER_USER@$SERVER_IP "cat > $REMOTE_DIR/Dockerfile << 'EOF'
FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["python", "main.py"]
EOF"

# Ensure requirements.txt exists
echo "Ensuring requirements.txt exists on server..."
ssh $SERVER_USER@$SERVER_IP "cat > $REMOTE_DIR/requirements.txt << 'EOF'
# Web Framework
fastapi>=0.95.0
uvicorn>=0.22.0,<0.30.0
starlette>=0.27.0
pydantic>=2.0.0
pydantic-settings>=2.0.0

# Authentication
python-jose>=3.3.0
passlib>=1.7.4
python-multipart>=0.0.6
bcrypt>=4.0.1

# HTTP Client
httpx>=0.24.0
requests>=2.31.0
aiohttp>=3.8.0

# AI Providers
openai>=1.0.0
mistralai>=1.6.0
mistral-common==1.5.4
tiktoken>=0.5.0

# Utility
python-dotenv>=1.0.0
tenacity>=8.0.0
cryptography>=40.0.0

# Databases
psycopg2-binary>=2.9.9
pymongo[srv]>=4.6.1
dnspython>=2.4.0
redis>=5.0.0,<=5.2.0

# Testing
pytest>=7.0.0
pytest-asyncio>=0.21.0
pytest-cov>=4.0.0

# Deployment tools
gunicorn>=21.0.0
EOF"

# Create a startup script
echo "Creating startup script on server..."
ssh $SERVER_USER@$SERVER_IP "cat > $REMOTE_DIR/start.sh << 'EOF'
#!/bin/bash
set -e

# Load environment variables
source .env

# Pull the latest images
docker-compose pull

# Start the services
docker-compose up -d

echo "Application started successfully!"
echo "You can access the server at http://\$SERVER_IP"
EOF"

ssh $SERVER_USER@$SERVER_IP "chmod +x $REMOTE_DIR/start.sh"

# Create a stop script
echo "Creating stop script on server..."
ssh $SERVER_USER@$SERVER_IP "cat > $REMOTE_DIR/stop.sh << 'EOF'
#!/bin/bash
set -e

echo "Stopping application..."
docker-compose down

echo "Application stopped successfully!"
EOF"

ssh $SERVER_USER@$SERVER_IP "chmod +x $REMOTE_DIR/stop.sh"

# Main deployment execution
if ! ssh -o ConnectTimeout=30 $SERVER_USER@$SERVER_IP "
  cd $REMOTE_DIR && 
  chmod +x deploy.sh && 
  source .env &&
  ./deploy.sh
"; then
  echo "❌ Remote execution failed!"
  echo "Try connecting to the server manually to diagnose the issue:"
  echo "  ssh $SERVER_USER@$SERVER_IP"
  rm -rf $TEMP_DIR
  exit 1
fi

# Cleanup
rm -rf $TEMP_DIR
echo "✅ Deployment completed successfully!"
echo "🔗 Access: http://$SERVER_IP"