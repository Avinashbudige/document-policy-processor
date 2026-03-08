#!/bin/bash

# API Gateway Deployment Script for Document Policy Processor
# This script deploys the API Gateway using AWS SAM

set -e  # Exit on error

echo "=========================================="
echo "API Gateway Deployment Script"
echo "Document Policy Processor"
echo "=========================================="
echo ""

# Check prerequisites
echo "Checking prerequisites..."

# Check AWS CLI
if ! command -v aws &> /dev/null; then
    echo "❌ AWS CLI not found. Please install it first."
    exit 1
fi
echo "✓ AWS CLI found"

# Check SAM CLI
if ! command -v sam &> /dev/null; then
    echo "❌ AWS SAM CLI not found. Please install it first."
    echo "   Install: pip install aws-sam-cli"
    exit 1
fi
echo "✓ SAM CLI found"

# Check AWS credentials
if ! aws sts get-caller-identity &> /dev/null; then
    echo "❌ AWS credentials not configured. Run 'aws configure' first."
    exit 1
fi
echo "✓ AWS credentials configured"

# Get AWS account info
AWS_ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
AWS_REGION=${AWS_REGION:-us-east-1}
echo "✓ AWS Account: $AWS_ACCOUNT_ID"
echo "✓ AWS Region: $AWS_REGION"
echo ""

# Check for OpenAI API key
if [ -z "$OPENAI_API_KEY" ]; then
    echo "⚠️  OPENAI_API_KEY environment variable not set"
    read -p "Enter your OpenAI API key: " OPENAI_API_KEY
    if [ -z "$OPENAI_API_KEY" ]; then
        echo "❌ OpenAI API key is required"
        exit 1
    fi
fi
echo "✓ OpenAI API key configured"
echo ""

# Set default parameters
S3_BUCKET_NAME=${S3_BUCKET_NAME:-document-policy-processor-uploads}
DYNAMODB_TABLE_JOBS=${DYNAMODB_TABLE_JOBS:-ProcessingJobs}
EMBEDDING_MODEL=${EMBEDDING_MODEL:-all-MiniLM-L6-v2}
LLM_MODEL=${LLM_MODEL:-gpt-3.5-turbo}
STACK_NAME=${STACK_NAME:-document-policy-processor}

echo "Deployment Configuration:"
echo "  Stack Name: $STACK_NAME"
echo "  S3 Bucket: $S3_BUCKET_NAME"
echo "  DynamoDB Table: $DYNAMODB_TABLE_JOBS"
echo "  Embedding Model: $EMBEDDING_MODEL"
echo "  LLM Model: $LLM_MODEL"
echo ""

# Ask for confirmation
read -p "Proceed with deployment? (y/n) " -n 1 -r
echo ""
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "Deployment cancelled"
    exit 0
fi

# Build SAM application
echo ""
echo "=========================================="
echo "Step 1: Building SAM Application"
echo "=========================================="
sam build

if [ $? -ne 0 ]; then
    echo "❌ SAM build failed"
    exit 1
fi
echo "✓ SAM build completed"

# Deploy SAM application
echo ""
echo "=========================================="
echo "Step 2: Deploying to AWS"
echo "=========================================="

# Check if samconfig.toml exists
if [ -f "samconfig.toml" ]; then
    echo "Using existing SAM configuration..."
    sam deploy \
        --parameter-overrides \
            "S3BucketName=$S3_BUCKET_NAME" \
            "DynamoDBTableJobs=$DYNAMODB_TABLE_JOBS" \
            "EmbeddingModel=$EMBEDDING_MODEL" \
            "LLMModel=$LLM_MODEL" \
            "OpenAIAPIKey=$OPENAI_API_KEY"
else
    echo "Running guided deployment (first time)..."
    sam deploy --guided \
        --parameter-overrides \
            "S3BucketName=$S3_BUCKET_NAME" \
            "DynamoDBTableJobs=$DYNAMODB_TABLE_JOBS" \
            "EmbeddingModel=$EMBEDDING_MODEL" \
            "LLMModel=$LLM_MODEL" \
            "OpenAIAPIKey=$OPENAI_API_KEY"
fi

if [ $? -ne 0 ]; then
    echo "❌ SAM deployment failed"
    exit 1
fi

# Get deployment outputs
echo ""
echo "=========================================="
echo "Step 3: Retrieving Deployment Information"
echo "=========================================="

# Get API endpoint
API_ENDPOINT=$(aws cloudformation describe-stacks \
    --stack-name $STACK_NAME \
    --query 'Stacks[0].Outputs[?OutputKey==`ApiEndpoint`].OutputValue' \
    --output text \
    --region $AWS_REGION)

# Get API Key ID
API_KEY_ID=$(aws cloudformation describe-stacks \
    --stack-name $STACK_NAME \
    --query 'Stacks[0].Outputs[?OutputKey==`ApiKey`].OutputValue' \
    --output text \
    --region $AWS_REGION)

# Get actual API key value
echo "Retrieving API key..."
API_KEY=$(aws apigateway get-api-key \
    --api-key $API_KEY_ID \
    --include-value \
    --query 'value' \
    --output text \
    --region $AWS_REGION)

# Display results
echo ""
echo "=========================================="
echo "Deployment Complete!"
echo "=========================================="
echo ""
echo "API Gateway Base URL:"
echo "  $API_ENDPOINT"
echo ""
echo "API Key:"
echo "  $API_KEY"
echo ""
echo "Endpoints:"
echo "  Health Check:      GET  $API_ENDPOINT/api/health (no auth)"
echo "  Upload URL:        POST $API_ENDPOINT/api/upload-url"
echo "  Process Document:  POST $API_ENDPOINT/api/process-document"
echo "  Job Status:        GET  $API_ENDPOINT/api/status/{jobId}"
echo "  Job Results:       GET  $API_ENDPOINT/api/results/{jobId}"
echo ""
echo "Authentication:"
echo "  Include header: X-Api-Key: $API_KEY"
echo ""

# Save to file
cat > API_DEPLOYMENT_INFO.txt << EOF
API Gateway Deployment Information
Generated: $(date)

API Gateway Base URL:
$API_ENDPOINT

API Key:
$API_KEY

Endpoints:
- Health Check:      GET  $API_ENDPOINT/api/health (no auth required)
- Upload URL:        POST $API_ENDPOINT/api/upload-url (auth required)
- Process Document:  POST $API_ENDPOINT/api/process-document (auth required)
- Job Status:        GET  $API_ENDPOINT/api/status/{jobId} (auth required)
- Job Results:       GET  $API_ENDPOINT/api/results/{jobId} (auth required)

Authentication:
Include header: X-Api-Key: $API_KEY

Rate Limits:
- 10 requests per second
- Burst: 20 requests
- Daily quota: 1000 requests

Example curl command:
curl -X GET "$API_ENDPOINT/api/health"

curl -X POST "$API_ENDPOINT/api/upload-url" \\
  -H "Content-Type: application/json" \\
  -H "X-Api-Key: $API_KEY" \\
  -d '{"filename":"test.pdf","file_type":"application/pdf"}'
EOF

echo "✓ Deployment information saved to: API_DEPLOYMENT_INFO.txt"
echo ""

# Test health endpoint
echo "=========================================="
echo "Step 4: Testing API Gateway"
echo "=========================================="
echo ""
echo "Testing health endpoint..."

HEALTH_RESPONSE=$(curl -s -w "\n%{http_code}" "$API_ENDPOINT/api/health")
HTTP_CODE=$(echo "$HEALTH_RESPONSE" | tail -n1)
RESPONSE_BODY=$(echo "$HEALTH_RESPONSE" | head -n-1)

if [ "$HTTP_CODE" = "200" ]; then
    echo "✓ Health check passed!"
    echo "  Response: $RESPONSE_BODY"
else
    echo "⚠️  Health check returned status: $HTTP_CODE"
    echo "  Response: $RESPONSE_BODY"
fi

echo ""
echo "=========================================="
echo "Next Steps"
echo "=========================================="
echo ""
echo "1. Test all endpoints:"
echo "   ./test-api-gateway.sh"
echo ""
echo "2. Update frontend configuration:"
echo "   - API Base URL: $API_ENDPOINT"
echo "   - API Key: $API_KEY"
echo ""
echo "3. View CloudWatch logs:"
echo "   aws logs tail /aws/lambda/DocumentPolicyProcessor --follow"
echo ""
echo "4. Monitor API Gateway:"
echo "   aws logs tail /aws/apigateway/$STACK_NAME/Prod --follow"
echo ""
echo "=========================================="
