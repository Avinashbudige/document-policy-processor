#!/bin/bash

# Lambda Deployment Verification Script
# This script verifies that the Lambda function is properly deployed and configured

set -e

# Configuration
LAMBDA_FUNCTION_NAME="${LAMBDA_FUNCTION_NAME:-DocumentPolicyProcessor}"
AWS_REGION="${AWS_REGION:-us-east-1}"

echo "=========================================="
echo "Lambda Deployment Verification"
echo "=========================================="
echo "Function Name: $LAMBDA_FUNCTION_NAME"
echo "AWS Region: $AWS_REGION"
echo "=========================================="
echo ""

# Color codes for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Test counter
TESTS_PASSED=0
TESTS_FAILED=0

# Function to print test result
print_result() {
    if [ $1 -eq 0 ]; then
        echo -e "${GREEN}✓ PASS${NC}: $2"
        ((TESTS_PASSED++))
    else
        echo -e "${RED}✗ FAIL${NC}: $2"
        ((TESTS_FAILED++))
    fi
}

# Test 1: Check if Lambda function exists
echo "Test 1: Checking if Lambda function exists..."
if aws lambda get-function --function-name $LAMBDA_FUNCTION_NAME --region $AWS_REGION &>/dev/null; then
    print_result 0 "Lambda function exists"
else
    print_result 1 "Lambda function not found"
    echo "Please deploy the Lambda function first using deploy-lambda.sh"
    exit 1
fi
echo ""

# Test 2: Check Lambda configuration
echo "Test 2: Checking Lambda configuration..."
CONFIG=$(aws lambda get-function-configuration --function-name $LAMBDA_FUNCTION_NAME --region $AWS_REGION)

# Check memory size
MEMORY_SIZE=$(echo $CONFIG | jq -r '.MemorySize')
if [ "$MEMORY_SIZE" -eq 2048 ]; then
    print_result 0 "Memory size is 2048 MB"
else
    print_result 1 "Memory size is $MEMORY_SIZE MB (expected 2048 MB)"
fi

# Check timeout
TIMEOUT=$(echo $CONFIG | jq -r '.Timeout')
if [ "$TIMEOUT" -eq 300 ]; then
    print_result 0 "Timeout is 300 seconds"
else
    print_result 1 "Timeout is $TIMEOUT seconds (expected 300 seconds)"
fi

# Check package type
PACKAGE_TYPE=$(echo $CONFIG | jq -r '.PackageType')
if [ "$PACKAGE_TYPE" = "Image" ]; then
    print_result 0 "Package type is Image"
else
    print_result 1 "Package type is $PACKAGE_TYPE (expected Image)"
fi

# Check state
STATE=$(echo $CONFIG | jq -r '.State')
if [ "$STATE" = "Active" ]; then
    print_result 0 "Function state is Active"
else
    print_result 1 "Function state is $STATE (expected Active)"
fi
echo ""

# Test 3: Check environment variables
echo "Test 3: Checking environment variables..."
ENV_VARS=$(echo $CONFIG | jq -r '.Environment.Variables')

# Check S3_BUCKET_NAME
if echo $ENV_VARS | jq -e '.S3_BUCKET_NAME' &>/dev/null; then
    S3_BUCKET=$(echo $ENV_VARS | jq -r '.S3_BUCKET_NAME')
    print_result 0 "S3_BUCKET_NAME is set: $S3_BUCKET"
else
    print_result 1 "S3_BUCKET_NAME is not set"
fi

# Check DYNAMODB_TABLE_JOBS
if echo $ENV_VARS | jq -e '.DYNAMODB_TABLE_JOBS' &>/dev/null; then
    DYNAMODB_TABLE=$(echo $ENV_VARS | jq -r '.DYNAMODB_TABLE_JOBS')
    print_result 0 "DYNAMODB_TABLE_JOBS is set: $DYNAMODB_TABLE"
else
    print_result 1 "DYNAMODB_TABLE_JOBS is not set"
fi

# Check EMBEDDING_MODEL
if echo $ENV_VARS | jq -e '.EMBEDDING_MODEL' &>/dev/null; then
    EMBEDDING_MODEL=$(echo $ENV_VARS | jq -r '.EMBEDDING_MODEL')
    print_result 0 "EMBEDDING_MODEL is set: $EMBEDDING_MODEL"
else
    print_result 1 "EMBEDDING_MODEL is not set"
fi

# Check LLM_MODEL
if echo $ENV_VARS | jq -e '.LLM_MODEL' &>/dev/null; then
    LLM_MODEL=$(echo $ENV_VARS | jq -r '.LLM_MODEL')
    print_result 0 "LLM_MODEL is set: $LLM_MODEL"
else
    print_result 1 "LLM_MODEL is not set"
fi

# Check OPENAI_API_KEY
if echo $ENV_VARS | jq -e '.OPENAI_API_KEY' &>/dev/null; then
    print_result 0 "OPENAI_API_KEY is set"
else
    print_result 1 "OPENAI_API_KEY is not set"
fi
echo ""

# Test 4: Test health check endpoint
echo "Test 4: Testing health check endpoint..."
cat > /tmp/test-health-check.json << 'EOF'
{
  "httpMethod": "GET",
  "path": "/api/health",
  "headers": {},
  "queryStringParameters": null,
  "body": null
}
EOF

if aws lambda invoke \
    --function-name $LAMBDA_FUNCTION_NAME \
    --payload file:///tmp/test-health-check.json \
    --region $AWS_REGION \
    /tmp/response-health.json &>/dev/null; then
    
    STATUS_CODE=$(cat /tmp/response-health.json | jq -r '.statusCode')
    if [ "$STATUS_CODE" -eq 200 ]; then
        print_result 0 "Health check endpoint returns 200"
        
        # Check response body
        BODY=$(cat /tmp/response-health.json | jq -r '.body' | jq -r '.status')
        if [ "$BODY" = "healthy" ]; then
            print_result 0 "Health check status is 'healthy'"
        else
            print_result 1 "Health check status is '$BODY' (expected 'healthy')"
        fi
    else
        print_result 1 "Health check endpoint returns $STATUS_CODE (expected 200)"
    fi
else
    print_result 1 "Failed to invoke health check endpoint"
fi
echo ""

# Test 5: Test upload URL generation
echo "Test 5: Testing upload URL generation..."
cat > /tmp/test-upload-url.json << 'EOF'
{
  "httpMethod": "POST",
  "path": "/api/upload-url",
  "headers": {
    "Content-Type": "application/json"
  },
  "body": "{\"filename\":\"test-document.pdf\",\"file_type\":\"application/pdf\"}"
}
EOF

if aws lambda invoke \
    --function-name $LAMBDA_FUNCTION_NAME \
    --payload file:///tmp/test-upload-url.json \
    --region $AWS_REGION \
    /tmp/response-upload.json &>/dev/null; then
    
    STATUS_CODE=$(cat /tmp/response-upload.json | jq -r '.statusCode')
    if [ "$STATUS_CODE" -eq 200 ]; then
        print_result 0 "Upload URL generation returns 200"
        
        # Check if upload_url is present
        BODY=$(cat /tmp/response-upload.json | jq -r '.body')
        if echo $BODY | jq -e '.upload_url' &>/dev/null; then
            print_result 0 "Upload URL is generated"
        else
            print_result 1 "Upload URL is not present in response"
        fi
    else
        print_result 1 "Upload URL generation returns $STATUS_CODE (expected 200)"
    fi
else
    print_result 1 "Failed to invoke upload URL generation endpoint"
fi
echo ""

# Test 6: Check IAM role permissions
echo "Test 6: Checking IAM role permissions..."
ROLE_ARN=$(echo $CONFIG | jq -r '.Role')
ROLE_NAME=$(echo $ROLE_ARN | awk -F'/' '{print $NF}')

if aws iam get-role --role-name $ROLE_NAME &>/dev/null; then
    print_result 0 "IAM role exists: $ROLE_NAME"
    
    # Check attached policies
    POLICIES=$(aws iam list-attached-role-policies --role-name $ROLE_NAME --query 'AttachedPolicies[*].PolicyName' --output text)
    if [ -n "$POLICIES" ]; then
        print_result 0 "IAM role has attached policies"
    else
        print_result 1 "IAM role has no attached policies"
    fi
else
    print_result 1 "IAM role not found: $ROLE_NAME"
fi
echo ""

# Test 7: Check CloudWatch log group
echo "Test 7: Checking CloudWatch log group..."
LOG_GROUP="/aws/lambda/$LAMBDA_FUNCTION_NAME"
if aws logs describe-log-groups --log-group-name-prefix $LOG_GROUP --region $AWS_REGION | jq -e '.logGroups[] | select(.logGroupName == "'$LOG_GROUP'")' &>/dev/null; then
    print_result 0 "CloudWatch log group exists"
    
    # Check if there are recent log streams
    RECENT_STREAMS=$(aws logs describe-log-streams \
        --log-group-name $LOG_GROUP \
        --order-by LastEventTime \
        --descending \
        --max-items 1 \
        --region $AWS_REGION \
        --query 'logStreams[0].logStreamName' \
        --output text 2>/dev/null)
    
    if [ -n "$RECENT_STREAMS" ] && [ "$RECENT_STREAMS" != "None" ]; then
        print_result 0 "Recent log streams found"
    else
        echo -e "${YELLOW}⚠ WARNING${NC}: No recent log streams (function may not have been invoked yet)"
    fi
else
    print_result 1 "CloudWatch log group not found"
fi
echo ""

# Test 8: Check ECR image
echo "Test 8: Checking ECR image..."
IMAGE_URI=$(echo $CONFIG | jq -r '.CodeSha256')
if [ -n "$IMAGE_URI" ] && [ "$IMAGE_URI" != "null" ]; then
    print_result 0 "Container image is configured"
else
    print_result 1 "Container image is not configured"
fi
echo ""

# Cleanup temporary files
rm -f /tmp/test-health-check.json /tmp/response-health.json
rm -f /tmp/test-upload-url.json /tmp/response-upload.json

# Summary
echo "=========================================="
echo "Verification Summary"
echo "=========================================="
echo -e "Tests Passed: ${GREEN}$TESTS_PASSED${NC}"
echo -e "Tests Failed: ${RED}$TESTS_FAILED${NC}"
echo "=========================================="
echo ""

if [ $TESTS_FAILED -eq 0 ]; then
    echo -e "${GREEN}✓ All tests passed! Lambda function is properly deployed.${NC}"
    echo ""
    echo "Next steps:"
    echo "1. Deploy API Gateway (Task 11.2)"
    echo "2. Configure CloudWatch monitoring (Task 11.3)"
    echo "3. Run end-to-end integration tests (Task 12)"
    exit 0
else
    echo -e "${RED}✗ Some tests failed. Please review the errors above.${NC}"
    echo ""
    echo "Common fixes:"
    echo "- Run deploy-lambda.sh to deploy/update the function"
    echo "- Check environment variables are set correctly"
    echo "- Verify IAM role has necessary permissions"
    echo "- Check CloudWatch logs for detailed errors"
    exit 1
fi
