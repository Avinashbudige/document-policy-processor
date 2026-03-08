#!/bin/bash

# Deploy IAM roles for Document Policy Processor
# This script can use either CloudFormation or Python boto3

set -e

echo "=========================================="
echo "Document Policy Processor - IAM Setup"
echo "=========================================="
echo ""

# Configuration
STACK_NAME="document-policy-processor-iam"
TEMPLATE_FILE="iam-roles.yaml"
ENVIRONMENT="dev"
S3_BUCKET_NAME="document-policy-processor-uploads"

# Check if AWS CLI is installed
if ! command -v aws &> /dev/null; then
    echo "❌ AWS CLI is not installed. Please install it first."
    echo "   Visit: https://aws.amazon.com/cli/"
    exit 1
fi

# Check AWS credentials
echo "🔍 Checking AWS credentials..."
if ! aws sts get-caller-identity &> /dev/null; then
    echo "❌ AWS credentials not configured. Please run 'aws configure'"
    exit 1
fi

ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
REGION=$(aws configure get region)
REGION=${REGION:-us-east-1}

echo "✅ AWS credentials configured"
echo "   Account: $ACCOUNT_ID"
echo "   Region: $REGION"
echo ""

# Ask user which method to use
echo "Choose deployment method:"
echo "  1) CloudFormation (recommended for production)"
echo "  2) Python script (faster, more flexible)"
echo ""
read -p "Enter choice (1 or 2): " choice

case $choice in
    1)
        echo ""
        echo "📦 Deploying IAM roles using CloudFormation..."
        echo ""
        
        # Check if stack exists
        if aws cloudformation describe-stacks --stack-name $STACK_NAME &> /dev/null; then
            echo "⚠️  Stack already exists. Updating..."
            aws cloudformation update-stack \
                --stack-name $STACK_NAME \
                --template-body file://$TEMPLATE_FILE \
                --parameters \
                    ParameterKey=Environment,ParameterValue=$ENVIRONMENT \
                    ParameterKey=S3BucketName,ParameterValue=$S3_BUCKET_NAME \
                --capabilities CAPABILITY_NAMED_IAM
            
            echo "⏳ Waiting for stack update to complete..."
            aws cloudformation wait stack-update-complete --stack-name $STACK_NAME
        else
            echo "📦 Creating new stack..."
            aws cloudformation create-stack \
                --stack-name $STACK_NAME \
                --template-body file://$TEMPLATE_FILE \
                --parameters \
                    ParameterKey=Environment,ParameterValue=$ENVIRONMENT \
                    ParameterKey=S3BucketName,ParameterValue=$S3_BUCKET_NAME \
                --capabilities CAPABILITY_NAMED_IAM
            
            echo "⏳ Waiting for stack creation to complete..."
            aws cloudformation wait stack-create-complete --stack-name $STACK_NAME
        fi
        
        echo ""
        echo "✅ CloudFormation deployment complete!"
        echo ""
        echo "📋 Stack Outputs:"
        aws cloudformation describe-stacks \
            --stack-name $STACK_NAME \
            --query 'Stacks[0].Outputs[*].[OutputKey,OutputValue]' \
            --output table
        ;;
    
    2)
        echo ""
        echo "🐍 Deploying IAM roles using Python script..."
        echo ""
        
        # Check if Python is installed
        if ! command -v python3 &> /dev/null; then
            echo "❌ Python 3 is not installed. Please install it first."
            exit 1
        fi
        
        # Check if boto3 is installed
        if ! python3 -c "import boto3" &> /dev/null; then
            echo "📦 Installing boto3..."
            pip3 install boto3
        fi
        
        # Run the Python setup script
        python3 setup_iam.py
        ;;
    
    *)
        echo "❌ Invalid choice. Please run the script again and choose 1 or 2."
        exit 1
        ;;
esac

echo ""
echo "=========================================="
echo "✅ IAM Setup Complete!"
echo "=========================================="
echo ""
echo "💡 Next Steps:"
echo "  1. Create Lambda functions using the Lambda execution role"
echo "  2. Configure API Gateway with the API Gateway role"
echo "  3. Test permissions by uploading a document"
echo ""
