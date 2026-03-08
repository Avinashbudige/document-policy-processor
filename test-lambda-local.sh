#!/bin/bash

# Local Lambda Testing Script
# Tests the Lambda function locally using Docker before deploying to AWS

set -e

echo "=========================================="
echo "Local Lambda Testing"
echo "=========================================="

# Configuration
IMAGE_NAME="document-policy-processor"
IMAGE_TAG="test"
CONTAINER_NAME="lambda-test"
PORT=9000

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "ERROR: Docker is not running. Please start Docker and try again."
    exit 1
fi

# Step 1: Build the Docker image
echo ""
echo "Step 1: Building Docker image..."
docker build -t $IMAGE_NAME:$IMAGE_TAG .

# Step 2: Stop and remove existing container if running
echo ""
echo "Step 2: Cleaning up existing containers..."
docker stop $CONTAINER_NAME 2>/dev/null || true
docker rm $CONTAINER_NAME 2>/dev/null || true

# Step 3: Run the container
echo ""
echo "Step 3: Starting Lambda container..."
echo "Container will listen on http://localhost:$PORT"

# Check if AWS credentials are available
if [ -z "$AWS_ACCESS_KEY_ID" ] || [ -z "$AWS_SECRET_ACCESS_KEY" ]; then
    echo "WARNING: AWS credentials not found in environment variables."
    echo "The Lambda function will not be able to access AWS services."
    echo "Set AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY before running this script."
fi

# Check if OpenAI API key is available
if [ -z "$OPENAI_API_KEY" ]; then
    echo "WARNING: OPENAI_API_KEY not found in environment variables."
    echo "The Lambda function will not be able to use LLM features."
fi

docker run -d \
    --name $CONTAINER_NAME \
    -p $PORT:8080 \
    -e AWS_ACCESS_KEY_ID="${AWS_ACCESS_KEY_ID}" \
    -e AWS_SECRET_ACCESS_KEY="${AWS_SECRET_ACCESS_KEY}" \
    -e AWS_SESSION_TOKEN="${AWS_SESSION_TOKEN}" \
    -e AWS_REGION="${AWS_REGION:-us-east-1}" \
    -e S3_BUCKET_NAME="${S3_BUCKET_NAME:-document-policy-processor-uploads}" \
    -e DYNAMODB_TABLE_JOBS="${DYNAMODB_TABLE_JOBS:-ProcessingJobs}" \
    -e EMBEDDING_MODEL="${EMBEDDING_MODEL:-all-MiniLM-L6-v2}" \
    -e LLM_MODEL="${LLM_MODEL:-gpt-3.5-turbo}" \
    -e OPENAI_API_KEY="${OPENAI_API_KEY}" \
    $IMAGE_NAME:$IMAGE_TAG

echo "Container started successfully!"

# Wait for container to be ready
echo ""
echo "Waiting for Lambda runtime to initialize..."
sleep 5

# Step 4: Test the function
echo ""
echo "Step 4: Testing Lambda function..."
echo "Sending test event from test-event.json..."

if [ ! -f "test-event.json" ]; then
    echo "ERROR: test-event.json not found. Creating a sample test event..."
    cat > test-event.json << 'EOF'
{
  "body": {
    "job_id": "test-job-12345",
    "document_url": "s3://document-policy-processor-uploads/documents/sample-policy.pdf",
    "symptoms": "Experiencing chest pain and shortness of breath for the past week"
  }
}
EOF
fi

# Invoke the function
RESPONSE=$(curl -s -XPOST "http://localhost:$PORT/2015-03-31/functions/function/invocations" \
    -d @test-event.json)

echo ""
echo "=========================================="
echo "Lambda Response:"
echo "=========================================="
echo "$RESPONSE" | python3 -m json.tool 2>/dev/null || echo "$RESPONSE"

# Step 5: Show container logs
echo ""
echo "=========================================="
echo "Container Logs:"
echo "=========================================="
docker logs $CONTAINER_NAME

# Step 6: Cleanup prompt
echo ""
echo "=========================================="
echo "Testing Complete!"
echo "=========================================="
echo ""
echo "Container is still running. To view logs:"
echo "  docker logs -f $CONTAINER_NAME"
echo ""
echo "To stop and remove the container:"
echo "  docker stop $CONTAINER_NAME && docker rm $CONTAINER_NAME"
echo ""
echo "Or run: ./cleanup-test.sh"
echo "=========================================="
