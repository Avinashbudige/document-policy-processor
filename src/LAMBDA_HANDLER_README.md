# Lambda Handler Documentation

## Overview

The `lambda_handler.py` module is the main entry point for the Document Policy Processor Lambda function. It orchestrates the complete document processing pipeline from document upload to recommendation generation.

## Architecture

The Lambda handler integrates the following modules:
- **TextExtractor**: Extracts text from PDF, image, and text files using AWS Textract
- **PolicyMatcher**: Generates embeddings and matches documents against policies using semantic similarity
- **LLMExclusionChecker**: Validates policy matches and checks for exclusions using OpenAI GPT
- **RecommendationEngine**: Generates actionable recommendations based on validated policies

## Event Format

### Input Event (API Gateway)

```json
{
  "body": {
    "job_id": "unique-job-identifier",
    "document_url": "s3://bucket-name/path/to/document.pdf",
    "symptoms": "User-provided symptom description"
  }
}
```

Or for direct Lambda invocation:

```json
{
  "job_id": "unique-job-identifier",
  "document_url": "s3://bucket-name/path/to/document.pdf",
  "symptoms": "User-provided symptom description"
}
```

### Response Format

#### Success Response (200)

```json
{
  "statusCode": 200,
  "headers": {
    "Content-Type": "application/json",
    "Access-Control-Allow-Origin": "*"
  },
  "body": {
    "job_id": "unique-job-identifier",
    "status": "completed",
    "recommendations": [
      {
        "policy_id": "POL-001",
        "policy_name": "Health Insurance Basic",
        "action": "claim",
        "confidence": 0.85,
        "reasoning": "Policy matches your situation...",
        "next_steps": ["Step 1", "Step 2", "..."],
        "priority": 1
      }
    ],
    "processing_time": 12.34,
    "document_summary": "Extracted text preview..."
  }
}
```

#### Error Response (400/404/500)

```json
{
  "statusCode": 400,
  "body": {
    "job_id": "unique-job-identifier",
    "status": "failed",
    "error": "VALIDATION_ERROR",
    "error_message": "Missing required field: symptoms",
    "processing_time": 0.12
  }
}
```

## Environment Variables

The Lambda function requires the following environment variables:

| Variable | Description | Default |
|----------|-------------|---------|
| `S3_BUCKET_NAME` | S3 bucket for documents and embeddings | `document-policy-processor-uploads` |
| `DYNAMODB_TABLE_JOBS` | DynamoDB table for job tracking | `ProcessingJobs` |
| `OPENAI_API_KEY` | OpenAI API key for LLM exclusion checking | (required) |
| `EMBEDDING_MODEL` | Sentence-transformers model name | `all-MiniLM-L6-v2` |
| `LLM_MODEL` | OpenAI model name | `gpt-3.5-turbo` |

## Processing Pipeline

1. **Parse Event**: Extract job_id, document_url, and symptoms from the event
2. **Update Job Status**: Mark job as "processing" in DynamoDB
3. **Initialize Modules**: Lazy initialization of processing modules (cached across warm invocations)
4. **Download Document**: Download document from S3 to temporary local file
5. **Extract Text**: Extract text using appropriate method based on file type
6. **Match Policies**: Generate embeddings and find similar policies using cosine similarity
7. **Check Exclusions**: Validate each policy match using LLM to check for exclusions
8. **Generate Recommendations**: Combine results to produce prioritized recommendations
9. **Store Results**: Save results to DynamoDB with 7-day TTL
10. **Return Response**: Return formatted response to API Gateway

## Error Handling

The Lambda handler implements comprehensive error handling:

### Validation Errors (400)
- Missing required fields (job_id, document_url, symptoms)
- Invalid S3 URL format
- Empty field values

### Not Found Errors (404)
- Document not found in S3
- Invalid S3 bucket or key

### Processing Errors (500)
- Text extraction failures (OCR errors, corrupted files)
- Embedding generation failures
- LLM API failures (with automatic fallback to rule-based checking)
- Recommendation generation failures

### Unexpected Errors (500)
- Any unhandled exceptions are caught and logged
- User receives a generic error message
- Full error details are logged to CloudWatch

## Performance Optimizations

1. **Module Caching**: Processing modules are initialized once and reused across warm Lambda invocations
2. **Policy Embeddings**: Pre-computed embeddings are loaded from S3 once and cached in memory
3. **Temporary Files**: Documents are downloaded to `/tmp` and cleaned up after processing
4. **Lazy Initialization**: Modules are only initialized when first needed

## CloudWatch Logging

The Lambda function logs the following events:
- Event parsing and validation
- Job status updates
- Module initialization
- Document download and extraction
- Policy matching results
- Exclusion checking results
- Recommendation generation
- Errors and exceptions

Log level: `INFO` (configurable via environment variable)

## DynamoDB Schema

### ProcessingJobs Table

```
{
  "job_id": "string (partition key)",
  "status": "processing | completed | failed",
  "result": "JSON string (full result)",
  "data": "JSON string (intermediate data)",
  "updated_at": "number (Unix timestamp)",
  "ttl": "number (Unix timestamp, 7 days)"
}
```

## Testing

Run the test suite:

```bash
cd document-policy-processor
python -m pytest tests/test_lambda_handler.py -v
```

Test coverage includes:
- Event parsing (direct and API Gateway formats)
- Input validation
- Response formatting
- Error handling
- Module imports

## Deployment

### Lambda Configuration

- **Runtime**: Python 3.11 or later
- **Memory**: 2048 MB (recommended for sentence-transformers)
- **Timeout**: 300 seconds (5 minutes)
- **Handler**: `lambda_handler.lambda_handler`

### IAM Permissions

The Lambda execution role requires:
- `s3:GetObject` on the documents bucket
- `dynamodb:PutItem` on the ProcessingJobs table
- `textract:DetectDocumentText` for OCR
- `logs:CreateLogGroup`, `logs:CreateLogStream`, `logs:PutLogEvents` for CloudWatch

### Deployment Package

The Lambda function can be deployed as:
1. **ZIP file**: Package all dependencies with the code
2. **Container image**: Use Docker for large dependencies (sentence-transformers, torch)

Recommended: Use container image for easier dependency management.

## Example Usage

### Direct Lambda Invocation

```python
import boto3
import json

lambda_client = boto3.client('lambda')

event = {
    'job_id': 'test-job-123',
    'document_url': 's3://my-bucket/documents/policy.pdf',
    'symptoms': 'fever, cough, and fatigue'
}

response = lambda_client.invoke(
    FunctionName='document-policy-processor',
    InvocationType='RequestResponse',
    Payload=json.dumps(event)
)

result = json.loads(response['Payload'].read())
print(result)
```

### Via API Gateway

```bash
curl -X POST https://api-gateway-url/api/process-document \
  -H "Content-Type: application/json" \
  -d '{
    "job_id": "test-job-123",
    "document_url": "s3://my-bucket/documents/policy.pdf",
    "symptoms": "fever, cough, and fatigue"
  }'
```

## Troubleshooting

### Common Issues

1. **Module Import Errors**: Ensure all dependencies are included in the deployment package
2. **Timeout Errors**: Increase Lambda timeout or optimize processing (reduce document size)
3. **Memory Errors**: Increase Lambda memory allocation (sentence-transformers requires ~2GB)
4. **S3 Access Denied**: Verify IAM permissions and bucket policies
5. **OpenAI API Errors**: Check API key and rate limits; fallback to rule-based checking is automatic

### Debug Mode

Enable debug logging by setting environment variable:
```
LOG_LEVEL=DEBUG
```

## Requirements

See `requirements.txt` for full dependency list:
- boto3 (AWS SDK)
- sentence-transformers (embeddings)
- openai (LLM API)
- numpy (numerical operations)

## License

See LICENSE file in the repository root.
