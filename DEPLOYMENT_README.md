# Lambda Deployment Package

This directory contains everything needed to deploy the Document Policy Processor Lambda function as a container image.

## Quick Start

### Prerequisites
- Docker installed and running
- AWS CLI configured with credentials
- Infrastructure already set up (S3, DynamoDB, IAM roles)

### Deploy to AWS

**Linux/Mac:**
```bash
chmod +x deploy-lambda.sh
./deploy-lambda.sh
```

**Windows:**
```cmd
deploy-lambda.bat
```

### Test Locally

**Linux/Mac:**
```bash
chmod +x test-lambda-local.sh
./test-lambda-local.sh
```

**Windows:**
```cmd
test-lambda-local.bat
```

## Files Overview

### Deployment Files

| File | Purpose |
|------|---------|
| `Dockerfile` | Container image definition with Python 3.11 and dependencies |
| `.dockerignore` | Excludes unnecessary files from Docker build |
| `deploy-lambda.sh` | Automated deployment script (Linux/Mac) |
| `deploy-lambda.bat` | Automated deployment script (Windows) |
| `template.yaml` | AWS SAM template for alternative deployment |

### Testing Files

| File | Purpose |
|------|---------|
| `test-lambda-local.sh` | Local testing with Docker (Linux/Mac) |
| `test-lambda-local.bat` | Local testing with Docker (Windows) |
| `test-event.json` | Sample Lambda event for testing |
| `cleanup-test.sh` | Cleanup script for test containers |

### Documentation

| File | Purpose |
|------|---------|
| `LAMBDA_DEPLOYMENT_GUIDE.md` | Comprehensive deployment guide |
| `DEPLOYMENT_README.md` | This file - quick reference |

### Source Code

| Directory | Contents |
|-----------|----------|
| `src/` | Lambda function code and modules |
| `src/requirements.txt` | Python dependencies |

## Dependencies

The Lambda function requires these major dependencies:

- **boto3** - AWS SDK for Python
- **sentence-transformers** - Embedding generation
- **torch** - PyTorch (CPU-only version)
- **openai** - OpenAI API client
- **numpy** - Numerical computing

Total image size: ~2GB (optimized with CPU-only torch)

## Environment Variables

Required environment variables for the Lambda function:

```bash
S3_BUCKET_NAME=document-policy-processor-uploads
DYNAMODB_TABLE_JOBS=ProcessingJobs
EMBEDDING_MODEL=all-MiniLM-L6-v2
LLM_MODEL=gpt-3.5-turbo
OPENAI_API_KEY=your-api-key-here
```

## Lambda Configuration

Recommended settings:

- **Memory**: 2048 MB (minimum for ML models)
- **Timeout**: 300 seconds (5 minutes)
- **Architecture**: x86_64
- **Package Type**: Image

## Deployment Process

The deployment script performs these steps:

1. **Create ECR Repository** - Stores container images
2. **Authenticate Docker** - Login to ECR
3. **Build Image** - Create container with dependencies
4. **Push to ECR** - Upload image to AWS
5. **Update Lambda** - Deploy function from ECR image

## Testing Process

Local testing with Docker:

1. **Build Image** - Create container locally
2. **Run Container** - Start Lambda runtime emulator
3. **Invoke Function** - Send test event
4. **View Logs** - Check execution logs
5. **Cleanup** - Stop and remove container

## Troubleshooting

### Common Issues

**Docker build fails:**
```bash
# Clean up Docker
docker system prune -a
```

**Lambda timeout:**
- Increase timeout to 300 seconds
- Check S3 bucket access
- Verify policy embeddings are loaded

**Out of memory:**
- Increase memory to 3008 MB
- Verify CPU-only torch is installed

**Cold start is slow:**
- Expected for first invocation (~30 seconds)
- Models are cached for warm starts
- Consider provisioned concurrency

### Debug Commands

```bash
# View Lambda logs
aws logs tail /aws/lambda/DocumentPolicyProcessor --follow

# Test Lambda function
aws lambda invoke \
    --function-name DocumentPolicyProcessor \
    --payload file://test-event.json \
    response.json

# Check function status
aws lambda get-function-configuration \
    --function-name DocumentPolicyProcessor
```

## Cost Considerations

- **Lambda execution**: ~$0.0000166667 per GB-second
- **ECR storage**: ~$0.10 per GB per month
- **Data transfer**: Varies by region
- **OpenAI API**: Varies by usage

Estimated cost for MVP: $5-20/month (depending on usage)

## Security Notes

- Never commit API keys to version control
- Use AWS Secrets Manager for production
- Enable ECR image scanning
- Use least privilege IAM roles
- Rotate credentials regularly

## Next Steps

After deployment:

1. Set up API Gateway endpoints
2. Configure CloudWatch alarms
3. Add monitoring dashboard
4. Implement CI/CD pipeline
5. Load test the function

## Support

For detailed information, see:
- [LAMBDA_DEPLOYMENT_GUIDE.md](LAMBDA_DEPLOYMENT_GUIDE.md) - Complete deployment guide
- [src/LAMBDA_HANDLER_README.md](src/LAMBDA_HANDLER_README.md) - Lambda handler documentation
- [infrastructure/README.md](infrastructure/README.md) - Infrastructure setup

## References

- [AWS Lambda Container Images](https://docs.aws.amazon.com/lambda/latest/dg/images-create.html)
- [Amazon ECR](https://docs.aws.amazon.com/ecr/)
- [AWS SAM](https://docs.aws.amazon.com/serverless-application-model/)
- [Docker](https://docs.docker.com/)
