#!/bin/bash

# Deployment script for Document Policy Processor Frontend

set -e

echo "=== Document Policy Processor Frontend Deployment ==="
echo ""

# Check if API_BASE_URL is provided
if [ -z "$1" ]; then
    echo "Usage: ./deploy.sh <API_GATEWAY_URL>"
    echo "Example: ./deploy.sh https://abc123.execute-api.us-east-1.amazonaws.com/prod"
    exit 1
fi

API_BASE_URL=$1

echo "Step 1: Creating .streamlit directory..."
mkdir -p .streamlit

echo "Step 2: Creating secrets.toml..."
cat > .streamlit/secrets.toml <<EOF
# Streamlit Secrets Configuration
API_BASE_URL = "$API_BASE_URL"
EOF

echo "Step 3: Installing dependencies..."
pip install -r requirements.txt

echo ""
echo "=== Deployment Complete ==="
echo ""
echo "To run the application locally:"
echo "  streamlit run app.py"
echo ""
echo "To deploy to Streamlit Cloud:"
echo "  1. Push code to GitHub"
echo "  2. Go to share.streamlit.io"
echo "  3. Connect your repository"
echo "  4. Add API_BASE_URL to Secrets"
echo "  5. Deploy!"
echo ""
