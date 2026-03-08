#!/bin/bash

# Deploy to Streamlit Cloud - Setup Script
# This script prepares your repository for Streamlit Cloud deployment

set -e

echo "🚀 Streamlit Cloud Deployment Setup"
echo "===================================="
echo ""

# Check if we're in the right directory
if [ ! -f "app.py" ]; then
    echo "❌ Error: app.py not found. Please run this script from the frontend/ directory."
    exit 1
fi

# Check if Git is initialized
if [ ! -d "../.git" ]; then
    echo "📦 Initializing Git repository..."
    cd ..
    git init
    cd frontend
else
    echo "✅ Git repository already initialized"
fi

# Create .streamlit directory if it doesn't exist
if [ ! -d ".streamlit" ]; then
    echo "📁 Creating .streamlit directory..."
    mkdir -p .streamlit
fi

# Create secrets.toml.example if it doesn't exist
if [ ! -f ".streamlit/secrets.toml.example" ]; then
    echo "📝 Creating secrets.toml.example..."
    cat > .streamlit/secrets.toml.example << 'EOF'
# Streamlit Secrets Configuration
# Copy this file to secrets.toml and update with your values

API_BASE_URL = "https://your-api-gateway-url.amazonaws.com/prod"
EOF
fi

# Create .gitignore for secrets
if [ ! -f ".streamlit/.gitignore" ]; then
    echo "🔒 Creating .gitignore for secrets..."
    cat > .streamlit/.gitignore << 'EOF'
secrets.toml
EOF
fi

# Prompt for API Gateway URL
echo ""
echo "📋 Configuration"
echo "==============="
read -p "Enter your API Gateway URL (or press Enter to skip): " api_url

if [ ! -z "$api_url" ]; then
    echo "💾 Creating secrets.toml with your API URL..."
    cat > .streamlit/secrets.toml << EOF
API_BASE_URL = "$api_url"
EOF
    echo "✅ secrets.toml created"
else
    echo "⚠️  Skipped secrets.toml creation. You'll need to add this in Streamlit Cloud."
fi

# Check if requirements.txt exists
if [ ! -f "requirements.txt" ]; then
    echo "❌ Error: requirements.txt not found"
    exit 1
else
    echo "✅ requirements.txt found"
fi

# Commit changes
echo ""
echo "📦 Preparing Git commit..."
cd ..
git add frontend/
git add -A

if git diff-index --quiet HEAD --; then
    echo "✅ No changes to commit"
else
    git commit -m "Prepare frontend for Streamlit Cloud deployment"
    echo "✅ Changes committed"
fi

echo ""
echo "✅ Setup Complete!"
echo ""
echo "📋 Next Steps:"
echo "=============="
echo ""
echo "1. Push to GitHub:"
echo "   git remote add origin https://github.com/YOUR_USERNAME/document-policy-processor.git"
echo "   git branch -M main"
echo "   git push -u origin main"
echo ""
echo "2. Go to https://share.streamlit.io"
echo ""
echo "3. Click 'New app' and configure:"
echo "   - Repository: YOUR_USERNAME/document-policy-processor"
echo "   - Branch: main"
echo "   - Main file path: frontend/app.py"
echo "   - Python version: 3.11"
echo ""
echo "4. Add secrets in Streamlit Cloud:"
echo "   - Go to app settings → Secrets"
echo "   - Add: API_BASE_URL = \"$api_url\""
echo ""
echo "5. Click 'Deploy'!"
echo ""
echo "🎉 Your app will be live at:"
echo "   https://YOUR-USERNAME-document-policy-processor-frontend-app-HASH.streamlit.app"
echo ""
