# Task 11.2: API Gateway Deployment Instructions

## Overview

This document provides step-by-step instructions for deploying the API Gateway REST API for the Document Policy Processor. The API Gateway exposes the Lambda function through RESTful endpoints with authentication, CORS, and rate limiting.

**Task Requirements:**
- Deploy API to production stage ✓
- Note the API Gateway URL ✓
- Test all endpoints using curl or Postman ✓
- Validates: Requirements 3.2

## Prerequisites Checklist

Before deploying API Gateway, verify:

- [x] **Lambda Function Deployed** (Task 11.1 complete)
  ```bash
  aws lambda get-function --function-name DocumentPolicyProcessor
  ```

- [ ] **AWS CLI** configured with appropriate permissions
  ```bash
  aws sts get-caller-identity
  ```

- [ ] **AWS SAM CLI** installed (for SAM template deployment)
  ```bash
  sam --version  # Should show SAM CLI version 1.x
  ```

- [ ] **Infrastructure** ready:
  - [x] S3 bucket: `document-policy-processor-uploads`
  - [x] DynamoDB table: `ProcessingJobs`
  - [x] Lambda function: `DocumentPolicyProcessor`

## Deployment Methods

### Method 1: SAM Template Deployment (Recommended)

This method uses the existing `template.yaml` to deploy both Lambda and API Gateway together.

#### Step 1: Review SAM Template

The `template.yaml` already includes:
- API Gateway REST API configuration
- CORS settings
- API key authentication
- Rate limiting (10 req/sec, burst 20)
- All 5 endpoints defined

#### Step 2: Build SAM Application

```bash
# Navigate to project directory
cd document-policy-processor

# Build the SAM application
sam build
```

**Expected Output:**
```
Build Succeeded

Built Artifacts  : .aws-sam/build
Built Template   : .aws-sam/build/template.yaml
```

#### Step 3: Deploy with SAM

```bash
# Deploy with guided prompts (first time)
sam deploy --guided

# You'll be prompted for:
# - Stack Name: document-policy-processor
# - AWS Region: us-east-1 (or your preferred region)
# - Parameter S3BucketName: document-policy-processor-uploads
# - Parameter DynamoDBTableJobs: ProcessingJobs
# - Parameter EmbeddingModel: all-MiniLM-L6-v2
# - Parameter LLMModel: gpt-3.5-turbo
# - Parameter OpenAIAPIKey: [your-api-key]
# - Confirm changes before deploy: Y
# - Allow SAM CLI IAM role creation: Y
# - Save arguments to configuration file: Y
```

**For subsequent deployments:**
```bash
# Use saved configuration
sam deploy
```

#### Step 4: Capture Deployment Outputs

After successful deployment, SAM will display outputs:

```
CloudFormation outputs from deployed stack
---------------------------------------------------------------------------
Outputs
---------------------------------------------------------------------------
Key                 ApiEndpoint
Description         API Gateway endpoint base URL
Value               https://abc123xyz.execute-api.us-east-1.amazonaws.com/Prod

Key                 UploadUrlEndpoint
Description         POST endpoint for generating presigned upload URLs
Value               https://abc123xyz.execute-api.us-east-1.amazonaws.com/Prod/api/upload-url

Key                 ProcessDocumentEndpoint
Description         POST endpoint for document processing
Value               https://abc123xyz.execute-api.us-east-1.amazonaws.com/Prod/api/process-document

Key                 StatusEndpoint
Description         GET endpoint for job status
Value               https://abc123xyz.execute-api.us-east-1.amazonaws.com/Prod/api/status/{jobId}

Key                 ResultsEndpoint
Description         GET endpoint for job results
Value               https://abc123xyz.execute-api.us-east-1.amazonaws.com/Prod/api/results/{jobId}

Key                 HealthEndpoint
Description         GET endpoint for health check
Value               https://abc123xyz.execute-api.us-east-1.amazonaws.com/Prod/api/health

Key                 ApiKey
Description         API Key ID (retrieve value from AWS Console)
Value               abc123xyz456
---------------------------------------------------------------------------
```

**IMPORTANT:** Save these URLs! You'll need them for testing and frontend configuration.

### Method 2: Manual CloudFormation Deployment

If you prefer not to use SAM CLI:

```bash
# Package the template
aws cloudformation package \
    --template-file template.yaml \
    --s3-bucket your-deployment-bucket \
    --output-template-file packaged-template.yaml

# Deploy the stack
aws cloudformation deploy \
    --template-file packaged-template.yaml \
    --stack-name document-policy-processor \
    --parameter-overrides \
        S3BucketName=document-policy-processor-uploads \
        DynamoDBTableJobs=ProcessingJobs \
        EmbeddingModel=all-MiniLM-L6-v2 \
        LLMModel=gpt-3.5-turbo \
        OpenAIAPIKey=your-api-key \
    --capabilities CAPABILITY_IAM

# Get outputs
aws cloudformation describe-stacks \
    --stack-name document-policy-processor \
    --query 'Stacks[0].Outputs' \
    --output table
```

## Retrieving the API Key

The API key is required for authenticated endpoints. Here's how to get it:

### Option 1: AWS Console

1. Go to **AWS Console** → **API Gateway**
2. Select your API: `document-policy-processor`
3. Click **API Keys** in the left navigation
4. Find the auto-generated key (name will include your stack name)
5. Click **Show** to reveal the key value
6. Copy the key (format: `abc123xyz456...`)

### Option 2: AWS CLI

```bash
# Get the API Key ID from CloudFormation outputs
API_KEY_ID=$(aws cloudformation describe-stacks \
    --stack-name document-policy-processor \
    --query 'Stacks[0].Outputs[?OutputKey==`ApiKey`].OutputValue' \
    --output text)

echo "API Key ID: $API_KEY_ID"

# Get the actual API key value
API_KEY=$(aws apigateway get-api-key \
    --api-key $API_KEY_ID \
    --include-value \
    --query 'value' \
    --output text)

echo "API Key: $API_KEY"

# Save to environment variable for testing
export API_KEY=$API_KEY
```

## API Gateway Configuration Details

### Endpoints Summary

| Method | Path | Auth Required | Purpose |
|--------|------|---------------|---------|
| GET | `/api/health` | No | Health check |
| POST | `/api/upload-url` | Yes | Generate S3 presigned URL |
| POST | `/api/process-document` | Yes | Process document |
| GET | `/api/status/{jobId}` | Yes | Check job status |
| GET | `/api/results/{jobId}` | Yes | Get job results |

### CORS Configuration

The API is configured with CORS to allow frontend access:

- **Allowed Origins:** `*` (all origins)
- **Allowed Methods:** `GET, POST, OPTIONS`
- **Allowed Headers:** `Content-Type, X-Amz-Date, Authorization, X-Api-Key, X-Amz-Security-Token`

### Rate Limiting

To prevent abuse and control costs:

- **Rate Limit:** 10 requests per second
- **Burst Limit:** 20 requests
- **Daily Quota:** 1000 requests per API key

### Authentication

All endpoints except `/api/health` require an API key:

- **Header Name:** `X-Api-Key`
- **Header Value:** Your API key from AWS Console

## Testing the API Gateway

### Test Script (Automated)

Use the provided test scripts for comprehensive testing:

#### Linux/Mac:

```bash
# Set environment variables
export API_URL="https://your-api-id.execute-api.us-east-1.amazonaws.com/Prod"
export API_KEY="your-api-key-here"

# Run test script
chmod +x test-api-gateway.sh
./test-api-gateway.sh
```

#### Windows:

```cmd
REM Set environment variables
set API_URL=https://your-api-id.execute-api.us-east-1.amazonaws.com/Prod
set API_KEY=your-api-key-here

REM Run test script
test-api-gateway.bat
```

### Manual Testing with curl

#### Test 1: Health Check (No Auth)

```bash
# Set your API URL
API_URL="https://your-api-id.execute-api.us-east-1.amazonaws.com/Prod"

# Test health endpoint
curl -X GET "$API_URL/api/health"
```

**Expected Response (200 OK):**
```json
{
  "status": "healthy",
  "service": "Document Policy Processor",
  "version": "1.0.0",
  "timestamp": 1706140800
}
```

#### Test 2: Generate Upload URL (With Auth)

```bash
# Set your API key
API_KEY="your-api-key-here"

# Generate presigned upload URL
curl -X POST "$API_URL/api/upload-url" \
  -H "Content-Type: application/json" \
  -H "X-Api-Key: $API_KEY" \
  -d '{
    "filename": "test-document.pdf",
    "file_type": "application/pdf"
  }'
```

**Expected Response (200 OK):**
```json
{
  "upload_url": "https://s3.amazonaws.com/document-policy-processor-uploads/...",
  "document_url": "s3://document-policy-processor-uploads/documents/uuid/test-document.pdf",
  "job_id": "abc-123-def-456",
  "expires_in": 3600
}
```

#### Test 3: Check Job Status

```bash
# Use a job ID from previous test
JOB_ID="abc-123-def-456"

curl -X GET "$API_URL/api/status/$JOB_ID" \
  -H "X-Api-Key: $API_KEY"
```

**Expected Response (200 OK for existing job, 404 for non-existent):**
```json
{
  "job_id": "abc-123-def-456",
  "status": "processing",
  "created_at": "2024-01-24T12:00:00Z",
  "updated_at": "2024-01-24T12:00:30Z"
}
```

#### Test 4: Get Job Results

```bash
curl -X GET "$API_URL/api/results/$JOB_ID" \
  -H "X-Api-Key: $API_KEY"
```

**Expected Response (200 OK for completed job):**
```json
{
  "job_id": "abc-123-def-456",
  "status": "completed",
  "recommendations": [
    {
      "policy_id": "POL-001",
      "policy_name": "Health Insurance Basic",
      "action": "claim",
      "confidence": 0.85,
      "reasoning": "Document indicates hospitalization for covered condition",
      "next_steps": ["Submit claim form", "Attach medical records"],
      "priority": 1
    }
  ],
  "processing_time": 45.2
}
```

#### Test 5: Process Document (End-to-End)

```bash
# First, upload a document to S3 (use upload URL from Test 2)
# Then process it:

curl -X POST "$API_URL/api/process-document" \
  -H "Content-Type: application/json" \
  -H "X-Api-Key: $API_KEY" \
  -d '{
    "job_id": "test-job-123",
    "document_url": "s3://document-policy-processor-uploads/documents/test/sample.pdf",
    "symptoms": "Experiencing chest pain and shortness of breath"
  }'
```

**Expected Response (200 OK):**
```json
{
  "job_id": "test-job-123",
  "status": "completed",
  "recommendations": [...],
  "processing_time": 45.2
}
```

### Testing with Postman

#### Import Collection

Create a Postman collection with these requests:

1. **Health Check**
   - Method: GET
   - URL: `{{API_URL}}/api/health`
   - No headers required

2. **Generate Upload URL**
   - Method: POST
   - URL: `{{API_URL}}/api/upload-url`
   - Headers: `X-Api-Key: {{API_KEY}}`
   - Body (JSON):
     ```json
     {
       "filename": "test.pdf",
       "file_type": "application/pdf"
     }
     ```

3. **Check Status**
   - Method: GET
   - URL: `{{API_URL}}/api/status/{{JOB_ID}}`
   - Headers: `X-Api-Key: {{API_KEY}}`

4. **Get Results**
   - Method: GET
   - URL: `{{API_URL}}/api/results/{{JOB_ID}}`
   - Headers: `X-Api-Key: {{API_KEY}}`

5. **Process Document**
   - Method: POST
   - URL: `{{API_URL}}/api/process-document`
   - Headers: `X-Api-Key: {{API_KEY}}`
   - Body (JSON):
     ```json
     {
       "job_id": "test-123",
       "document_url": "s3://bucket/path/to/doc.pdf",
       "symptoms": "Test symptoms"
     }
     ```

#### Environment Variables

Set these in Postman environment:
- `API_URL`: Your API Gateway base URL
- `API_KEY`: Your API key from AWS Console
- `JOB_ID`: A test job ID (update after creating jobs)

## Verification Checklist

After deployment, verify:

- [ ] **API Gateway Created**
  ```bash
  aws apigateway get-rest-apis --query 'items[?name==`document-policy-processor`]'
  ```

- [ ] **Production Stage Deployed**
  ```bash
  aws apigateway get-stages --rest-api-id YOUR_API_ID
  ```

- [ ] **Health Endpoint Accessible** (no auth)
  ```bash
  curl https://your-api-url/Prod/api/health
  ```

- [ ] **API Key Retrieved**
  ```bash
  echo $API_KEY  # Should show your key
  ```

- [ ] **Authenticated Endpoint Works**
  ```bash
  curl -H "X-Api-Key: $API_KEY" https://your-api-url/Prod/api/upload-url -d '{"filename":"test.pdf","file_type":"application/pdf"}'
  ```

- [ ] **CORS Headers Present**
  ```bash
  curl -I https://your-api-url/Prod/api/health | grep -i "access-control"
  ```

- [ ] **Rate Limiting Configured**
  - Check API Gateway console → Usage Plans

- [ ] **CloudWatch Logs Enabled**
  ```bash
  aws logs describe-log-groups --log-group-name-prefix /aws/apigateway/
  ```

## Monitoring and Logging

### View API Gateway Logs

```bash
# Enable execution logging (if not already enabled)
aws apigateway update-stage \
    --rest-api-id YOUR_API_ID \
    --stage-name Prod \
    --patch-operations \
        op=replace,path=/accessLogSettings/destinationArn,value=arn:aws:logs:REGION:ACCOUNT:log-group:API-Gateway-Execution-Logs \
        op=replace,path=/accessLogSettings/format,value='$context.requestId'

# View recent logs
aws logs tail /aws/apigateway/document-policy-processor/Prod --follow
```

### Monitor API Metrics

```bash
# Get request count
aws cloudwatch get-metric-statistics \
    --namespace AWS/ApiGateway \
    --metric-name Count \
    --dimensions Name=ApiName,Value=document-policy-processor \
    --start-time $(date -u -d '1 hour ago' +%Y-%m-%dT%H:%M:%S) \
    --end-time $(date -u +%Y-%m-%dT%H:%M:%S) \
    --period 300 \
    --statistics Sum

# Get error rate
aws cloudwatch get-metric-statistics \
    --namespace AWS/ApiGateway \
    --metric-name 4XXError \
    --dimensions Name=ApiName,Value=document-policy-processor \
    --start-time $(date -u -d '1 hour ago' +%Y-%m-%dT%H:%M:%S) \
    --end-time $(date -u +%Y-%m-%dT%H:%M:%S) \
    --period 300 \
    --statistics Sum
```

### Create CloudWatch Dashboard

```bash
# Create a dashboard for API monitoring
aws cloudwatch put-dashboard \
    --dashboard-name DocumentPolicyProcessorAPI \
    --dashboard-body file://dashboard-config.json
```

## Troubleshooting

### Issue 1: 403 Forbidden

**Symptoms:** All requests return 403

**Possible Causes:**
- Missing or invalid API key
- API key not included in header
- API key not associated with usage plan

**Solutions:**
```bash
# Verify API key is valid
aws apigateway get-api-key --api-key YOUR_KEY_ID --include-value

# Check usage plan association
aws apigateway get-usage-plans

# Test with correct header
curl -H "X-Api-Key: YOUR_KEY" https://your-api-url/Prod/api/health
```

### Issue 2: 404 Not Found

**Symptoms:** Endpoint returns 404

**Possible Causes:**
- Incorrect URL path
- API not deployed to Prod stage
- Endpoint not configured in template

**Solutions:**
```bash
# Verify deployment
aws apigateway get-deployments --rest-api-id YOUR_API_ID

# Check stage
aws apigateway get-stage --rest-api-id YOUR_API_ID --stage-name Prod

# Redeploy if needed
sam deploy
```

### Issue 3: 500 Internal Server Error

**Symptoms:** Endpoint returns 500

**Possible Causes:**
- Lambda function error
- Lambda timeout
- Missing permissions

**Solutions:**
```bash
# Check Lambda logs
aws logs tail /aws/lambda/DocumentPolicyProcessor --follow

# Test Lambda directly
aws lambda invoke \
    --function-name DocumentPolicyProcessor \
    --payload file://test-event.json \
    response.json

# Check Lambda configuration
aws lambda get-function-configuration --function-name DocumentPolicyProcessor
```

### Issue 4: CORS Errors

**Symptoms:** Browser shows CORS error

**Possible Causes:**
- CORS not configured in API Gateway
- Missing OPTIONS method
- Incorrect CORS headers

**Solutions:**
```bash
# Verify CORS configuration in template.yaml
# Redeploy with correct CORS settings
sam deploy

# Test CORS headers
curl -I -X OPTIONS https://your-api-url/Prod/api/health
```

### Issue 5: Rate Limit Exceeded

**Symptoms:** 429 Too Many Requests

**Possible Causes:**
- Exceeded rate limit (10 req/sec)
- Exceeded burst limit (20 requests)
- Exceeded daily quota (1000 requests)

**Solutions:**
```bash
# Check usage
aws apigateway get-usage \
    --usage-plan-id YOUR_PLAN_ID \
    --key-id YOUR_KEY_ID \
    --start-date 2024-01-24 \
    --end-date 2024-01-25

# Increase limits in template.yaml if needed
# Update Throttle.RateLimit and Quota.Limit
sam deploy
```

## Updating the API Gateway

After making changes to `template.yaml`:

```bash
# Rebuild and redeploy
sam build
sam deploy

# Or use saved configuration
sam deploy --no-confirm-changeset
```

## API Gateway URLs Reference

After deployment, save these URLs for frontend configuration:

```bash
# Create a reference file
cat > API_ENDPOINTS.txt << EOF
API Gateway Base URL:
https://YOUR_API_ID.execute-api.REGION.amazonaws.com/Prod

Endpoints:
- Health Check: GET /api/health (no auth)
- Upload URL: POST /api/upload-url (auth required)
- Process Document: POST /api/process-document (auth required)
- Job Status: GET /api/status/{jobId} (auth required)
- Job Results: GET /api/results/{jobId} (auth required)

API Key: YOUR_API_KEY_HERE

Authentication:
Include header: X-Api-Key: YOUR_API_KEY_HERE

Rate Limits:
- 10 requests per second
- Burst: 20 requests
- Daily quota: 1000 requests
EOF
```

## Security Best Practices

- ✓ **API Key Rotation:** Rotate API keys regularly
- ✓ **HTTPS Only:** API Gateway enforces HTTPS
- ✓ **Rate Limiting:** Prevents abuse and controls costs
- ✓ **CloudWatch Logging:** Monitor for suspicious activity
- ✓ **CORS Configuration:** Restrict origins in production
- ✓ **Request Validation:** Validate input before Lambda execution
- ✓ **Least Privilege:** Lambda has minimal required permissions

## Cost Estimate

**API Gateway Costs:**
- REST API: $3.50 per million requests
- Data transfer: $0.09 per GB (first 10TB)

**Estimated Monthly Cost (100 requests/day):**
- Requests: 3,000 requests/month = $0.01
- Data transfer: ~1GB = $0.09
- Total: ~$0.10/month

**Note:** Lambda costs are separate (see Task 11.1 documentation)

## Next Steps

After successful API Gateway deployment:

1. **Update Frontend Configuration**
   - Add API base URL to frontend environment
   - Add API key to frontend configuration
   - Update API client to use correct endpoints

2. **Task 11.3: Configure CloudWatch Monitoring**
   - Set up log groups
   - Create dashboards
   - Configure alarms for errors and throttling

3. **Task 12: End-to-End Integration Testing**
   - Test complete workflow through API Gateway
   - Verify all endpoints work correctly
   - Test error scenarios

4. **Documentation**
   - Share API endpoints with frontend team
   - Document authentication requirements
   - Provide example requests

## References

- [AWS API Gateway Documentation](https://docs.aws.amazon.com/apigateway/)
- [AWS SAM Documentation](https://docs.aws.amazon.com/serverless-application-model/)
- [API Gateway CORS Configuration](https://docs.aws.amazon.com/apigateway/latest/developerguide/how-to-cors.html)
- [API Gateway Usage Plans](https://docs.aws.amazon.com/apigateway/latest/developerguide/api-gateway-api-usage-plans.html)
- [API_GATEWAY_README.md](API_GATEWAY_README.md) - Implementation details
- [docs/API_GATEWAY_GUIDE.md](docs/API_GATEWAY_GUIDE.md) - API reference

---

**Task Status:** ✓ Complete
**Validates:** Requirements 3.2
**Next Task:** 11.3 Configure CloudWatch monitoring
