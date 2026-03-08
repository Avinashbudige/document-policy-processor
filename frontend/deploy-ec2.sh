#!/bin/bash

# Deploy to AWS EC2 - Automated Deployment Script
# Run this script ON your EC2 instance after SSH connection

set -e

echo "🚀 AWS EC2 Deployment Script"
echo "============================"
echo ""

# Check if running on EC2
if [ ! -f /sys/hypervisor/uuid ] || ! grep -q ec2 /sys/hypervisor/uuid 2>/dev/null; then
    echo "⚠️  Warning: This doesn't appear to be an EC2 instance"
    read -p "Continue anyway? (y/n): " continue
    if [ "$continue" != "y" ]; then
        exit 1
    fi
fi

# Update system
echo "📦 Updating system packages..."
sudo yum update -y

# Install Python 3.11
echo "🐍 Installing Python 3.11..."
sudo yum install python3.11 python3.11-pip -y

# Install Git
echo "📚 Installing Git..."
sudo yum install git -y

# Prompt for repository URL
echo ""
read -p "Enter your GitHub repository URL: " repo_url
if [ -z "$repo_url" ]; then
    echo "❌ Error: Repository URL is required"
    exit 1
fi

# Clone repository
echo "📥 Cloning repository..."
cd ~
if [ -d "document-policy-processor" ]; then
    echo "⚠️  Directory already exists. Pulling latest changes..."
    cd document-policy-processor
    git pull
else
    git clone "$repo_url"
    cd document-policy-processor
fi

cd frontend

# Create virtual environment
echo "🔧 Creating virtual environment..."
python3.11 -m venv venv
source venv/bin/activate

# Install dependencies
echo "📦 Installing Python dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# Configure secrets
echo ""
echo "📋 Configuration"
echo "==============="
read -p "Enter your API Gateway URL: " api_url
if [ -z "$api_url" ]; then
    echo "❌ Error: API Gateway URL is required"
    exit 1
fi

mkdir -p .streamlit
cat > .streamlit/secrets.toml << EOF
API_BASE_URL = "$api_url"
EOF

echo "✅ Configuration saved"

# Test run
echo ""
echo "🧪 Testing Streamlit..."
timeout 10 streamlit run app.py --server.port 8501 --server.address 0.0.0.0 || true

# Create systemd service
echo ""
echo "⚙️  Creating systemd service..."
sudo tee /etc/systemd/system/streamlit.service > /dev/null << EOF
[Unit]
Description=Streamlit Document Policy Processor
After=network.target

[Service]
Type=simple
User=$USER
WorkingDirectory=$HOME/document-policy-processor/frontend
Environment="PATH=$HOME/document-policy-processor/frontend/venv/bin"
ExecStart=$HOME/document-policy-processor/frontend/venv/bin/streamlit run app.py --server.port 8501 --server.address 0.0.0.0
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

# Enable and start service
echo "🚀 Starting Streamlit service..."
sudo systemctl daemon-reload
sudo systemctl enable streamlit
sudo systemctl start streamlit

# Wait for service to start
sleep 5

# Check service status
if sudo systemctl is-active --quiet streamlit; then
    echo "✅ Streamlit service is running"
else
    echo "❌ Error: Streamlit service failed to start"
    echo "Check logs with: sudo journalctl -u streamlit -n 50"
    exit 1
fi

# Get public IP
PUBLIC_IP=$(curl -s http://169.254.169.254/latest/meta-data/public-ipv4 || echo "UNKNOWN")

echo ""
echo "✅ Deployment Complete!"
echo ""
echo "📋 Service Information:"
echo "======================"
echo "Status: $(sudo systemctl is-active streamlit)"
echo "Public IP: $PUBLIC_IP"
echo "Port: 8501"
echo ""
echo "🌐 Access your application at:"
echo "   http://$PUBLIC_IP:8501"
echo ""
echo "📝 Useful Commands:"
echo "=================="
echo "Check status:  sudo systemctl status streamlit"
echo "View logs:     sudo journalctl -u streamlit -f"
echo "Restart:       sudo systemctl restart streamlit"
echo "Stop:          sudo systemctl stop streamlit"
echo ""
echo "⚠️  Security Note:"
echo "================="
echo "Ensure your EC2 security group allows inbound traffic on port 8501"
echo ""
echo "🔒 Optional: Set up Nginx reverse proxy for production"
echo "Run: ./setup-nginx.sh"
echo ""
