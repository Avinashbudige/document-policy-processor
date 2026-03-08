# AWS Deployment - Quick Start

**Fast track guide if you already have AWS account and CLI configured**

---

## Prerequisites

- ✅ AWS account created
- ✅ AWS CLI installed and configured
- ✅ OpenAI API key

---

## 5-Minute Deployment

### Step 1: Deploy Infrastructure (2 minutes)

```cmd
cd document-policy-processor\infrastructure

REM Create S3 buckets
deploy-s3.bat

REM Create DynamoDB tables
deploy-dynamodb.bat

REM Create IAM roles
deploy-iam.bat

REM Pre-compute embeddings
deploy-embeddings.bat
```

**Save these values**:
- S3 bucket name: `document-policy-processor-uploads-[random]`
- IAM role ARN: `arn:aws:iam::123456789012:role/...`

### Step 2: Deploy Lambda (2 minutes)

```cmd
cd ..

REM Package function
py package-lambda.py

REM Deploy
deploy-lambda.bat
```

**When prompted, enter**:
- Function name: `DocumentPolicyProcessor`
- Role ARN: [paste from Step 1]
- Environment variables:
  ```
  S3_BUCKET_NAME=your-bucket-name
  DYNAMODB_TABLE_POLICIES=Policies
  DYNAMODB_TABLE_JOBS=ProcessingJobs
  OPENAI_API_KEY=sk-your-key
  AWS_REGION=us-east-1
  ```

**Save**: Lambda function ARN

### Step 3: Deploy API Gateway (1 minute)

```cmd
deploy-api-gateway.bat
```

**When prompted, enter**:
- API name: `DocumentPolicyProcessorAPI`
- Lambda ARN: [paste from Step 2]
- Create API key: `y`

**Save**:
- API URL: `https://[api-id].execute-api.us-east-1.amazonaws.com/prod`
- API Key: `[your-api-key]`

### Step 4: Setup Monitoring

```cmd
setup-cloudwatch-monitoring.bat
```

### Step 5: Test

```cmd
REM Test Lambda
verify-lambda-deployment.bat

REM Test API
test-api-gateway.bat --api-url [your-api-url] --api-key [your-api-key]
```

---

## Update Frontend

Edit `frontend/app.py`:

```python
API_BASE_URL = "https://[your-api-id].execute-api.us-east-1.amazonaws.com/prod"
API_KEY = "[your-api-key]"
```

Run frontend:

```cmd
cd frontend
streamlit run app.py
```

---

## Done! 🎉

Your application is deployed and ready for demo video recording!

---

## Troubleshooting

**Check logs**:
```cmd
aws logs tail /aws/lambda/DocumentPolicyProcessor --follow
```

**Test Lambda directly**:
```cmd
aws lambda invoke --function-name DocumentPolicyProcessor --payload file://test-event.json output.json
```

**Update environment variables**:
```cmd
aws lambda update-function-configuration ^
  --function-name DocumentPolicyProcessor ^
  --environment Variables={KEY=value}
```

---

## Need detailed help?

See `AWS_DEPLOYMENT_FOR_BEGINNERS.md` for complete step-by-step instructions.
