# Lambda Deployment Guide

This guide explains how to deploy the Document Policy Processor Lambda function using a container image approach.

## Overview

The Lambda function is deployed as a container image to AWS Lambda because of the large dependencies (sentence-transformers, torch). This approach provides:

- **Larger package size support**: Up to 10GB vs 250MB for ZIP deployment
- **Consistent environment**: Same Docker image works locally and in Lambda
- **Easier dependency management**: All dependencies bundled in the container

## Prerequisites

Before deploying, ensure you have:

1. **AWS CLI** installed and configured with appropriate credentials
2. **Docker** installed and running
3. **AWS Infrastructure** set up (S3 buckets, DynamoDB tables, IAM roles)
   - Run infrastructure setup scripts in `infrastructure/` directory first
4. **OpenAI API Key** (set as environment variable or in Lambda configuration)

## Deployment Architecture

```
┌─────────────────┐
│  Dockerfile     │  Build container with Python 3.11 + dependencies
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Docker Image   │  ~2GB image with torch (CPU), sentence-transformers
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Amazon ECR     │  Store container image
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  AWS Lambda     │  Deploy function from ECR image
└─────────────────┘
```

## Quick Start

### Option 1: Automated Deployment (Recommended)

**Linux/Mac:**
```bash
chmod +x deploy-lambda.sh
./deploy-lambda.sh
```

**Windows:**
```cmd
deploy-lambda.bat
```

The script will:
1. Create ECR repository (if not exists)
2. Build Docker image
3. Push to ECR
4. Create/update Lambda function

### Option 2: Manual Deployment

#### Step 1: Set Environment Variables

```bash
export AWS_REGION=us-east-1
export AWS_ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
export ECR_REPOSITORY_NAME=document-policy-processor
export LAMBDA_FUNCTION_NAME=DocumentPolicyProcessor
```

#### Step 2: Create ECR Repository

```bash
aws ecr create-repository \
    --repository-name $ECR_REPOSITORY_NAME \
    --region $AWS_REGION \
    --image-scanning-configuration scanOnPush=true
```

#### Step 3: Authenticate Docker to ECR

```bash
aws ecr get-login-password --region $AWS_REGION | \
    docker login --username AWS --password-stdin \
    $AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com
```

#### Step 4: Build Docker Image

```bash
docker build -t $ECR_REPOSITORY_NAME:latest .
```

#### Step 5: Tag and Push Image

```bash
docker tag $ECR_REPOSITORY_NAME:latest \
    $AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com/$ECR_REPOSITORY_NAME:latest

docker push \
    $AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com/$ECR_REPOSITORY_NAME:latest
```

#### Step 6: Create Lambda Function

```bash
# Get Lambda execution role ARN
LAMBDA_ROLE_ARN=$(aws iam get-role \
    --role-name DocumentPolicyProcessorLambdaRole \
    --query 'Role.Arn' --output text)

# Create Lambda function
aws lambda create-function \
    --function-name $LAMBDA_FUNCTION_NAME \
    --package-type Image \
    --code ImageUri=$AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com/$ECR_REPOSITORY_NAME:latest \
    --role $LAMBDA_ROLE_ARN \
    --timeout 300 \
    --memory-size 2048 \
    --environment Variables="{
        S3_BUCKET_NAME=document-policy-processor-uploads,
        DYNAMODB_TABLE_JOBS=ProcessingJobs,
        EMBEDDING_MODEL=all-MiniLM-L6-v2,
        LLM_MODEL=gpt-3.5-turbo,
        OPENAI_API_KEY=your-api-key-here
    }" \
    --region $AWS_REGION
```

## Local Testing with Docker

### Test Locally Before Deploying

```bash
# Build the image
docker build -t document-policy-processor:test .

# Run locally (requires AWS credentials)
docker run -p 9000:8080 \
    -e AWS_ACCESS_KEY_ID=$AWS_ACCESS_KEY_ID \
    -e AWS_SECRET_ACCESS_KEY=$AWS_SECRET_ACCESS_KEY \
    -e AWS_SESSION_TOKEN=$AWS_SESSION_TOKEN \
    -e S3_BUCKET_NAME=document-policy-processor-uploads \
    -e DYNAMODB_TABLE_JOBS=ProcessingJobs \
    -e OPENAI_API_KEY=your-api-key \
    document-policy-processor:test

# In another terminal, invoke the function
curl -XPOST "http://localhost:9000/2015-03-31/functions/function/invocations" \
    -d @test-event.json
```

### Test with AWS SAM (Alternative)

If you prefer AWS SAM for local testing:

1. Install AWS SAM CLI
2. Create `template.yaml`:

```yaml
AWSTemplateFormatVersion: '2010-09-09'
Transform: AWS::Serverless-2016-10-31

Resources:
  DocumentPolicyProcessor:
    Type: AWS::Serverless::Function
    Properties:
      PackageType: Image
      Timeout: 300
      MemorySize: 2048
      Environment:
        Variables:
          S3_BUCKET_NAME: document-policy-processor-uploads
          DYNAMODB_TABLE_JOBS: ProcessingJobs
          EMBEDDING_MODEL: all-MiniLM-L6-v2
          LLM_MODEL: gpt-3.5-turbo
    Metadata:
      Dockerfile: Dockerfile
      DockerContext: .
      DockerTag: latest
```

3. Test locally:

```bash
sam build
sam local invoke -e test-event.json
```

## Configuration

### Environment Variables

The Lambda function uses these environment variables:

| Variable | Description | Default |
|----------|-------------|---------|
| `S3_BUCKET_NAME` | S3 bucket for documents and embeddings | `document-policy-processor-uploads` |
| `DYNAMODB_TABLE_JOBS` | DynamoDB table for job tracking | `ProcessingJobs` |
| `EMBEDDING_MODEL` | Sentence-transformers model name | `all-MiniLM-L6-v2` |
| `LLM_MODEL` | OpenAI model for exclusion checking | `gpt-3.5-turbo` |
| `OPENAI_API_KEY` | OpenAI API key (required) | None |

### Lambda Configuration

Recommended settings:

- **Memory**: 2048 MB (required for ML models)
- **Timeout**: 300 seconds (5 minutes)
- **Ephemeral Storage**: 512 MB (default is sufficient)
- **Architecture**: x86_64 (required for torch CPU)

## Updating the Lambda Function

After making code changes:

```bash
# Rebuild and push new image
./deploy-lambda.sh

# Or manually:
docker build -t document-policy-processor:latest .
docker tag document-policy-processor:latest $ECR_URI:latest
docker push $ECR_URI:latest

# Update Lambda function
aws lambda update-function-code \
    --function-name DocumentPolicyProcessor \
    --image-uri $ECR_URI:latest
```

## Monitoring and Debugging

### View Logs

```bash
# Get recent logs
aws logs tail /aws/lambda/DocumentPolicyProcessor --follow

# Get logs for specific invocation
aws logs filter-log-events \
    --log-group-name /aws/lambda/DocumentPolicyProcessor \
    --filter-pattern "ERROR"
```

### Test Invocation

```bash
# Invoke function with test event
aws lambda invoke \
    --function-name DocumentPolicyProcessor \
    --payload file://test-event.json \
    response.json

# View response
cat response.json | jq .
```

### Check Function Status

```bash
# Get function configuration
aws lambda get-function-configuration \
    --function-name DocumentPolicyProcessor

# Get function metrics
aws cloudwatch get-metric-statistics \
    --namespace AWS/Lambda \
    --metric-name Duration \
    --dimensions Name=FunctionName,Value=DocumentPolicyProcessor \
    --start-time $(date -u -d '1 hour ago' +%Y-%m-%dT%H:%M:%S) \
    --end-time $(date -u +%Y-%m-%dT%H:%M:%S) \
    --period 300 \
    --statistics Average,Maximum
```

## Troubleshooting

### Common Issues

**1. Docker build fails with "no space left on device"**
```bash
# Clean up Docker
docker system prune -a
```

**2. Lambda timeout errors**
- Increase timeout to 300 seconds
- Check if policy embeddings are loaded correctly
- Verify S3 bucket access

**3. Out of memory errors**
- Increase memory to 3008 MB
- Use CPU-only torch version (already configured)

**4. Cold start is slow (>30 seconds)**
- This is expected for first invocation (loading ML models)
- Consider provisioned concurrency for production
- Models are cached in Lambda container for warm starts

**5. ECR authentication fails**
```bash
# Re-authenticate
aws ecr get-login-password --region $AWS_REGION | \
    docker login --username AWS --password-stdin $ECR_URI
```

### Debug Mode

Enable debug logging:

```bash
aws lambda update-function-configuration \
    --function-name DocumentPolicyProcessor \
    --environment Variables="{
        S3_BUCKET_NAME=document-policy-processor-uploads,
        DYNAMODB_TABLE_JOBS=ProcessingJobs,
        EMBEDDING_MODEL=all-MiniLM-L6-v2,
        LLM_MODEL=gpt-3.5-turbo,
        OPENAI_API_KEY=your-api-key,
        LOG_LEVEL=DEBUG
    }"
```

## Cost Optimization

### Reduce Image Size

The current Dockerfile uses CPU-only torch to reduce size:

```dockerfile
RUN pip install --no-cache-dir torch --index-url https://download.pytorch.org/whl/cpu
```

This reduces the image from ~4GB to ~2GB.

### Optimize Cold Starts

1. **Use provisioned concurrency** (costs more but eliminates cold starts)
2. **Keep functions warm** with scheduled pings
3. **Reduce dependencies** if possible

### Monitor Costs

```bash
# Check Lambda invocations
aws cloudwatch get-metric-statistics \
    --namespace AWS/Lambda \
    --metric-name Invocations \
    --dimensions Name=FunctionName,Value=DocumentPolicyProcessor \
    --start-time $(date -u -d '1 day ago' +%Y-%m-%dT%H:%M:%S) \
    --end-time $(date -u +%Y-%m-%dT%H:%M:%S) \
    --period 3600 \
    --statistics Sum
```

## Security Best Practices

1. **Never commit API keys** - Use AWS Secrets Manager or environment variables
2. **Use least privilege IAM roles** - Only grant necessary permissions
3. **Enable ECR image scanning** - Detect vulnerabilities in dependencies
4. **Rotate credentials regularly** - Update API keys periodically
5. **Use VPC** (optional) - For additional network isolation

## Next Steps

After deploying the Lambda function:

1. **Set up API Gateway** - Create REST API endpoints
2. **Configure triggers** - S3 events or API Gateway
3. **Add monitoring** - CloudWatch alarms for errors
4. **Load test** - Verify performance under load
5. **Set up CI/CD** - Automate deployments with GitHub Actions

## References

- [AWS Lambda Container Images](https://docs.aws.amazon.com/lambda/latest/dg/images-create.html)
- [Amazon ECR Documentation](https://docs.aws.amazon.com/ecr/)
- [AWS SAM CLI](https://docs.aws.amazon.com/serverless-application-model/latest/developerguide/serverless-sam-cli-install.html)
- [Docker Documentation](https://docs.docker.com/)
