# Production Deployment Guide for IndoxRouter

This guide explains how to deploy the IndoxRouter server to your production environment.

## Prerequisites

- Your server (IPv4: 91.107.253.133, IPv6: 2a01:4f8:1c1b:2aa9::/64)
- Access to your website's PostgreSQL database (where users and API keys are stored)
- Domain name (optional but recommended)

## Step 1: Configure Access to the Website Database

The IndoxRouter server needs to connect to your website's database to validate API keys. Make sure:

1. Your website database has the necessary tables for users and API keys
2. The database user has appropriate read permissions
3. The database is accessible from the server where IndoxRouter will run

### Expected Database Schema

Your website database should have tables similar to:

```sql
-- Users table
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    -- other user fields
    is_active BOOLEAN DEFAULT TRUE
);

-- API keys table
CREATE TABLE api_keys (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    api_key VARCHAR(100) UNIQUE NOT NULL,
    name VARCHAR(50) NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP NULL
);

-- Optional: API request logging table
CREATE TABLE api_requests (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    api_key_id INTEGER REFERENCES api_keys(id),
    endpoint VARCHAR(50) NOT NULL,
    provider VARCHAR(50),
    model VARCHAR(100),
    status_code INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

## Step 2: Prepare the Server Environment

### 2.1 Connect to Your Server and Clone the Repository

```bash
# SSH into your server using the provided credentials
ssh root@91.107.253.133
# Password: a9heJi99FNaJHTUk4pxwa

# Clone the repository
git clone https://github.com/yourusername/indoxRouter_server.git
cd indoxRouter_server
```

### 2.2 Create Production .env File

Create a `.env` file with production settings by using the provided `.env.example` as a template:

```bash
# Copy the example file
cp .env.example .env

# Edit the .env file with your specific settings
nano .env
```

Make sure to update the following values in your `.env` file:

```
# Security settings
SECRET_KEY=your-secure-random-secret-key  # Change this to a random secure string

# CORS settings
CORS_ORIGINS=["https://yourdomain.com", "http://91.107.253.133"]  # Add your website domain

# External website database settings
DATABASE_URL=postgresql://dbuser:securepassword@your-website-db-host:5432/your_website_db  # Update with your actual database credentials

# Provider API keys
OPENAI_API_KEY=your-openai-api-key  # Add your actual API keys
ANTHROPIC_API_KEY=your-anthropic-api-key
COHERE_API_KEY=your-cohere-api-key
GOOGLE_API_KEY=your-google-api-key
MISTRAL_API_KEY=your-mistral-api-key
```

### 2.3 Install Docker and Docker Compose (if not already installed)

```bash
# Update package lists
apt-get update

# Install required packages
apt-get install -y apt-transport-https ca-certificates curl software-properties-common

# Add Docker's official GPG key
curl -fsSL https://download.docker.com/linux/debian/gpg | apt-key add -

# Add Docker repository (adjust for your Linux distribution if needed)
add-apt-repository "deb [arch=amd64] https://download.docker.com/linux/debian $(lsb_release -cs) stable"

# Update package lists again
apt-get update

# Install Docker
apt-get install -y docker-ce docker-ce-cli containerd.io

# Install Docker Compose
curl -L "https://github.com/docker/compose/releases/download/v2.20.3/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
chmod +x /usr/local/bin/docker-compose

# Verify installations
docker --version
docker-compose --version
```

### 2.4 Create Docker Compose File

Create or update the `docker-compose.yml` file:

```bash
cat > docker-compose.yml << 'EOL'
version: "3"

services:
  indoxrouter-server:
    build: .
    container_name: indoxrouter-server
    restart: unless-stopped
    ports:
      - "8000:8000"
    environment:
      - HOST=0.0.0.0
      - PORT=8000
    volumes:
      - ./.env:/app/.env
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 5s
EOL
```

## Step 3: Deploy the Server

### 3.1 Build and Start the Server

```bash
# Build and start the server
docker-compose up -d

# Check the logs
docker-compose logs -f
```

### 3.2 Verify the Deployment

```bash
# Test the health check endpoint
curl http://91.107.253.133:8000/

# Expected response:
# {"status":"ok","message":"IndoxRouter Server is running"}
```

## Step 4: Configure the Client

Update the `constants.py` file in your IndoxRouter client to point to your production server:

```python
# API settings
DEFAULT_API_VERSION = "v1"
DEFAULT_BASE_URL = "http://91.107.253.133:8000"  # Your server IP
DEFAULT_TIMEOUT = 60
```

## Step 5: Secure Your Deployment (Optional but Recommended)

### 5.1 Set Up HTTPS with Nginx

```bash
# Install Nginx
apt-get update
apt-get install -y nginx certbot python3-certbot-nginx

# Create Nginx configuration
cat > /etc/nginx/sites-available/indoxrouter << 'EOL'
server {
    listen 80;
    listen [::]:80;
    server_name 91.107.253.133;  # Replace with your domain if available

    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
EOL

# Enable the site
ln -s /etc/nginx/sites-available/indoxrouter /etc/nginx/sites-enabled/
nginx -t
systemctl restart nginx

# If you have a domain, set up HTTPS
# certbot --nginx -d yourdomain.com
```

### 5.2 Set Up Firewall

```bash
# Install UFW if not already installed
apt-get install -y ufw

# Allow only necessary ports
ufw allow ssh
ufw allow http
ufw allow https
ufw enable
```

## Step 6: Monitoring and Maintenance

### 6.1 Set Up Basic Monitoring

```bash
# Install monitoring tools
apt-get install -y htop glances

# Monitor logs
docker-compose logs -f

# Monitor system resources
htop
```

### 6.2 Set Up Automatic Updates

```bash
# Create update script
cat > /usr/local/bin/update-indoxrouter.sh << 'EOL'
#!/bin/bash
cd /root/indoxRouter_server
git pull
docker-compose down
docker-compose build
docker-compose up -d
EOL

chmod +x /usr/local/bin/update-indoxrouter.sh

# Set up cron job for weekly updates (optional)
# crontab -e
# Add: 0 2 * * 0 /usr/local/bin/update-indoxrouter.sh >> /var/log/indoxrouter-update.log 2>&1
```

## Troubleshooting

### Database Connection Issues

If you encounter database connection issues:

1. Check if the website database is accessible from the IndoxRouter server:

   ```bash
   apt-get install -y iputils-ping
   docker exec -it indoxrouter-server ping your-website-db-host
   ```

2. Verify the database connection string in `.env`

3. Make sure the database user has appropriate permissions:
   ```sql
   GRANT SELECT ON users, api_keys TO dbuser;
   ```

### Server Not Starting

If the server doesn't start:

1. Check the server logs:

   ```bash
   docker-compose logs
   ```

2. Verify all required environment variables are set in `.env`

## Additional Resources

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Docker Documentation](https://docs.docker.com/)
- [PostgreSQL Documentation](https://www.postgresql.org/docs/)
