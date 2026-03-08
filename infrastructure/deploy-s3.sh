#!/bin/bash
# Deploy S3 bucket for Document Policy Processor

set -e  # Exit on error

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configuration
BUCKET_NAME="document-policy-processor-uploads"
REGION="${AWS_REGION:-us-east-1}"
STACK_NAME="document-policy-processor-s3"

echo "=========================================="
echo "Document Policy Processor - S3 Deployment"
echo "=========================================="
echo ""
echo "Bucket Name: $BUCKET_NAME"
echo "Region: $REGION"
echo "Stack Name: $STACK_NAME"
echo ""

# Check if AWS CLI is installed
if ! command -v aws &> /dev/null; then
    echo -e "${RED}✗ AWS CLI is not installed${NC}"
    echo "Please install AWS CLI: https://aws.amazon.com/cli/"
    exit 1
fi

# Check if AWS credentials are configured
if ! aws sts get-caller-identity &> /dev/null; then
    echo -e "${RED}✗ AWS credentials are not configured${NC}"
    echo "Please run: aws configure"
    exit 1
fi

echo -e "${GREEN}✓ AWS CLI configured${NC}"
echo ""

# Ask user for deployment method
echo "Choose deployment method:"
echo "1) CloudFormation (recommended)"
echo "2) Python script"
echo "3) Exit"
read -p "Enter choice [1-3]: " choice

case $choice in
    1)
        echo ""
        echo "Deploying with CloudFormation..."
        
        # Check if stack exists
        if aws cloudformation describe-stacks --stack-name $STACK_NAME --region $REGION &> /dev/null; then
            echo -e "${YELLOW}Stack already exists. Updating...${NC}"
            aws cloudformation update-stack \
                --stack-name $STACK_NAME \
                --template-body file://infrastructure/s3-bucket.yaml \
                --parameters ParameterKey=BucketName,ParameterValue=$BUCKET_NAME \
                             ParameterKey=Environment,ParameterValue=dev \
                --region $REGION
            
            echo "Waiting for stack update to complete..."
            aws cloudformation wait stack-update-complete \
                --stack-name $STACK_NAME \
                --region $REGION
        else
            echo "Creating new stack..."
            aws cloudformation create-stack \
                --stack-name $STACK_NAME \
                --template-body file://infrastructure/s3-bucket.yaml \
                --parameters ParameterKey=BucketName,ParameterValue=$BUCKET_NAME \
                             ParameterKey=Environment,ParameterValue=dev \
                --region $REGION
            
            echo "Waiting for stack creation to complete..."
            aws cloudformation wait stack-create-complete \
                --stack-name $STACK_NAME \
                --region $REGION
        fi
        
        echo ""
        echo -e "${GREEN}✓ CloudFormation deployment complete${NC}"
        echo ""
        echo "Stack Outputs:"
        aws cloudformation describe-stacks \
            --stack-name $STACK_NAME \
            --region $REGION \
            --query 'Stacks[0].Outputs[*].[OutputKey,OutputValue]' \
            --output table
        
        # Create folders
        echo ""
        echo "Creating folder structure..."
        aws s3api put-object --bucket $BUCKET_NAME --key documents/ --region $REGION
        aws s3api put-object --bucket $BUCKET_NAME --key embeddings/ --region $REGION
        aws s3api put-object --bucket $BUCKET_NAME --key results/ --region $REGION
        echo -e "${GREEN}✓ Folders created${NC}"
        ;;
        
    2)
        echo ""
        echo "Deploying with Python script..."
        
        # Check if Python is installed
        if ! command -v python3 &> /dev/null; then
            echo -e "${RED}✗ Python 3 is not installed${NC}"
            exit 1
        fi
        
        # Check if boto3 is installed
        if ! python3 -c "import boto3" &> /dev/null; then
            echo -e "${YELLOW}Installing boto3...${NC}"
            pip3 install boto3
        fi
        
        # Run the Python script
        python3 infrastructure/setup_s3.py
        ;;
        
    3)
        echo "Exiting..."
        exit 0
        ;;
        
    *)
        echo -e "${RED}Invalid choice${NC}"
        exit 1
        ;;
esac

echo ""
echo "=========================================="
echo -e "${GREEN}✓ Deployment Complete!${NC}"
echo "=========================================="
echo ""
echo "Bucket URL: https://$BUCKET_NAME.s3.$REGION.amazonaws.com"
echo "Console URL: https://s3.console.aws.amazon.com/s3/buckets/$BUCKET_NAME"
echo ""
echo "Next steps:"
echo "1. Set up DynamoDB tables (task 2.2)"
echo "2. Set up IAM roles (task 2.3)"
echo "3. Implement Lambda functions"
