#!/bin/bash

# Set up Nginx reverse proxy for Streamlit on EC2
# Run this script on your EC2 instance after deploying Streamlit

set -e

echo "🔧 Nginx Reverse Proxy Setup"
echo "============================"
echo ""

# Check if running as root
if [ "$EUID" -ne 0 ]; then 
    echo "⚠️  This script requires sudo privileges"
    echo "Re-running with sudo..."
    sudo "$0" "$@"
    exit $?
fi

# Check if Streamlit service is running
if ! systemctl is-active --quiet streamlit; then
    echo "❌ Error: Streamlit service is not running"
    echo "Start it with: sudo systemctl start streamlit"
    exit 1
fi

echo "✅ Streamlit service is running"

# Install Nginx
echo ""
echo "📦 Installing Nginx..."
yum install nginx -y

# Prompt for domain name
echo ""
read -p "Enter your domain name (or press Enter to use IP): " domain_name
if [ -z "$domain_name" ]; then
    # Get public IP
    domain_name=$(curl -s http://169.254.169.254/latest/meta-data/public-ipv4 || echo "localhost")
    echo "Using IP address: $domain_name"
fi

# Create Nginx configuration
echo "⚙️  Creating Nginx configuration..."
cat > /etc/nginx/conf.d/streamlit.conf << EOF
# Streamlit reverse proxy configuration
server {
    listen 80;
    server_name $domain_name;

    # Increase buffer sizes for Streamlit
    client_max_body_size 10M;
    proxy_buffering off;

    # Logging
    access_log /var/log/nginx/streamlit-access.log;
    error_log /var/log/nginx/streamlit-error.log;

    location / {
        proxy_pass http://localhost:8501;
        proxy_http_version 1.1;
        
        # WebSocket support
        proxy_set_header Upgrade \$http_upgrade;
        proxy_set_header Connection "upgrade";
        
        # Headers
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        
        # Timeouts
        proxy_read_timeout 86400;
        proxy_connect_timeout 86400;
        proxy_send_timeout 86400;
    }

    # Health check endpoint
    location /health {
        access_log off;
        return 200 "healthy\n";
        add_header Content-Type text/plain;
    }
}
EOF

echo "✅ Nginx configuration created"

# Test Nginx configuration
echo ""
echo "🧪 Testing Nginx configuration..."
if nginx -t; then
    echo "✅ Nginx configuration is valid"
else
    echo "❌ Error: Nginx configuration is invalid"
    exit 1
fi

# Enable and start Nginx
echo ""
echo "🚀 Starting Nginx..."
systemctl enable nginx
systemctl restart nginx

# Wait for Nginx to start
sleep 2

# Check Nginx status
if systemctl is-active --quiet nginx; then
    echo "✅ Nginx is running"
else
    echo "❌ Error: Nginx failed to start"
    echo "Check logs with: sudo journalctl -u nginx -n 50"
    exit 1
fi

# Get public IP
PUBLIC_IP=$(curl -s http://169.254.169.254/latest/meta-data/public-ipv4 || echo "UNKNOWN")

echo ""
echo "✅ Nginx Setup Complete!"
echo ""
echo "📋 Service Information:"
echo "======================"
echo "Nginx Status: $(systemctl is-active nginx)"
echo "Streamlit Status: $(systemctl is-active streamlit)"
echo "Domain/IP: $domain_name"
echo "Public IP: $PUBLIC_IP"
echo ""
echo "🌐 Access your application at:"
echo "   http://$domain_name"
if [ "$domain_name" != "$PUBLIC_IP" ]; then
    echo "   http://$PUBLIC_IP"
fi
echo ""
echo "📝 Useful Commands:"
echo "=================="
echo "Check Nginx status:  sudo systemctl status nginx"
echo "View Nginx logs:     sudo tail -f /var/log/nginx/streamlit-error.log"
echo "Restart Nginx:       sudo systemctl restart nginx"
echo "Test config:         sudo nginx -t"
echo ""

# Prompt for SSL setup
echo "🔒 SSL/HTTPS Setup"
echo "=================="
read -p "Do you want to set up SSL with Let's Encrypt? (y/n): " setup_ssl

if [ "$setup_ssl" = "y" ]; then
    if [ "$domain_name" = "$PUBLIC_IP" ] || [ "$domain_name" = "localhost" ]; then
        echo "❌ Error: SSL requires a domain name, not an IP address"
        echo "Set up a domain first, then run: sudo certbot --nginx -d yourdomain.com"
        exit 0
    fi
    
    echo ""
    echo "📦 Installing Certbot..."
    yum install certbot python3-certbot-nginx -y
    
    echo ""
    echo "🔐 Obtaining SSL certificate..."
    read -p "Enter your email address for Let's Encrypt: " email
    
    if [ -z "$email" ]; then
        echo "❌ Error: Email is required for Let's Encrypt"
        exit 1
    fi
    
    certbot --nginx -d "$domain_name" --non-interactive --agree-tos --email "$email"
    
    if [ $? -eq 0 ]; then
        echo "✅ SSL certificate installed successfully"
        echo ""
        echo "🌐 Your application is now accessible at:"
        echo "   https://$domain_name"
        echo ""
        echo "🔄 Auto-renewal is configured"
        echo "Test renewal with: sudo certbot renew --dry-run"
    else
        echo "❌ Error: SSL certificate installation failed"
        echo "You can try again manually with: sudo certbot --nginx -d $domain_name"
    fi
else
    echo ""
    echo "⚠️  SSL not configured. Your site is accessible via HTTP only."
    echo "To set up SSL later, run: sudo certbot --nginx -d $domain_name"
fi

echo ""
echo "⚠️  Security Reminder:"
echo "===================="
echo "Ensure your EC2 security group allows:"
echo "  - Port 80 (HTTP) from 0.0.0.0/0"
if [ "$setup_ssl" = "y" ]; then
    echo "  - Port 443 (HTTPS) from 0.0.0.0/0"
fi
echo ""
