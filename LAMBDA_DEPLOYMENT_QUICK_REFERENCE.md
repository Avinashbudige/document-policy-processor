# Lambda Deployment Quick Reference Card

## One-Command Deployment

### Linux/Mac
```bash
export OPENAI_API_KEY="sk-..." && chmod +x deploy-lambda.sh && ./deploy-lambda.sh
```

### Windows
```cmd
set OPENAI_API_KEY=sk-... && deploy-lambda.bat
```

## Verification

### Linux/Mac
```bash
chmod +x verify-lambda-deployment.sh && ./verify-lambda-deployment.sh
```

### Windows
```cmd
verify-lambda-deployment.bat
```

## Quick Tests

### Health Check
```bash
aws lambda invoke \
  --function-name DocumentPolicyProcessor \
  --payload '{"httpMethod":"GET","path":"/api/health"}' \
  response.json && cat response.json | jq .
```

### View Logs
```bash
aws logs tail /aws/lambda/DocumentPolicyProcessor --follow
```

### Check Configuration
```bash
aws lambda get-function-configuration \
  --function-name DocumentPolicyProcessor \
  | jq '{Memory:.MemorySize, Timeout:.Timeout, State:.State}'
```

## Update Function

### After Code Changes
```bash
./deploy-lambda.sh  # Rebuilds and redeploys
```

### Update Environment Variable Only
```bash
aws lambda update-function-configuration \
  --function-name DocumentPolicyProcessor \
  --environment Variables="{
    S3_BUCKET_NAME=document-policy-processor-uploads,
    DYNAMODB_TABLE_JOBS=ProcessingJobs,
    EMBEDDING_MODEL=all-MiniLM-L6-v2,
    LLM_MODEL=gpt-3.5-turbo,
    OPENAI_API_KEY=new-key-here
  }"
```

## Troubleshooting

### Docker Issues
```bash
docker system prune -a  # Clean up Docker
```

### ECR Authentication
```bash
aws ecr get-login-password --region us-east-1 | \
  docker login --username AWS --password-stdin \
  $(aws sts get-caller-identity --query Account --output text).dkr.ecr.us-east-1.amazonaws.com
```

### Increase Memory
```bash
aws lambda update-function-configuration \
  --function-name DocumentPolicyProcessor \
  --memory-size 3008
```

### View Recent Errors
```bash
aws logs filter-log-events \
  --log-group-name /aws/lambda/DocumentPolicyProcessor \
  --filter-pattern "ERROR" \
  --max-items 10
```

## Configuration Summary

| Setting | Value |
|---------|-------|
| **Function Name** | DocumentPolicyProcessor |
| **Memory** | 2048 MB |
| **Timeout** | 300 seconds (5 minutes) |
| **Package Type** | Image (Container) |
| **Runtime** | Python 3.11 (via container) |
| **Architecture** | x86_64 |

## Environment Variables

| Variable | Default Value |
|----------|---------------|
| `S3_BUCKET_NAME` | document-policy-processor-uploads |
| `DYNAMODB_TABLE_JOBS` | ProcessingJobs |
| `EMBEDDING_MODEL` | all-MiniLM-L6-v2 |
| `LLM_MODEL` | gpt-3.5-turbo |
| `OPENAI_API_KEY` | (required - set during deployment) |

## Performance Expectations

| Metric | Expected Value |
|--------|----------------|
| **Cold Start** | 20-40 seconds |
| **Warm Start** | 1-3 seconds |
| **Memory Usage** | 1200-1600 MB (60-80% of 2048MB) |
| **Processing Time** | 30-60 seconds per document |

## Cost Estimate

| Component | Cost |
|-----------|------|
| **Lambda Compute** | ~$0.002 per invocation |
| **ECR Storage** | ~$0.20/month |
| **Total (100 invocations/day)** | ~$6.20/month |

*Excludes OpenAI API costs*

## Next Steps After Deployment

1. ✓ Deploy Lambda function (Task 11.1)
2. ⏭ Deploy API Gateway (Task 11.2)
3. ⏭ Configure CloudWatch monitoring (Task 11.3)
4. ⏭ End-to-end integration testing (Task 12)

## Support Resources

- **Detailed Guide**: [TASK_11.1_LAMBDA_DEPLOYMENT.md](TASK_11.1_LAMBDA_DEPLOYMENT.md)
- **Deployment Guide**: [LAMBDA_DEPLOYMENT_GUIDE.md](LAMBDA_DEPLOYMENT_GUIDE.md)
- **Lambda Handler Docs**: [src/LAMBDA_HANDLER_README.md](src/LAMBDA_HANDLER_README.md)
- **AWS Lambda Docs**: https://docs.aws.amazon.com/lambda/

## Common Commands Reference

```bash
# Get function ARN
aws lambda get-function --function-name DocumentPolicyProcessor \
  --query 'Configuration.FunctionArn' --output text

# Get function URL (if configured)
aws lambda get-function-url-config --function-name DocumentPolicyProcessor

# List all Lambda functions
aws lambda list-functions --query 'Functions[*].[FunctionName,Runtime,MemorySize]' --output table

# Delete function (if needed)
aws lambda delete-function --function-name DocumentPolicyProcessor

# Get metrics
aws cloudwatch get-metric-statistics \
  --namespace AWS/Lambda \
  --metric-name Duration \
  --dimensions Name=FunctionName,Value=DocumentPolicyProcessor \
  --start-time $(date -u -d '1 hour ago' +%Y-%m-%dT%H:%M:%S) \
  --end-time $(date -u +%Y-%m-%dT%H:%M:%S) \
  --period 300 \
  --statistics Average,Maximum
```

---

**Last Updated**: January 2025
**Task**: 11.1 Deploy Lambda function
**Status**: Complete ✓
