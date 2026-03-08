# API Gateway Implementation - Task 9.1

This document describes the API Gateway REST API implementation for the Document Policy Processor.

## Overview

Task 9.1 has been completed, implementing a full REST API with API Gateway that exposes the Lambda function through four endpoints.

## What Was Implemented

### 1. API Gateway Configuration (template.yaml)

Created an explicit API Gateway REST API resource with:

- **CORS Configuration**: Allows cross-origin requests from any domain
  - Methods: GET, POST, OPTIONS
  - Headers: Content-Type, X-Amz-Date, Authorization, X-Api-Key, X-Amz-Security-Token
  - Origin: * (all origins)

- **API Key Authentication**: Required for all endpoints except health check
  - Automatic API key generation
  - Usage plan with rate limiting and quotas

- **Rate Limiting**:
  - 10 requests per second
  - Burst limit of 20 requests
  - Daily quota of 1000 requests

### 2. API Endpoints

#### POST /api/process-document
- **Purpose**: Process a document and generate policy recommendations
- **Authentication**: API Key required
- **Input**: JSON with job_id, document_url (S3), and symptoms
- **Output**: Processing results with recommendations

#### GET /api/status/{jobId}
- **Purpose**: Check the processing status of a job
- **Authentication**: API Key required
- **Input**: Job ID in path parameter
- **Output**: Job status (processing, completed, failed)

#### GET /api/results/{jobId}
- **Purpose**: Retrieve the results of a completed job
- **Authentication**: API Key required
- **Input**: Job ID in path parameter
- **Output**: Full processing results with recommendations

#### GET /api/health
- **Purpose**: Health check endpoint
- **Authentication**: No authentication required
- **Output**: Service health status and version

### 3. Lambda Handler Updates (lambda_handler.py)

Enhanced the Lambda function to support routing:

- **Request Router**: Routes requests based on HTTP method and path
- **Handler Functions**: Separate handlers for each endpoint
  - `handle_health_check()`: Returns service health status
  - `handle_get_status()`: Queries DynamoDB for job status
  - `handle_get_results()`: Retrieves job results from DynamoDB
  - `handle_process_document()`: Original document processing logic

- **Error Handling**: Proper HTTP status codes for different error types
  - 400: Validation errors
  - 404: Resource not found
  - 500: Server errors

- **CORS Headers**: All responses include CORS headers

### 4. Documentation

Created comprehensive documentation:

- **API_GATEWAY_GUIDE.md**: Complete API reference with examples
  - Endpoint descriptions
  - Request/response formats
  - Authentication instructions
  - Testing examples
  - Troubleshooting guide

### 5. Testing Scripts

Created test scripts for both platforms:

- **test-api-gateway.sh**: Linux/Mac testing script
- **test-api-gateway.bat**: Windows testing script

Both scripts test:
- Health check endpoint
- Status endpoint (404 for non-existent jobs)
- Results endpoint (404 for non-existent jobs)
- Request validation (400 for missing fields)
- CORS headers
- API key authentication (403 without key)

## Deployment

To deploy the API Gateway:

```bash
# Linux/Mac
./deploy-lambda.sh

# Windows
deploy-lambda.bat
```

After deployment, the CloudFormation outputs will include:
- API base URL
- Individual endpoint URLs
- API Key ID (retrieve value from AWS Console)

## Testing

### Quick Test

```bash
# Get the API URL from CloudFormation outputs
API_URL="https://your-api-id.execute-api.region.amazonaws.com/Prod"

# Test health endpoint (no auth required)
curl $API_URL/api/health

# Test with API key
API_KEY="your-api-key-here"

# Run full test suite
./test-api-gateway.sh --api-url $API_URL --api-key $API_KEY
```

### Retrieve API Key

1. Go to AWS Console → API Gateway
2. Select your API
3. Click "API Keys" in the left menu
4. Find the auto-generated key
5. Click "Show" to reveal the key value

## Request Validation

The API validates:
- Required fields (job_id, document_url, symptoms)
- S3 URL format (must start with s3://)
- Non-empty values
- JSON format

## Security Features

1. **API Key Authentication**: Prevents unauthorized access
2. **CORS Configuration**: Controls which domains can access the API
3. **Rate Limiting**: Prevents abuse and controls costs
4. **HTTPS Only**: API Gateway enforces HTTPS
5. **Request Validation**: Validates input before processing

## Monitoring

Monitor the API in CloudWatch:
- Request count
- Error rates (4XX, 5XX)
- Latency
- Integration latency (Lambda execution time)

## Next Steps

After deployment:

1. **Retrieve API Key**: Get the API key from AWS Console
2. **Test Endpoints**: Run the test scripts to verify functionality
3. **Update Frontend**: Configure frontend to use the API endpoints
4. **Monitor Usage**: Set up CloudWatch alarms for errors and throttling
5. **Document for Users**: Share API documentation with frontend developers

## Files Modified/Created

### Modified
- `template.yaml`: Added API Gateway configuration and endpoints
- `src/lambda_handler.py`: Added routing and endpoint handlers

### Created
- `docs/API_GATEWAY_GUIDE.md`: Complete API documentation
- `test-api-gateway.sh`: Linux/Mac test script
- `test-api-gateway.bat`: Windows test script
- `API_GATEWAY_README.md`: This file

## Requirements Satisfied

This implementation satisfies requirement 3.2 from the design document:

✅ Created POST /api/process-document endpoint
✅ Created GET /api/status/{jobId} endpoint
✅ Created GET /api/results/{jobId} endpoint
✅ Created GET /api/health endpoint
✅ Configured CORS for frontend domain
✅ Added request validation
✅ Added API key authentication

## Troubleshooting

### Common Issues

**403 Forbidden**
- Ensure API key is included in X-Api-Key header
- Verify API key is valid

**404 Not Found**
- Check endpoint path is correct
- Verify API is deployed to Prod stage

**500 Internal Server Error**
- Check CloudWatch logs for Lambda errors
- Verify environment variables are set
- Check IAM permissions

**CORS Errors**
- Verify CORS configuration in template.yaml
- Check that OPTIONS method is enabled
- Ensure frontend sends correct headers

## Support

For issues or questions:
1. Check CloudWatch logs for Lambda function
2. Review API Gateway execution logs
3. Verify DynamoDB table exists and is accessible
4. Check IAM role permissions
