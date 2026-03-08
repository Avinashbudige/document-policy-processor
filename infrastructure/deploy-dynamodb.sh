#!/bin/bash
# DynamoDB Deployment Script for Unix/Linux/Mac
# Deploys DynamoDB tables for Document Policy Processor

set -e

echo "=========================================="
echo "DynamoDB Deployment Script"
echo "=========================================="
echo ""

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "Error: Python 3 is not installed"
    echo "Please install Python 3 and try again"
    exit 1
fi

# Check if AWS CLI is installed
if ! command -v aws &> /dev/null; then
    echo "Error: AWS CLI is not installed"
    echo "Please install AWS CLI and configure it with 'aws configure'"
    exit 1
fi

# Check if AWS credentials are configured
if ! aws sts get-caller-identity &> /dev/null; then
    echo "Error: AWS credentials are not configured"
    echo "Please run 'aws configure' to set up your credentials"
    exit 1
fi

echo "✓ Prerequisites check passed"
echo ""

# Install required Python packages
echo "Installing required Python packages..."
pip3 install boto3 --quiet
echo "✓ Dependencies installed"
echo ""

# Run the setup script
echo "Running DynamoDB setup..."
python3 setup_dynamodb.py

echo ""
echo "=========================================="
echo "Deployment Complete!"
echo "=========================================="
