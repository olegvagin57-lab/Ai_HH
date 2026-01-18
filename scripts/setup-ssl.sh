#!/bin/bash
# SSL Certificate Setup Script
# This script helps set up SSL certificates for production using Let's Encrypt

set -e

DOMAIN="${1:-yourdomain.com}"
EMAIL="${2:-admin@yourdomain.com}"

echo "Setting up SSL certificates for domain: $DOMAIN"
echo "Email: $EMAIL"

# Check if certbot is installed
if ! command -v certbot &> /dev/null; then
    echo "Certbot is not installed. Installing..."
    if [[ "$OSTYPE" == "linux-gnu"* ]]; then
        sudo apt-get update
        sudo apt-get install -y certbot
    elif [[ "$OSTYPE" == "darwin"* ]]; then
        brew install certbot
    else
        echo "Please install certbot manually for your OS"
        exit 1
    fi
fi

# Create directories
mkdir -p nginx/ssl
mkdir -p nginx/logs

# Generate certificates using certbot
echo "Generating SSL certificates..."
sudo certbot certonly --standalone \
    --preferred-challenges http \
    -d "$DOMAIN" \
    -d "www.$DOMAIN" \
    --email "$EMAIL" \
    --agree-tos \
    --non-interactive

# Copy certificates to nginx/ssl directory
echo "Copying certificates..."
sudo cp /etc/letsencrypt/live/$DOMAIN/fullchain.pem nginx/ssl/fullchain.pem
sudo cp /etc/letsencrypt/live/$DOMAIN/privkey.pem nginx/ssl/privkey.pem
sudo cp /etc/letsencrypt/live/$DOMAIN/chain.pem nginx/ssl/chain.pem

# Set proper permissions
sudo chown $USER:$USER nginx/ssl/*.pem
chmod 600 nginx/ssl/privkey.pem
chmod 644 nginx/ssl/fullchain.pem
chmod 644 nginx/ssl/chain.pem

echo "SSL certificates have been set up successfully!"
echo ""
echo "Next steps:"
echo "1. Update nginx/nginx.prod.conf with your domain name"
echo "2. Update docker-compose.prod.yml with your domain name"
echo "3. Set up automatic renewal: sudo certbot renew --dry-run"
echo ""
echo "To renew certificates manually: sudo certbot renew"
