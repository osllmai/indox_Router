#!/bin/bash

# IndoxRouter Server - Nginx & SSL Setup Script

# Check if domain name was provided
if [ -z "$1" ]; then
  echo "Error: No domain name provided"
  echo "Usage: bash setup_nginx.sh yourdomain.com"
  exit 1
fi

DOMAIN=$1

echo "Setting up Nginx and SSL for $DOMAIN"
echo "==================================="

# Check if running as root
if [ "$EUID" -ne 0 ]; then
  echo "Please run as root"
  exit 1
fi

# Install Nginx and Certbot
echo "Installing Nginx and Certbot..."
apt-get update
apt-get install -y nginx certbot python3-certbot-nginx

# Create Nginx configuration
echo "Creating Nginx configuration..."
cat > /etc/nginx/sites-available/indoxrouter << EOF
server {
    listen 80;
    server_name $DOMAIN;

    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        
        # WebSocket support
        proxy_http_version 1.1;
        proxy_set_header Upgrade \$http_upgrade;
        proxy_set_header Connection "upgrade";
    }
    
    # Larger file uploads
    client_max_body_size 10M;
    
    # Security headers
    add_header X-Content-Type-Options nosniff;
    add_header X-XSS-Protection "1; mode=block";
    add_header X-Frame-Options SAMEORIGIN;
}
EOF

# Enable the site
echo "Enabling the site..."
ln -sf /etc/nginx/sites-available/indoxrouter /etc/nginx/sites-enabled/

# Test Nginx configuration
echo "Testing Nginx configuration..."
nginx -t

if [ $? -ne 0 ]; then
  echo "Nginx configuration test failed. Please check the configuration."
  exit 1
fi

# Restart Nginx
echo "Restarting Nginx..."
systemctl restart nginx

# Obtain SSL certificate
echo "Obtaining SSL certificate with Let's Encrypt..."
certbot --nginx -d $DOMAIN --non-interactive --agree-tos --email admin@$DOMAIN

if [ $? -ne 0 ]; then
  echo "Failed to obtain SSL certificate. Please check the error message."
  exit 1
fi

# Final steps
echo ""
echo "Nginx and SSL setup complete!"
echo "============================"
echo ""
echo "Your IndoxRouter server is now accessible at:"
echo "https://$DOMAIN"
echo ""
echo "SSL certificates will auto-renew via Certbot"
echo ""
echo "To check Nginx status: systemctl status nginx"
echo "To view Nginx logs: tail -f /var/log/nginx/error.log"
echo "" 