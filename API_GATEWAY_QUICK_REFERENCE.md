# API Gateway Quick Reference

## Quick Deploy

### Linux/Mac
```bash
export OPENAI_API_KEY="sk-your-key-here"
chmod +x deploy-api-gateway.sh
./deploy-api-gateway.sh
```

### Windows
```cmd
set OPENAI_API_KEY=sk-your-key-here
deploy-api-gateway.bat
```

## API Endpoints

After deployment, you'll get a base URL like:
```
https://abc123xyz.execute-api.us-east-1.amazonaws.com/Prod
```

### Available Endpoints

| Endpoint | Method | Auth | Purpose |
|----------|--------|------|---------|
| `/api/health` | GET | No | Health check |
| `/api/upload-url` | POST | Yes | Get S3 upload URL |
| `/api/process-document` | POST | Yes | Process document |
| `/api/status/{jobId}` | GET | Yes | Check job status |
| `/api/results/{jobId}` | GET | Yes | Get results |

## Quick Test

### 1. Health Check (No Auth)
```bash
curl https://YOUR_API_URL/api/health
```

Expected: `{"status":"healthy",...}`

### 2. Generate Upload URL (With Auth)
```bash
curl -X POST https://YOUR_API_URL/api/upload-url \
  -H "Content-Type: application/json" \
  -H "X-Api-Key: YOUR_API_KEY" \
  -d '{"filename":"test.pdf","file_type":"application/pdf"}'
```

Expected: `{"upload_url":"https://s3...","job_id":"..."}`

### 3. Check Status
```bash
curl https://YOUR_API_URL/api/status/JOB_ID \
  -H "X-Api-Key: YOUR_API_KEY"
```

Expected: `{"job_id":"...","status":"processing"}`

## Get Your API Key

### AWS Console
1. Go to **API Gateway** → **API Keys**
2. Find your key → Click **Show**
3. Copy the value

### AWS CLI
```bash
# Get API Key ID from CloudFormation
API_KEY_ID=$(aws cloudformation describe-stacks \
  --stack-name document-policy-processor \
  --query 'Stacks[0].Outputs[?OutputKey==`ApiKey`].OutputValue' \
  --output text)

# Get actual key value
aws apigateway get-api-key \
  --api-key $API_KEY_ID \
  --include-value \
  --query 'value' \
  --output text
```

## Authentication

All endpoints except `/api/health` require an API key:

```bash
# Add this header to your requests
-H "X-Api-Key: YOUR_API_KEY_HERE"
```

## Rate Limits

- **Rate:** 10 requests/second
- **Burst:** 20 requests
- **Daily Quota:** 1000 requests

## Common Issues

### 403 Forbidden
- Missing or invalid API key
- Add header: `X-Api-Key: YOUR_KEY`

### 404 Not Found
- Wrong URL or path
- Check API is deployed to `Prod` stage

### 500 Internal Error
- Lambda function error
- Check CloudWatch logs:
  ```bash
  aws logs tail /aws/lambda/DocumentPolicyProcessor --follow
  ```

### CORS Error
- Browser blocking request
- CORS is configured for all origins (`*`)
- Ensure OPTIONS method is enabled

## Monitoring

### View API Logs
```bash
aws logs tail /aws/apigateway/document-policy-processor/Prod --follow
```

### View Lambda Logs
```bash
aws logs tail /aws/lambda/DocumentPolicyProcessor --follow
```

### Check Metrics
```bash
# Request count
aws cloudwatch get-metric-statistics \
  --namespace AWS/ApiGateway \
  --metric-name Count \
  --dimensions Name=ApiName,Value=document-policy-processor \
  --start-time $(date -u -d '1 hour ago' +%Y-%m-%dT%H:%M:%S) \
  --end-time $(date -u +%Y-%m-%dT%H:%M:%S) \
  --period 300 \
  --statistics Sum
```

## Update Deployment

After code changes:

```bash
# Rebuild and redeploy
sam build
sam deploy
```

## Frontend Configuration

Add these to your frontend environment:

```javascript
// .env or config file
API_BASE_URL=https://YOUR_API_ID.execute-api.REGION.amazonaws.com/Prod
API_KEY=your-api-key-here
```

## Example Frontend Code

```javascript
// Upload document
const response = await fetch(`${API_BASE_URL}/api/upload-url`, {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
    'X-Api-Key': API_KEY
  },
  body: JSON.stringify({
    filename: 'document.pdf',
    file_type: 'application/pdf'
  })
});

const { upload_url, job_id } = await response.json();

// Upload file to S3
await fetch(upload_url, {
  method: 'PUT',
  body: file,
  headers: { 'Content-Type': 'application/pdf' }
});

// Process document
await fetch(`${API_BASE_URL}/api/process-document`, {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
    'X-Api-Key': API_KEY
  },
  body: JSON.stringify({
    job_id,
    document_url: `s3://bucket/path/to/file`,
    symptoms: 'User symptoms here'
  })
});

// Check status
const statusResponse = await fetch(
  `${API_BASE_URL}/api/status/${job_id}`,
  { headers: { 'X-Api-Key': API_KEY } }
);

// Get results
const resultsResponse = await fetch(
  `${API_BASE_URL}/api/results/${job_id}`,
  { headers: { 'X-Api-Key': API_KEY } }
);
```

## Cost Estimate

- **API Gateway:** ~$0.10/month (100 requests/day)
- **Lambda:** ~$6/month (see Lambda deployment docs)
- **Total:** ~$6.10/month (excluding OpenAI API costs)

## Documentation

- **Full Guide:** [TASK_11.2_API_GATEWAY_DEPLOYMENT.md](TASK_11.2_API_GATEWAY_DEPLOYMENT.md)
- **API Reference:** [docs/API_GATEWAY_GUIDE.md](docs/API_GATEWAY_GUIDE.md)
- **Implementation:** [API_GATEWAY_README.md](API_GATEWAY_README.md)
- **Lambda Deployment:** [TASK_11.1_LAMBDA_DEPLOYMENT.md](TASK_11.1_LAMBDA_DEPLOYMENT.md)

## Support

For issues:
1. Check CloudWatch logs (Lambda and API Gateway)
2. Verify API key is correct
3. Test Lambda function directly
4. Review IAM permissions
5. Check DynamoDB and S3 access

## Next Steps

1. ✓ Deploy API Gateway
2. Test all endpoints
3. Update frontend with API URL and key
4. Configure CloudWatch monitoring (Task 11.3)
5. End-to-end integration testing (Task 12)
