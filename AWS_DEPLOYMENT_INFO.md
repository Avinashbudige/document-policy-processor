# AWS Deployment Information

**Generated**: March 8, 2026
**Status**: Deployment Complete (6/7 steps)

---

## 🎯 Quick Access

### API Gateway
- **Base URL**: `https://bmi41mg6uf.execute-api.us-east-1.amazonaws.com/prod`
- **API Key**: `9wx9nHe2NV5vSAOyRps9l3c7PpQ19OttaJqHw4mw`
- **Region**: us-east-1

### Test Command
```bash
curl -X GET "https://bmi41mg6uf.execute-api.us-east-1.amazonaws.com/prod/api/health" \
  -H "X-Api-Key: 9wx9nHe2NV5vSAOyRps9l3c7PpQ19OttaJqHw4mw"
```

---

## 📋 Deployed Resources

### 1. S3 Bucket
- **Name**: `document-policy-processor-uploads`
- **Region**: us-east-1
- **Purpose**: Document storage, embeddings, and results
- **Folders**:
  - `documents/` - Uploaded documents
  - `embeddings/` - Pre-computed policy embeddings
  - `results/` - Processing results

### 2. DynamoDB Tables

#### Policies Table
- **Name**: `Policies`
- **Primary Key**: `policy_id` (String)
- **Purpose**: Store insurance policy information
- **Sample Data**: 3 policies loaded

#### ProcessingJobs Table
- **Name**: `ProcessingJobs`
- **Primary Key**: `job_id` (String)
- **Purpose**: Track document processing jobs
- **TTL**: Enabled for auto-cleanup

### 3. IAM Roles

#### Lambda Execution Role
- **Name**: `DocumentPolicyProcessor-Lambda-dev`
- **ARN**: `arn:aws:iam::877786395190:role/DocumentPolicyProcessor-Lambda-dev`
- **Permissions**:
  - S3: GetObject, PutObject, DeleteObject, ListBucket
  - DynamoDB: GetItem, PutItem, Query, Scan
  - Textract: DetectDocumentText, AnalyzeDocument
  - CloudWatch: CreateLogGroup, CreateLogStream, PutLogEvents

#### API Gateway Role
- **Name**: `DocumentPolicyProcessor-ApiGateway-dev`
- **ARN**: `arn:aws:iam::877786395190:role/DocumentPolicyProcessor-ApiGateway-dev`
- **Permissions**:
  - Lambda: InvokeFunction
  - CloudWatch: Logging

### 4. Policy Embeddings
- **Model**: all-MiniLM-L6-v2
- **Dimension**: 384
- **Policies**: 3 embeddings generated
- **Location**: `s3://document-policy-processor-uploads/embeddings/`
- **Files**:
  - `policy_embeddings.json`
  - `policy_metadata.json`
  - `embeddings_info.json`

### 5. Lambda Function
- **Name**: `DocumentPolicyProcessor`
- **ARN**: `arn:aws:lambda:us-east-1:877786395190:function:DocumentPolicyProcessor`
- **Runtime**: Container Image (Python 3.11)
- **Memory**: 2048 MB
- **Timeout**: 300 seconds (5 minutes)
- **Image**: `877786395190.dkr.ecr.us-east-1.amazonaws.com/document-policy-processor@sha256:72fd0b6bbc9c71d3d609d0388796b500eca0dec5ffdf6540c77542ec106a580a`

#### Environment Variables
```
S3_BUCKET_NAME=document-policy-processor-uploads
DYNAMODB_TABLE_POLICIES=Policies
DYNAMODB_TABLE_JOBS=ProcessingJobs
EMBEDDING_MODEL=all-MiniLM-L6-v2
LLM_MODEL=gpt-3.5-turbo
```

**⚠️ Note**: OpenAI API key needs to be added for full functionality

### 6. API Gateway
- **API ID**: `bmi41mg6uf`
- **Name**: `DocumentPolicyProcessorAPI`
- **Type**: REST API (Regional)
- **Stage**: prod
- **Base URL**: `https://bmi41mg6uf.execute-api.us-east-1.amazonaws.com/prod`

#### API Key
- **Key ID**: `e9qkm17b0h`
- **Key Value**: `9wx9nHe2NV5vSAOyRps9l3c7PpQ19OttaJqHw4mw`
- **Header Name**: `X-Api-Key`

#### Rate Limits
- **Burst Limit**: 20 requests
- **Rate Limit**: 10 requests/second
- **Daily Quota**: 1000 requests

#### Endpoints
- **Health Check**: `GET /api/health` (no auth required)

---

## 🔧 Configuration for Frontend

Update your frontend configuration with these values:

```python
# frontend/app.py or frontend/.streamlit/secrets.toml

API_BASE_URL = "https://bmi41mg6uf.execute-api.us-east-1.amazonaws.com/prod"
API_KEY = "9wx9nHe2NV5vSAOyRps9l3c7PpQ19OttaJqHw4mw"
```

---

## 🧪 Testing

### Test Health Endpoint
```bash
curl -X GET "https://bmi41mg6uf.execute-api.us-east-1.amazonaws.com/prod/api/health"
```

### View Lambda Logs
```bash
aws logs tail /aws/lambda/DocumentPolicyProcessor --follow --region us-east-1
```

### View API Gateway Logs
```bash
aws logs tail /aws/apigateway/DocumentPolicyProcessorAPI/prod --follow --region us-east-1
```

---

## 📊 Monitoring (To Be Configured)

### CloudWatch Log Groups
- Lambda: `/aws/lambda/DocumentPolicyProcessor`
- API Gateway: `/aws/apigateway/DocumentPolicyProcessorAPI/prod`

### Metrics to Monitor
- Lambda invocations
- Lambda errors
- Lambda duration
- API Gateway requests
- API Gateway 4XX/5XX errors
- API Gateway latency

---

## 💰 Cost Estimate

### AWS Free Tier (First 12 Months)
- **Lambda**: 1 million requests/month FREE
- **API Gateway**: 1 million requests/month FREE
- **S3**: 5 GB storage FREE
- **DynamoDB**: 25 GB storage FREE
- **CloudWatch**: 10 custom metrics FREE

### Estimated Monthly Cost (After Free Tier)
- **Lambda**: ~$0.20 per 1000 requests
- **API Gateway**: ~$3.50 per million requests
- **S3**: ~$0.023 per GB
- **DynamoDB**: ~$0.25 per GB
- **Total**: ~$5-10/month for moderate usage

---

## ⚠️ Important Notes

### 1. OpenAI API Key Required
The Lambda function needs an OpenAI API key to process documents. Add it using:

```bash
aws lambda update-function-configuration \
  --function-name DocumentPolicyProcessor \
  --environment "Variables={S3_BUCKET_NAME=document-policy-processor-uploads,DYNAMODB_TABLE_POLICIES=Policies,DYNAMODB_TABLE_JOBS=ProcessingJobs,EMBEDDING_MODEL=all-MiniLM-L6-v2,LLM_MODEL=gpt-3.5-turbo,OPENAI_API_KEY=sk-your-key-here}" \
  --region us-east-1
```

### 2. Lambda Cold Start
First invocation may take 30-60 seconds due to:
- Large container image (~600MB)
- Loading ML models (sentence-transformers, torch)
- Subsequent calls will be faster (warm start)

### 3. API Gateway Timeout
API Gateway has a 29-second timeout. For long-running operations:
- Use asynchronous processing
- Return job ID immediately
- Poll for results using status endpoint

### 4. CORS Configuration
If accessing from a web frontend, enable CORS:
```bash
# Add CORS headers to API Gateway responses
```

---

## 🚀 Next Steps

### 1. Setup CloudWatch Monitoring
```bash
cd document-policy-processor
.\setup-cloudwatch-monitoring.bat
```

### 2. Add More API Endpoints
- POST /api/upload-url - Generate S3 presigned URL
- POST /api/process-document - Process uploaded document
- GET /api/status/{jobId} - Check processing status
- GET /api/results/{jobId} - Get processing results

### 3. Configure Frontend
Update frontend with API URL and key, then deploy:
```bash
cd frontend
streamlit run app.py
```

### 4. Test End-to-End Flow
1. Upload a document
2. Process it through the API
3. Retrieve recommendations

### 5. Record Demo Video
Follow the guide in `demo/VIDEO_CREATION_WALKTHROUGH.md`

---

## 🔗 Useful Links

- **AWS Console**: https://console.aws.amazon.com/
- **Lambda Console**: https://console.aws.amazon.com/lambda/home?region=us-east-1#/functions/DocumentPolicyProcessor
- **API Gateway Console**: https://console.aws.amazon.com/apigateway/home?region=us-east-1#/apis/bmi41mg6uf
- **S3 Console**: https://s3.console.aws.amazon.com/s3/buckets/document-policy-processor-uploads
- **DynamoDB Console**: https://console.aws.amazon.com/dynamodbv2/home?region=us-east-1#tables
- **CloudWatch Console**: https://console.aws.amazon.com/cloudwatch/home?region=us-east-1

---

## 🗑️ Cleanup (After Hackathon)

To delete all resources and avoid charges:

```bash
# Delete Lambda function
aws lambda delete-function --function-name DocumentPolicyProcessor --region us-east-1

# Delete API Gateway
aws apigateway delete-rest-api --rest-api-id bmi41mg6uf --region us-east-1

# Empty and delete S3 bucket
aws s3 rm s3://document-policy-processor-uploads --recursive
aws s3 rb s3://document-policy-processor-uploads

# Delete DynamoDB tables
aws dynamodb delete-table --table-name Policies --region us-east-1
aws dynamodb delete-table --table-name ProcessingJobs --region us-east-1

# Delete IAM roles
aws iam delete-role --role-name DocumentPolicyProcessor-Lambda-dev
aws iam delete-role --role-name DocumentPolicyProcessor-ApiGateway-dev

# Delete ECR repository
aws ecr delete-repository --repository-name document-policy-processor --force --region us-east-1
```

---

**Deployment completed successfully! 🎉**

*Last updated: March 8, 2026*
