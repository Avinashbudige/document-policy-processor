#!/bin/bash

# Lambda Deployment Script for Document Policy Processor
# This script builds and deploys the Lambda function as a container image

set -e  # Exit on error

# Configuration
AWS_REGION="${AWS_REGION:-us-east-1}"
AWS_ACCOUNT_ID="${AWS_ACCOUNT_ID:-$(aws sts get-caller-identity --query Account --output text)}"
ECR_REPOSITORY_NAME="document-policy-processor"
LAMBDA_FUNCTION_NAME="DocumentPolicyProcessor"
IMAGE_TAG="${IMAGE_TAG:-latest}"

echo "=========================================="
echo "Lambda Deployment Configuration"
echo "=========================================="
echo "AWS Region: $AWS_REGION"
echo "AWS Account ID: $AWS_ACCOUNT_ID"
echo "ECR Repository: $ECR_REPOSITORY_NAME"
echo "Lambda Function: $LAMBDA_FUNCTION_NAME"
echo "Image Tag: $IMAGE_TAG"
echo "=========================================="

# Step 1: Create ECR repository if it doesn't exist
echo ""
echo "Step 1: Creating ECR repository (if not exists)..."
aws ecr describe-repositories --repository-names $ECR_REPOSITORY_NAME --region $AWS_REGION 2>/dev/null || \
    aws ecr create-repository \
        --repository-name $ECR_REPOSITORY_NAME \
        --region $AWS_REGION \
        --image-scanning-configuration scanOnPush=true

ECR_URI="$AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com/$ECR_REPOSITORY_NAME"
echo "ECR URI: $ECR_URI"

# Step 2: Authenticate Docker to ECR
echo ""
echo "Step 2: Authenticating Docker to ECR..."
aws ecr get-login-password --region $AWS_REGION | \
    docker login --username AWS --password-stdin $ECR_URI

# Step 3: Build Docker image
echo ""
echo "Step 3: Building Docker image..."
docker build -t $ECR_REPOSITORY_NAME:$IMAGE_TAG .

# Step 4: Tag image for ECR
echo ""
echo "Step 4: Tagging image for ECR..."
docker tag $ECR_REPOSITORY_NAME:$IMAGE_TAG $ECR_URI:$IMAGE_TAG

# Step 5: Push image to ECR
echo ""
echo "Step 5: Pushing image to ECR..."
docker push $ECR_URI:$IMAGE_TAG

# Step 6: Update or create Lambda function
echo ""
echo "Step 6: Updating Lambda function..."

# Check if Lambda function exists
if aws lambda get-function --function-name $LAMBDA_FUNCTION_NAME --region $AWS_REGION 2>/dev/null; then
    echo "Updating existing Lambda function..."
    aws lambda update-function-code \
        --function-name $LAMBDA_FUNCTION_NAME \
        --image-uri $ECR_URI:$IMAGE_TAG \
        --region $AWS_REGION
    
    # Wait for update to complete
    echo "Waiting for Lambda update to complete..."
    aws lambda wait function-updated \
        --function-name $LAMBDA_FUNCTION_NAME \
        --region $AWS_REGION
else
    echo "Creating new Lambda function..."
    
    # Get the Lambda execution role ARN (assumes it was created by infrastructure setup)
    LAMBDA_ROLE_ARN=$(aws iam get-role --role-name DocumentPolicyProcessorLambdaRole --query 'Role.Arn' --output text 2>/dev/null)
    
    if [ -z "$LAMBDA_ROLE_ARN" ]; then
        echo "ERROR: Lambda execution role not found. Please run infrastructure setup first."
        exit 1
    fi
    
    aws lambda create-function \
        --function-name $LAMBDA_FUNCTION_NAME \
        --package-type Image \
        --code ImageUri=$ECR_URI:$IMAGE_TAG \
        --role $LAMBDA_ROLE_ARN \
        --timeout 300 \
        --memory-size 2048 \
        --environment Variables="{
            S3_BUCKET_NAME=document-policy-processor-uploads,
            DYNAMODB_TABLE_JOBS=ProcessingJobs,
            EMBEDDING_MODEL=all-MiniLM-L6-v2,
            LLM_MODEL=gpt-3.5-turbo
        }" \
        --region $AWS_REGION
    
    echo "Waiting for Lambda creation to complete..."
    aws lambda wait function-active \
        --function-name $LAMBDA_FUNCTION_NAME \
        --region $AWS_REGION
fi

echo ""
echo "=========================================="
echo "Deployment Complete!"
echo "=========================================="
echo "Lambda Function ARN:"
aws lambda get-function --function-name $LAMBDA_FUNCTION_NAME --region $AWS_REGION --query 'Configuration.FunctionArn' --output text
echo ""
echo "To test the function, run:"
echo "aws lambda invoke --function-name $LAMBDA_FUNCTION_NAME --payload file://test-event.json response.json"
echo "=========================================="
