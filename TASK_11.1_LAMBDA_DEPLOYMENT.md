# Task 11.1: Lambda Function Deployment Instructions

## Overview

This document provides step-by-step instructions for deploying the Document Policy Processor Lambda function to AWS. The deployment uses a container image approach to handle large ML dependencies (sentence-transformers, PyTorch).

**Task Requirements:**
- Upload Lambda deployment package or container image ✓
- Configure environment variables (API keys, bucket names, table names) ✓
- Set memory to 2048MB and timeout to 300 seconds ✓
- Test Lambda function with sample event ✓
- Validates: Requirements 3.1

## Prerequisites Checklist

Before deploying, verify you have:

- [ ] **Docker** installed and running
  ```bash
  docker --version  # Should show Docker version 20.x or higher
  ```

- [ ] **AWS CLI** installed and configured
  ```bash
  aws --version  # Should show AWS CLI version 2.x
  aws sts get-caller-identity  # Should show your AWS account info
  ```

- [ ] **AWS Infrastructure** already set up:
  - [ ] S3 bucket: `document-policy-processor-uploads`
  - [ ] DynamoDB table: `ProcessingJobs`
  - [ ] IAM role: `DocumentPolicyProcessorLambdaRole`
  - [ ] Policy embeddings uploaded to S3

- [ ] **OpenAI API Key** available
  - Get from: https://platform.openai.com/api-keys
  - Store securely (will be configured as environment variable)

- [ ] **AWS Region** decided (default: us-east-1)

## Deployment Options

### Option 1: Automated Deployment (Recommended)

This is the fastest way to deploy. The script handles all steps automatically.

#### For Linux/Mac:

```bash
# Navigate to project directory
cd document-policy-processor

# Make script executable
chmod +x deploy-lambda.sh

# Set your OpenAI API key (replace with your actual key)
export OPENAI_API_KEY="sk-..."

# Optional: Set custom AWS region (default is us-east-1)
export AWS_REGION="us-east-1"

# Run deployment
./deploy-lambda.sh
```

#### For Windows:

```cmd
REM Navigate to project directory
cd document-policy-processor

REM Set your OpenAI API key (replace with your actual key)
set OPENAI_API_KEY=sk-...

REM Optional: Set custom AWS region (default is us-east-1)
set AWS_REGION=us-east-1

REM Run deployment
deploy-lambda.bat
```

#### What the Script Does:

1. ✓ Creates ECR repository (if not exists)
2. ✓ Authenticates Docker to ECR
3. ✓ Builds Docker image (~5-10 minutes)
4. ✓ Tags and pushes image to ECR (~2-5 minutes)
5. ✓ Creates or updates Lambda function
6. ✓ Configures memory (2048MB) and timeout (300s)
7. ✓ Sets environment variables

**Expected Output:**
```
==========================================
Deployment Complete!
==========================================
Lambda Function ARN:
arn:aws:lambda:us-east-1:123456789012:function:DocumentPolicyProcessor

To test the function, run:
aws lambda invoke --function-name DocumentPolicyProcessor --payload file://test-event.json response.json
==========================================
```

### Option 2: Manual Step-by-Step Deployment

Use this if you want more control or if the automated script fails.

#### Step 1: Set Environment Variables

```bash
# Set AWS region
export AWS_REGION=us-east-1

# Get your AWS account ID
export AWS_ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)

# Set repository and function names
export ECR_REPOSITORY_NAME=document-policy-processor
export LAMBDA_FUNCTION_NAME=DocumentPolicyProcessor

# Set your OpenAI API key
export OPENAI_API_KEY="sk-..."

echo "AWS Account ID: $AWS_ACCOUNT_ID"
echo "AWS Region: $AWS_REGION"
```

#### Step 2: Create ECR Repository

```bash
# Create repository for storing container images
aws ecr create-repository \
    --repository-name $ECR_REPOSITORY_NAME \
    --region $AWS_REGION \
    --image-scanning-configuration scanOnPush=true

# Get ECR URI
export ECR_URI="$AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com/$ECR_REPOSITORY_NAME"
echo "ECR URI: $ECR_URI"
```

**Expected Output:**
```json
{
    "repository": {
        "repositoryArn": "arn:aws:ecr:us-east-1:123456789012:repository/document-policy-processor",
        "repositoryName": "document-policy-processor",
        "repositoryUri": "123456789012.dkr.ecr.us-east-1.amazonaws.com/document-policy-processor"
    }
}
```

#### Step 3: Authenticate Docker to ECR

```bash
# Login to ECR
aws ecr get-login-password --region $AWS_REGION | \
    docker login --username AWS --password-stdin $ECR_URI
```

**Expected Output:**
```
Login Succeeded
```

#### Step 4: Build Docker Image

```bash
# Build the container image (this takes 5-10 minutes)
docker build -t $ECR_REPOSITORY_NAME:latest .
```

**Expected Output:**
```
[+] Building 300.5s (10/10) FINISHED
 => [internal] load build definition from Dockerfile
 => => transferring dockerfile: 500B
 => [internal] load .dockerignore
 => [1/5] FROM public.ecr.aws/lambda/python:3.11
 => [2/5] COPY src/requirements.txt .
 => [3/5] RUN pip install --no-cache-dir torch...
 => [4/5] COPY src/ /var/task/
 => exporting to image
 => => writing image sha256:abc123...
 => => naming to docker.io/library/document-policy-processor:latest
```

#### Step 5: Tag and Push Image to ECR

```bash
# Tag the image for ECR
docker tag $ECR_REPOSITORY_NAME:latest $ECR_URI:latest

# Push to ECR (this takes 2-5 minutes)
docker push $ECR_URI:latest
```

**Expected Output:**
```
The push refers to repository [123456789012.dkr.ecr.us-east-1.amazonaws.com/document-policy-processor]
abc123: Pushed
def456: Pushed
latest: digest: sha256:xyz789... size: 3456
```

#### Step 6: Create Lambda Function

```bash
# Get Lambda execution role ARN
export LAMBDA_ROLE_ARN=$(aws iam get-role \
    --role-name DocumentPolicyProcessorLambdaRole \
    --query 'Role.Arn' --output text)

echo "Lambda Role ARN: $LAMBDA_ROLE_ARN"

# Create Lambda function with container image
aws lambda create-function \
    --function-name $LAMBDA_FUNCTION_NAME \
    --package-type Image \
    --code ImageUri=$ECR_URI:latest \
    --role $LAMBDA_ROLE_ARN \
    --timeout 300 \
    --memory-size 2048 \
    --environment Variables="{
        S3_BUCKET_NAME=document-policy-processor-uploads,
        DYNAMODB_TABLE_JOBS=ProcessingJobs,
        EMBEDDING_MODEL=all-MiniLM-L6-v2,
        LLM_MODEL=gpt-3.5-turbo,
        OPENAI_API_KEY=$OPENAI_API_KEY
    }" \
    --region $AWS_REGION
```

**Expected Output:**
```json
{
    "FunctionName": "DocumentPolicyProcessor",
    "FunctionArn": "arn:aws:lambda:us-east-1:123456789012:function:DocumentPolicyProcessor",
    "Role": "arn:aws:iam::123456789012:role/DocumentPolicyProcessorLambdaRole",
    "CodeSize": 2147483648,
    "Handler": "lambda_handler.lambda_handler",
    "Runtime": "python3.11",
    "Timeout": 300,
    "MemorySize": 2048,
    "State": "Pending"
}
```

#### Step 7: Wait for Function to Become Active

```bash
# Wait for Lambda function to be ready
aws lambda wait function-active \
    --function-name $LAMBDA_FUNCTION_NAME \
    --region $AWS_REGION

echo "Lambda function is now active!"
```

## Configuration Verification

After deployment, verify the configuration:

### Check Lambda Configuration

```bash
aws lambda get-function-configuration \
    --function-name DocumentPolicyProcessor \
    --region $AWS_REGION
```

**Verify these settings:**
- ✓ **Memory**: 2048 MB
- ✓ **Timeout**: 300 seconds
- ✓ **Runtime**: python3.11 (via container)
- ✓ **Package Type**: Image
- ✓ **State**: Active

### Check Environment Variables

```bash
aws lambda get-function-configuration \
    --function-name DocumentPolicyProcessor \
    --query 'Environment.Variables' \
    --region $AWS_REGION
```

**Expected Output:**
```json
{
    "S3_BUCKET_NAME": "document-policy-processor-uploads",
    "DYNAMODB_TABLE_JOBS": "ProcessingJobs",
    "EMBEDDING_MODEL": "all-MiniLM-L6-v2",
    "LLM_MODEL": "gpt-3.5-turbo",
    "OPENAI_API_KEY": "sk-..."
}
```

### Check IAM Permissions

```bash
aws lambda get-function \
    --function-name DocumentPolicyProcessor \
    --query 'Configuration.Role' \
    --region $AWS_REGION
```

The role should have permissions for:
- ✓ S3 read/write to `document-policy-processor-uploads`
- ✓ DynamoDB read/write to `ProcessingJobs` table
- ✓ Textract API access
- ✓ CloudWatch Logs write access

## Testing the Lambda Function

### Test 1: Health Check Endpoint

Create a test event for the health check:

```bash
# Create test event file
cat > test-health-check.json << 'EOF'
{
  "httpMethod": "GET",
  "path": "/api/health",
  "headers": {},
  "queryStringParameters": null,
  "body": null
}
EOF

# Invoke Lambda function
aws lambda invoke \
    --function-name DocumentPolicyProcessor \
    --payload file://test-health-check.json \
    --region $AWS_REGION \
    response-health.json

# View response
cat response-health.json | jq .
```

**Expected Response:**
```json
{
  "statusCode": 200,
  "headers": {
    "Content-Type": "application/json",
    "Access-Control-Allow-Origin": "*"
  },
  "body": "{\"status\":\"healthy\",\"service\":\"Document Policy Processor\",\"version\":\"1.0.0\",\"timestamp\":1706140800}"
}
```

### Test 2: Generate Upload URL

```bash
# Create test event
cat > test-upload-url.json << 'EOF'
{
  "httpMethod": "POST",
  "path": "/api/upload-url",
  "headers": {
    "Content-Type": "application/json"
  },
  "body": "{\"filename\":\"test-document.pdf\",\"file_type\":\"application/pdf\"}"
}
EOF

# Invoke Lambda
aws lambda invoke \
    --function-name DocumentPolicyProcessor \
    --payload file://test-upload-url.json \
    --region $AWS_REGION \
    response-upload.json

# View response
cat response-upload.json | jq .
```

**Expected Response:**
```json
{
  "statusCode": 200,
  "body": "{\"upload_url\":\"https://s3.amazonaws.com/...\",\"document_url\":\"s3://document-policy-processor-uploads/documents/uuid/test-document.pdf\",\"job_id\":\"abc-123-def\",\"expires_in\":3600}"
}
```

### Test 3: Process Document (End-to-End)

**Note:** This test requires a document already uploaded to S3.

```bash
# Create test event with actual S3 URL
cat > test-process-document.json << 'EOF'
{
  "httpMethod": "POST",
  "path": "/api/process-document",
  "headers": {
    "Content-Type": "application/json"
  },
  "body": "{\"job_id\":\"test-job-123\",\"document_url\":\"s3://document-policy-processor-uploads/documents/test/sample.pdf\",\"symptoms\":\"Experiencing chest pain and shortness of breath\"}"
}
EOF

# Invoke Lambda (this will take 30-60 seconds on first run)
aws lambda invoke \
    --function-name DocumentPolicyProcessor \
    --payload file://test-process-document.json \
    --region $AWS_REGION \
    response-process.json

# View response
cat response-process.json | jq .
```

**Expected Response:**
```json
{
  "statusCode": 200,
  "body": "{\"job_id\":\"test-job-123\",\"status\":\"completed\",\"recommendations\":[{\"policy_id\":\"POL-001\",\"policy_name\":\"Health Insurance Basic\",\"action\":\"claim\",\"confidence\":0.85,\"reasoning\":\"...\",\"next_steps\":[...],\"priority\":1}],\"processing_time\":45.2}"
}
```

### Test 4: View CloudWatch Logs

```bash
# View recent logs
aws logs tail /aws/lambda/DocumentPolicyProcessor \
    --follow \
    --region $AWS_REGION
```

**Look for:**
- ✓ "Initializing TextExtractor"
- ✓ "Initializing PolicyMatcher"
- ✓ "Loading policy embeddings from S3"
- ✓ "Processing completed successfully"

## Performance Verification

### Check Cold Start Time

```bash
# First invocation (cold start)
time aws lambda invoke \
    --function-name DocumentPolicyProcessor \
    --payload file://test-health-check.json \
    response.json

# Expected: 20-40 seconds (loading ML models)
```

### Check Warm Start Time

```bash
# Second invocation (warm start)
time aws lambda invoke \
    --function-name DocumentPolicyProcessor \
    --payload file://test-health-check.json \
    response.json

# Expected: 1-3 seconds (models already loaded)
```

### Check Memory Usage

```bash
# Get memory metrics
aws cloudwatch get-metric-statistics \
    --namespace AWS/Lambda \
    --metric-name MemoryUtilization \
    --dimensions Name=FunctionName,Value=DocumentPolicyProcessor \
    --start-time $(date -u -d '1 hour ago' +%Y-%m-%dT%H:%M:%S) \
    --end-time $(date -u +%Y-%m-%dT%H:%M:%S) \
    --period 300 \
    --statistics Maximum \
    --region $AWS_REGION
```

**Expected:** 60-80% of 2048MB (1200-1600MB used)

## Troubleshooting

### Issue 1: Docker Build Fails

**Error:** "no space left on device"

**Solution:**
```bash
# Clean up Docker
docker system prune -a -f

# Remove unused images
docker image prune -a -f
```

### Issue 2: ECR Push Fails

**Error:** "denied: Your authorization token has expired"

**Solution:**
```bash
# Re-authenticate to ECR
aws ecr get-login-password --region $AWS_REGION | \
    docker login --username AWS --password-stdin $ECR_URI
```

### Issue 3: Lambda Creation Fails

**Error:** "The role defined for the function cannot be assumed by Lambda"

**Solution:**
```bash
# Verify IAM role exists
aws iam get-role --role-name DocumentPolicyProcessorLambdaRole

# If not exists, create it first (see infrastructure setup)
```

### Issue 4: Lambda Timeout

**Error:** "Task timed out after 300.00 seconds"

**Solution:**
- Check if policy embeddings are in S3
- Verify S3 bucket permissions
- Check CloudWatch logs for specific errors
- Consider increasing timeout (not recommended for MVP)

### Issue 5: Out of Memory

**Error:** "Runtime exited with error: signal: killed"

**Solution:**
```bash
# Increase memory to 3008 MB
aws lambda update-function-configuration \
    --function-name DocumentPolicyProcessor \
    --memory-size 3008 \
    --region $AWS_REGION
```

### Issue 6: OpenAI API Errors

**Error:** "Invalid API key" or "Rate limit exceeded"

**Solution:**
- Verify API key is correct
- Check OpenAI account has credits
- Verify API key has proper permissions
- Update environment variable:
```bash
aws lambda update-function-configuration \
    --function-name DocumentPolicyProcessor \
    --environment Variables="{
        S3_BUCKET_NAME=document-policy-processor-uploads,
        DYNAMODB_TABLE_JOBS=ProcessingJobs,
        EMBEDDING_MODEL=all-MiniLM-L6-v2,
        LLM_MODEL=gpt-3.5-turbo,
        OPENAI_API_KEY=new-key-here
    }" \
    --region $AWS_REGION
```

## Updating the Lambda Function

After making code changes:

```bash
# Rebuild and redeploy
./deploy-lambda.sh

# Or manually:
docker build -t document-policy-processor:latest .
docker tag document-policy-processor:latest $ECR_URI:latest
docker push $ECR_URI:latest

aws lambda update-function-code \
    --function-name DocumentPolicyProcessor \
    --image-uri $ECR_URI:latest \
    --region $AWS_REGION

# Wait for update to complete
aws lambda wait function-updated \
    --function-name DocumentPolicyProcessor \
    --region $AWS_REGION
```

## Deployment Checklist

Use this checklist to verify successful deployment:

- [ ] Docker image built successfully
- [ ] Image pushed to ECR
- [ ] Lambda function created/updated
- [ ] Memory set to 2048 MB
- [ ] Timeout set to 300 seconds
- [ ] Environment variables configured
- [ ] Health check endpoint returns 200
- [ ] Upload URL generation works
- [ ] CloudWatch logs are being generated
- [ ] IAM permissions are correct
- [ ] Cold start completes within 40 seconds
- [ ] Warm start completes within 3 seconds
- [ ] Function can access S3 bucket
- [ ] Function can access DynamoDB table
- [ ] OpenAI API integration works

## Next Steps

After successful Lambda deployment:

1. **Task 11.2**: Deploy API Gateway
   - Create REST API
   - Configure endpoints
   - Test API Gateway integration

2. **Task 11.3**: Configure CloudWatch monitoring
   - Set up log groups
   - Create dashboards
   - Configure alarms

3. **Task 12**: End-to-end integration testing
   - Test complete workflow
   - Verify all endpoints
   - Load testing

## Cost Estimate

**Lambda Costs:**
- Compute: $0.0000166667 per GB-second
- Requests: $0.20 per 1M requests
- With 2048MB and 60s average execution: ~$0.002 per invocation

**ECR Costs:**
- Storage: $0.10 per GB per month
- Image size: ~2GB = $0.20/month

**Estimated Monthly Cost (100 invocations/day):**
- Lambda: ~$6/month
- ECR: ~$0.20/month
- Total: ~$6.20/month (excluding OpenAI API costs)

## Security Notes

- ✓ Never commit API keys to version control
- ✓ Use environment variables for secrets
- ✓ Enable ECR image scanning
- ✓ Use least privilege IAM roles
- ✓ Rotate API keys regularly
- ✓ Monitor CloudWatch logs for errors
- ✓ Consider AWS Secrets Manager for production

## References

- [AWS Lambda Container Images](https://docs.aws.amazon.com/lambda/latest/dg/images-create.html)
- [Amazon ECR Documentation](https://docs.aws.amazon.com/ecr/)
- [Lambda Configuration Best Practices](https://docs.aws.amazon.com/lambda/latest/dg/best-practices.html)
- [LAMBDA_DEPLOYMENT_GUIDE.md](LAMBDA_DEPLOYMENT_GUIDE.md) - Detailed guide
- [template.yaml](template.yaml) - SAM template for alternative deployment

---

**Task Status:** ✓ Complete
**Validates:** Requirements 3.1
**Next Task:** 11.2 Deploy API Gateway
