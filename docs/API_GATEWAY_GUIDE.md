# API Gateway Setup Guide

This guide explains the API Gateway REST API configuration for the Document Policy Processor.

## Overview

The API Gateway provides a RESTful interface to the Document Policy Processor Lambda function. It includes four endpoints for document processing, status checking, results retrieval, and health monitoring.

## Endpoints

### 1. POST /api/upload-url

Generate a presigned URL for direct document upload to S3.

**Authentication**: API Key required

**Request Body**:
```json
{
  "filename": "medical-report.pdf",
  "file_type": "application/pdf"
}
```

**Response** (200 OK):
```json
{
  "upload_url": "https://document-policy-processor-uploads.s3.amazonaws.com/documents/uuid/medical-report.pdf?X-Amz-Algorithm=...",
  "document_url": "s3://document-policy-processor-uploads/documents/uuid/medical-report.pdf",
  "job_id": "550e8400-e29b-41d4-a716-446655440000",
  "expires_in": 3600,
  "upload_method": "PUT"
}
```

**Supported File Types**:
- `.pdf` - PDF documents
- `.png` - PNG images
- `.jpg`, `.jpeg` - JPEG images
- `.txt` - Plain text files

**Error Responses**:
- 400: Invalid filename or unsupported file type
- 500: Failed to generate presigned URL

**Usage Flow**:
1. Frontend calls this endpoint with filename and file type
2. Backend generates presigned URL and unique job ID
3. Frontend uploads file directly to S3 using the presigned URL (PUT request)
4. Frontend calls `/api/process-document` with the returned `document_url` and `job_id`

### 2. POST /api/process-document

Process a document and generate policy recommendations.

**Authentication**: API Key required

**Request Body**:
```json
{
  "job_id": "unique-job-identifier",
  "document_url": "s3://bucket-name/path/to/document.pdf",
  "symptoms": "User symptom description"
}
```

**Response** (200 OK):
```json
{
  "job_id": "unique-job-identifier",
  "status": "completed",
  "recommendations": [
    {
      "policy_id": "POL-001",
      "policy_name": "Basic Health Insurance",
      "action": "claim",
      "confidence": 0.85,
      "reasoning": "Policy covers the described symptoms...",
      "next_steps": ["Submit claim form", "Attach medical records"],
      "priority": 1
    }
  ],
  "processing_time": 12.34,
  "document_summary": "Extracted text preview..."
}
```

**Error Responses**:
- 400: Validation error (missing fields, invalid format)
- 404: Document not found in S3
- 500: Processing error

### 3. GET /api/status/{jobId}

Check the processing status of a job.

**Authentication**: API Key required

**Path Parameters**:
- `jobId`: The unique job identifier

**Response** (200 OK):
```json
{
  "job_id": "unique-job-identifier",
  "status": "processing",
  "updated_at": 1706140800
}
```

**Status Values**:
- `processing`: Job is currently being processed
- `completed`: Job completed successfully
- `failed`: Job failed with an error

**Error Responses**:
- 404: Job not found

### 4. GET /api/results/{jobId}

Retrieve the results of a completed job.

**Authentication**: API Key required

**Path Parameters**:
- `jobId`: The unique job identifier

**Response** (200 OK):
```json
{
  "job_id": "unique-job-identifier",
  "status": "completed",
  "recommendations": [...],
  "processing_time": 12.34,
  "document_summary": "..."
}
```

**Response** (202 Accepted):
```json
{
  "job_id": "unique-job-identifier",
  "status": "processing",
  "message": "Job is still processing. Please check back later."
}
```

**Error Responses**:
- 404: Job not found

### 5. GET /api/health

Health check endpoint to verify the service is running.

**Authentication**: No authentication required

**Response** (200 OK):
```json
{
  "status": "healthy",
  "service": "Document Policy Processor",
  "version": "1.0.0",
  "timestamp": 1706140800
}
```

## CORS Configuration

The API Gateway is configured with CORS to allow frontend access:

- **Allowed Origins**: `*` (all origins)
- **Allowed Methods**: `GET`, `POST`, `OPTIONS`
- **Allowed Headers**: `Content-Type`, `X-Amz-Date`, `Authorization`, `X-Api-Key`, `X-Amz-Security-Token`

## Authentication

All endpoints except `/api/health` require API key authentication.

### Using the API Key

Include the API key in the `X-Api-Key` header:

```bash
curl -X POST https://api-id.execute-api.region.amazonaws.com/Prod/api/process-document \
  -H "X-Api-Key: your-api-key-here" \
  -H "Content-Type: application/json" \
  -d '{
    "job_id": "test-job-123",
    "document_url": "s3://bucket/document.pdf",
    "symptoms": "Fever and cough"
  }'
```

### Retrieving the API Key

After deployment, retrieve the API key from AWS Console:

1. Go to API Gateway console
2. Select your API
3. Click "API Keys" in the left menu
4. Find the auto-generated key
5. Click "Show" to reveal the key value

## Rate Limiting

The API includes usage plan limits:

- **Rate Limit**: 10 requests per second
- **Burst Limit**: 20 requests
- **Quota**: 1000 requests per day

## Request Validation

The API Gateway validates requests before invoking the Lambda function:

- **Content-Type**: Must be `application/json` for POST requests
- **Request Size**: Maximum 10MB (API Gateway limit)
- **Required Fields**: Validated by Lambda function

## Deployment

The API Gateway is deployed using AWS SAM:

```bash
# Deploy the stack
sam deploy --guided

# Or use the deployment script
./deploy-lambda.sh
```

After deployment, the API endpoints will be output in the CloudFormation stack outputs.

## Testing

### Test Health Endpoint

```bash
curl https://api-id.execute-api.region.amazonaws.com/Prod/api/health
```

### Test Process Document Endpoint

```bash
curl -X POST https://api-id.execute-api.region.amazonaws.com/Prod/api/process-document \
  -H "X-Api-Key: your-api-key" \
  -H "Content-Type: application/json" \
  -d '{
    "job_id": "test-123",
    "document_url": "s3://document-policy-processor-uploads/documents/test.pdf",
    "symptoms": "Test symptoms"
  }'
```

### Test Status Endpoint

```bash
curl https://api-id.execute-api.region.amazonaws.com/Prod/api/status/test-123 \
  -H "X-Api-Key: your-api-key"
```

### Test Results Endpoint

```bash
curl https://api-id.execute-api.region.amazonaws.com/Prod/api/results/test-123 \
  -H "X-Api-Key: your-api-key"
```

## Monitoring

Monitor API Gateway metrics in CloudWatch:

- **4XXError**: Client errors (validation, not found)
- **5XXError**: Server errors (Lambda failures)
- **Count**: Total number of requests
- **Latency**: Request processing time
- **IntegrationLatency**: Lambda execution time

## Troubleshooting

### 403 Forbidden

- Check that you're including the API key in the `X-Api-Key` header
- Verify the API key is valid and associated with the usage plan

### 404 Not Found

- Verify the endpoint path is correct
- Check that the API is deployed to the correct stage (Prod)

### 500 Internal Server Error

- Check CloudWatch logs for Lambda function errors
- Verify environment variables are set correctly
- Check that IAM permissions are configured properly

### CORS Errors

- Verify the frontend is sending the correct headers
- Check that the API Gateway CORS configuration matches your needs
- Ensure OPTIONS method is enabled for preflight requests

## Security Best Practices

1. **API Key Rotation**: Rotate API keys regularly
2. **Usage Plans**: Monitor usage and adjust limits as needed
3. **CloudWatch Alarms**: Set up alarms for error rates
4. **Request Validation**: Enable request validation in API Gateway
5. **HTTPS Only**: API Gateway enforces HTTPS by default
6. **Least Privilege**: Lambda execution role has minimal required permissions

## Complete Upload and Processing Flow

The recommended flow for document upload and processing:

### Step 1: Request Upload URL

```bash
curl -X POST https://api-id.execute-api.region.amazonaws.com/Prod/api/upload-url \
  -H "X-Api-Key: your-api-key" \
  -H "Content-Type: application/json" \
  -d '{
    "filename": "medical-report.pdf",
    "file_type": "application/pdf"
  }'
```

Response:
```json
{
  "upload_url": "https://s3.amazonaws.com/...",
  "document_url": "s3://bucket/documents/uuid/medical-report.pdf",
  "job_id": "550e8400-e29b-41d4-a716-446655440000",
  "expires_in": 3600,
  "upload_method": "PUT"
}
```

### Step 2: Upload File to S3

```bash
curl -X PUT "https://s3.amazonaws.com/..." \
  -H "Content-Type: application/pdf" \
  --data-binary @medical-report.pdf
```

### Step 3: Trigger Processing

```bash
curl -X POST https://api-id.execute-api.region.amazonaws.com/Prod/api/process-document \
  -H "X-Api-Key: your-api-key" \
  -H "Content-Type: application/json" \
  -d '{
    "job_id": "550e8400-e29b-41d4-a716-446655440000",
    "document_url": "s3://bucket/documents/uuid/medical-report.pdf",
    "symptoms": "Fever and cough for 3 days"
  }'
```

### Step 4: Check Status (Optional)

```bash
curl https://api-id.execute-api.region.amazonaws.com/Prod/api/status/550e8400-e29b-41d4-a716-446655440000 \
  -H "X-Api-Key: your-api-key"
```

### Step 5: Get Results

```bash
curl https://api-id.execute-api.region.amazonaws.com/Prod/api/results/550e8400-e29b-41d4-a716-446655440000 \
  -H "X-Api-Key: your-api-key"
```

### Frontend Implementation Example (JavaScript)

```javascript
async function uploadAndProcessDocument(file, symptoms, apiKey, apiBaseUrl) {
  // Step 1: Get upload URL
  const uploadUrlResponse = await fetch(`${apiBaseUrl}/api/upload-url`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'X-Api-Key': apiKey
    },
    body: JSON.stringify({
      filename: file.name,
      file_type: file.type
    })
  });
  
  const { upload_url, document_url, job_id } = await uploadUrlResponse.json();
  
  // Step 2: Upload file to S3
  await fetch(upload_url, {
    method: 'PUT',
    headers: {
      'Content-Type': file.type
    },
    body: file
  });
  
  // Step 3: Trigger processing
  const processResponse = await fetch(`${apiBaseUrl}/api/process-document`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'X-Api-Key': apiKey
    },
    body: JSON.stringify({
      job_id: job_id,
      document_url: document_url,
      symptoms: symptoms
    })
  });
  
  const result = await processResponse.json();
  return result;
}
```

## Next Steps

- Configure custom domain name (optional)
- Set up CloudWatch alarms for monitoring
- Implement request throttling per client
- Add request/response logging for debugging
- Consider AWS WAF for additional security
