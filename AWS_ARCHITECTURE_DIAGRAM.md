# AWS Architecture Diagram - Document Policy Processor

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                          DOCUMENT POLICY PROCESSOR                           │
│                        AWS Architecture Diagram                              │
└─────────────────────────────────────────────────────────────────────────────┘

┌──────────────┐
│   End User   │
│  (Browser)   │
└──────┬───────┘
       │ HTTPS
       ▼
┌──────────────────────────────────────────────────────────────────────────────┐
│                         FRONTEND LAYER                                        │
│  ┌────────────────────────────────────────────────────────────────────┐     │
│  │  Streamlit Cloud                                                    │     │
│  │  • Python Web Application                                           │     │
│  │  • Document Upload Interface                                        │     │
│  │  • Results Display                                                  │     │
│  └────────────────────────────────────────────────────────────────────┘     │
└───────────────────────────────────┬──────────────────────────────────────────┘
                                    │ HTTPS/REST API
                                    │ X-Api-Key Authentication
                                    ▼
┌──────────────────────────────────────────────────────────────────────────────┐
│                         API GATEWAY LAYER                                     │
│  ┌────────────────────────────────────────────────────────────────────┐     │
│  │  Amazon API Gateway (REST API)                                      │     │
│  │  ID: bmi41mg6uf                                                     │     │
│  │  Region: us-east-1                                                  │     │
│  │                                                                      │     │
│  │  Endpoints:                                                          │     │
│  │  • POST /api/upload-url        - Generate presigned S3 URL          │     │
│  │  • POST /api/process-document  - Trigger processing                 │     │
│  │  • GET  /api/status/{jobId}    - Check job status                   │     │
│  │  • GET  /api/results/{jobId}   - Get results                        │     │
│  │  • GET  /api/health            - Health check                       │     │
│  │                                                                      │     │
│  │  Features:                                                           │     │
│  │  • API Key Authentication                                            │     │
│  │  • CORS Enabled                                                      │     │
│  │  • Request/Response Logging                                          │     │
│  └────────────────────────────────────────────────────────────────────┘     │
└───────────────────────────────────┬──────────────────────────────────────────┘
                                    │ Lambda Proxy Integration
                                    ▼
┌──────────────────────────────────────────────────────────────────────────────┐
│                         COMPUTE LAYER                                         │
│  ┌────────────────────────────────────────────────────────────────────┐     │
│  │  AWS Lambda (Container)                                             │     │
│  │  Function: DocumentPolicyProcessor                                  │     │
│  │  Runtime: Python 3.11 (Docker Container)                            │     │
│  │  Memory: 3008 MB (3 GB)                                             │     │
│  │  Timeout: 900 seconds (15 minutes)                                  │     │
│  │  Image: 877786395190.dkr.ecr.us-east-1.amazonaws.com/              │     │
│  │         document-policy-processor:latest                            │     │
│  │                                                                      │     │
│  │  Components:                                                         │     │
│  │  ┌──────────────────────────────────────────────────────────┐      │     │
│  │  │ 1. Text Extractor                                         │      │     │
│  │  │    • Tesseract OCR (images)                               │      │     │
│  │  │    • PyMuPDF (PDFs)                                        │      │     │
│  │  │    • Direct text extraction                                │      │     │
│  │  └──────────────────────────────────────────────────────────┘      │     │
│  │  ┌──────────────────────────────────────────────────────────┐      │     │
│  │  │ 2. Policy Matcher                                          │      │     │
│  │  │    • Sentence Transformers (all-MiniLM-L6-v2)             │      │     │
│  │  │    • 384-dimensional embeddings                            │      │     │
│  │  │    • Cosine similarity matching                            │      │     │
│  │  └──────────────────────────────────────────────────────────┘      │     │
│  │  ┌──────────────────────────────────────────────────────────┐      │     │
│  │  │ 3. LLM Exclusion Checker                                   │      │     │
│  │  │    • Mistral AI (mistral-small-latest)                     │      │     │
│  │  │    • Exclusion analysis                                     │      │     │
│  │  │    • Reasoning generation                                   │      │     │
│  │  └──────────────────────────────────────────────────────────┘      │     │
│  │  ┌──────────────────────────────────────────────────────────┐      │     │
│  │  │ 4. Recommendation Engine                                   │      │     │
│  │  │    • Confidence scoring                                     │      │     │
│  │  │    • Priority assignment                                    │      │     │
│  │  │    • Action determination                                   │      │     │
│  │  └──────────────────────────────────────────────────────────┘      │     │
│  │                                                                      │     │
│  │  Environment Variables:                                              │     │
│  │  • S3_BUCKET_NAME: document-policy-processor-uploads                │     │
│  │  • DYNAMODB_TABLE_POLICIES: Policies                                │     │
│  │  • DYNAMODB_TABLE_JOBS: ProcessingJobs                              │     │
│  │  • EMBEDDING_MODEL: all-MiniLM-L6-v2                                │     │
│  │  • LLM_MODEL: mistral-small-latest                                  │     │
│  │  • MISTRAL_API_KEY: [encrypted]                                     │     │
│  └────────────────────────────────────────────────────────────────────┘     │
└──────┬────────────────┬────────────────┬────────────────┬───────────────────┘
       │                │                │                │
       │                │                │                │
       ▼                ▼                ▼                ▼
┌──────────────┐ ┌──────────────┐ ┌──────────────┐ ┌──────────────────────┐
│              │ │              │ │              │ │                      │
│   Amazon     │ │   Amazon     │ │   Amazon     │ │   Mistral AI API     │
│     S3       │ │  DynamoDB    │ │     ECR      │ │   (External)         │
│              │ │              │ │              │ │                      │
└──────────────┘ └──────────────┘ └──────────────┘ └──────────────────────┘

┌──────────────────────────────────────────────────────────────────────────────┐
│                         STORAGE LAYER                                         │
│                                                                               │
│  ┌────────────────────────────────────────────────────────────────────┐     │
│  │  Amazon S3                                                          │     │
│  │  Bucket: document-policy-processor-uploads                          │     │
│  │  Region: us-east-1                                                  │     │
│  │                                                                      │     │
│  │  Folders:                                                            │     │
│  │  • documents/{jobId}/        - Uploaded documents                   │     │
│  │  • embeddings/               - Policy embeddings (JSON)             │     │
│  │  • results/{jobId}/          - Processing results                   │     │
│  │                                                                      │     │
│  │  Features:                                                           │     │
│  │  • Presigned URLs (1-hour expiration)                               │     │
│  │  • CORS enabled                                                      │     │
│  │  • Server-side encryption (AES-256)                                 │     │
│  │  • Versioning enabled                                                │     │
│  └────────────────────────────────────────────────────────────────────┘     │
│                                                                               │
│  ┌────────────────────────────────────────────────────────────────────┐     │
│  │  Amazon DynamoDB                                                     │     │
│  │  Region: us-east-1                                                   │     │
│  │                                                                      │     │
│  │  Table 1: Policies                                                   │     │
│  │  ├─ Partition Key: policy_id (String)                               │     │
│  │  ├─ Attributes:                                                      │     │
│  │  │  • policy_name                                                    │     │
│  │  │  • description                                                    │     │
│  │  │  • coverage_details                                               │     │
│  │  │  • exclusions                                                     │     │
│  │  │  • embedding_s3_key                                               │     │
│  │  │  • created_at                                                     │     │
│  │  └─ Sample Data: 3 policies (Basic Health, Critical Illness, etc.)  │     │
│  │                                                                      │     │
│  │  Table 2: ProcessingJobs                                             │     │
│  │  ├─ Partition Key: job_id (String)                                  │     │
│  │  ├─ Attributes:                                                      │     │
│  │  │  • status (pending/processing/completed/failed)                   │     │
│  │  │  • document_url                                                   │     │
│  │  │  • symptoms                                                       │     │
│  │  │  • recommendations (List)                                         │     │
│  │  │  • processing_time                                                │     │
│  │  │  • error_message                                                  │     │
│  │  │  • created_at                                                     │     │
│  │  │  • updated_at                                                     │     │
│  │  └─ TTL: 7 days                                                      │     │
│  │                                                                      │     │
│  │  Features:                                                           │     │
│  │  • On-demand capacity                                                │     │
│  │  • Point-in-time recovery                                            │     │
│  │  • Encryption at rest                                                │     │
│  └────────────────────────────────────────────────────────────────────┘     │
│                                                                               │
│  ┌────────────────────────────────────────────────────────────────────┐     │
│  │  Amazon ECR (Elastic Container Registry)                            │     │
│  │  Repository: document-policy-processor                               │     │
│  │  Region: us-east-1                                                   │     │
│  │                                                                      │     │
│  │  Image:                                                              │     │
│  │  • Base: public.ecr.aws/lambda/python:3.11                          │     │
│  │  • Size: ~2.3 GB (includes ML models)                               │     │
│  │  • Layers:                                                           │     │
│  │    - Python dependencies                                             │     │
│  │    - PyTorch (CPU)                                                   │     │
│  │    - Sentence Transformers                                           │     │
│  │    - Tesseract OCR                                                   │     │
│  │    - Application code                                                │     │
│  │                                                                      │     │
│  │  Features:                                                           │     │
│  │  • Image scanning enabled                                            │     │
│  │  • Lifecycle policies                                                │     │
│  │  • Encryption at rest                                                │     │
│  └────────────────────────────────────────────────────────────────────┘     │
└──────────────────────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────────────────────┐
│                         EXTERNAL SERVICES                                     │
│  ┌────────────────────────────────────────────────────────────────────┐     │
│  │  Mistral AI API                                                     │     │
│  │  Endpoint: https://api.mistral.ai/v1                                │     │
│  │  Model: mistral-small-latest                                        │     │
│  │                                                                      │     │
│  │  Usage:                                                              │     │
│  │  • Exclusion checking                                                │     │
│  │  • Reasoning generation                                              │     │
│  │  • Natural language understanding                                    │     │
│  │                                                                      │     │
│  │  Authentication: API Key (stored in Lambda env vars)                │     │
│  └────────────────────────────────────────────────────────────────────┘     │
└──────────────────────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────────────────────┐
│                         MONITORING & LOGGING                                  │
│  ┌────────────────────────────────────────────────────────────────────┐     │
│  │  Amazon CloudWatch                                                   │     │
│  │  Region: us-east-1                                                   │     │
│  │                                                                      │     │
│  │  Log Groups:                                                         │     │
│  │  • /aws/lambda/DocumentPolicyProcessor                              │     │
│  │    - Retention: 7 days                                               │     │
│  │    - Log level: INFO                                                 │     │
│  │    - Includes: Request/response, errors, processing steps           │     │
│  │                                                                      │     │
│  │  • /aws/apigateway/document-policy-processor                        │     │
│  │    - Retention: 7 days                                               │     │
│  │    - Includes: API requests, latency, errors                         │     │
│  │                                                                      │     │
│  │  Metrics:                                                            │     │
│  │  • Lambda: Invocations, Duration, Errors, Throttles                 │     │
│  │  • API Gateway: Count, Latency, 4XX/5XX errors                      │     │
│  │  • DynamoDB: Read/Write capacity, Throttles                         │     │
│  │  • S3: Requests, Bytes transferred                                   │     │
│  │                                                                      │     │
│  │  Alarms:                                                             │     │
│  │  • Lambda errors > 5% (5 minutes)                                    │     │
│  │  • API Gateway 5XX > 10 (5 minutes)                                  │     │
│  │  • Lambda duration > 800s                                            │     │
│  └────────────────────────────────────────────────────────────────────┘     │
└──────────────────────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────────────────────┐
│                         SECURITY & IAM                                        │
│  ┌────────────────────────────────────────────────────────────────────┐     │
│  │  IAM Roles & Policies                                                │     │
│  │                                                                      │     │
│  │  Lambda Execution Role: DocumentPolicyProcessor-Lambda-dev          │     │
│  │  Permissions:                                                        │     │
│  │  • S3: GetObject, PutObject, DeleteObject                           │     │
│  │  • DynamoDB: GetItem, PutItem, UpdateItem, Query, Scan              │     │
│  │  • CloudWatch Logs: CreateLogGroup, CreateLogStream, PutLogEvents   │     │
│  │  • ECR: GetAuthorizationToken, BatchGetImage                        │     │
│  │                                                                      │     │
│  │  API Gateway Execution Role                                          │     │
│  │  Permissions:                                                        │     │
│  │  • Lambda: InvokeFunction                                            │     │
│  │  • CloudWatch Logs: CreateLogGroup, CreateLogStream, PutLogEvents   │     │
│  │                                                                      │     │
│  │  Security Features:                                                  │     │
│  │  • API Key authentication                                            │     │
│  │  • Presigned URLs with expiration                                    │     │
│  │  • Encryption at rest (S3, DynamoDB, ECR)                           │     │
│  │  • Encryption in transit (HTTPS/TLS)                                │     │
│  │  • Least privilege IAM policies                                      │     │
│  │  • No hardcoded credentials                                          │     │
│  └────────────────────────────────────────────────────────────────────┘     │
└──────────────────────────────────────────────────────────────────────────────┘
```

## Data Flow

### 1. Document Upload Flow
```
User → Streamlit → API Gateway → Lambda (generate presigned URL)
                                    ↓
                                  S3 (presigned URL returned)
                                    ↓
User → S3 (direct upload via presigned URL)
```

### 2. Document Processing Flow
```
User → Streamlit → API Gateway → Lambda
                                    ↓
                            ┌───────┴───────┐
                            ▼               ▼
                          S3 (get)    DynamoDB (update status)
                            │
                            ▼
                    Text Extractor
                    (OCR/PDF parsing)
                            │
                            ▼
                    Policy Matcher
                    (embeddings + similarity)
                            │
                            ▼
                    ┌───────┴───────┐
                    ▼               ▼
              DynamoDB (get)   Mistral AI
              (policies)       (exclusion check)
                    │               │
                    └───────┬───────┘
                            ▼
                  Recommendation Engine
                  (scoring + prioritization)
                            │
                            ▼
                    DynamoDB (save results)
                            │
                            ▼
                    Return job_id to user
```

### 3. Results Retrieval Flow
```
User → Streamlit → API Gateway → Lambda
                                    ↓
                            DynamoDB (get results)
                                    ↓
                            Return recommendations
```

## Component Details

### Lambda Function Specifications
- **Runtime**: Python 3.11 (Container)
- **Memory**: 3008 MB (3 GB)
- **Timeout**: 900 seconds (15 minutes)
- **Ephemeral Storage**: 512 MB
- **Architecture**: x86_64
- **Package Type**: Image
- **Cold Start**: 30-90 seconds (loading ML models)
- **Warm Execution**: 10-20 seconds

### API Gateway Specifications
- **Type**: REST API
- **Protocol**: HTTPS
- **Authentication**: API Key (X-Api-Key header)
- **CORS**: Enabled
- **Throttling**: Default AWS limits
- **Caching**: Disabled
- **Stage**: prod

### S3 Bucket Specifications
- **Storage Class**: Standard
- **Encryption**: AES-256 (SSE-S3)
- **Versioning**: Enabled
- **Lifecycle**: 30-day expiration for documents
- **CORS**: Enabled for presigned URLs
- **Public Access**: Blocked

### DynamoDB Specifications
- **Capacity Mode**: On-demand
- **Encryption**: AWS managed keys
- **Point-in-time Recovery**: Enabled
- **TTL**: Enabled (7 days for ProcessingJobs)
- **Backup**: Automatic daily backups

## Network Architecture

```
Internet
   │
   ├─── Streamlit Cloud (Frontend)
   │      │
   │      └─── HTTPS ───┐
   │                    │
   └─── API Gateway ────┤
          (Public)      │
             │          │
             └─── Lambda (VPC optional)
                    │
                    ├─── S3 (via VPC endpoint or public)
                    ├─── DynamoDB (via VPC endpoint or public)
                    ├─── ECR (via VPC endpoint or public)
                    └─── Mistral AI (Internet)
```

## Cost Breakdown (Monthly)

### Free Tier Usage
- **Lambda**: 1M requests, 400,000 GB-seconds free
- **API Gateway**: 1M requests free (first 12 months)
- **S3**: 5GB storage, 20,000 GET, 2,000 PUT free
- **DynamoDB**: 25GB storage, 25 WCU, 25 RCU free
- **CloudWatch**: 5GB logs, 10 custom metrics free

### Estimated Costs (After Free Tier)
- **Lambda**: $5-10/month (moderate usage)
- **API Gateway**: $1-2/month
- **S3**: $1-2/month
- **DynamoDB**: $1-2/month
- **CloudWatch**: $1-2/month
- **Mistral AI**: Variable (pay per token)

**Total**: ~$10-20/month for moderate usage

## Performance Metrics

### Latency
- **API Gateway**: < 100ms
- **Lambda Cold Start**: 30-90 seconds
- **Lambda Warm**: 10-20 seconds
- **S3 Upload**: 1-5 seconds (depends on file size)
- **DynamoDB Query**: < 10ms

### Throughput
- **Concurrent Lambda**: 10+ (can scale to 1000+)
- **API Gateway**: 10,000 requests/second
- **S3**: 3,500 PUT/5,500 GET per second per prefix
- **DynamoDB**: On-demand (auto-scales)

## Scalability

### Horizontal Scaling
- **Lambda**: Auto-scales to 1000+ concurrent executions
- **API Gateway**: Auto-scales to handle traffic
- **S3**: Unlimited storage and throughput
- **DynamoDB**: Auto-scales with on-demand mode

### Vertical Scaling
- **Lambda Memory**: Can increase to 10GB
- **Lambda Timeout**: Can increase to 15 minutes
- **DynamoDB**: Can switch to provisioned capacity

## High Availability

### Multi-AZ Deployment
- **API Gateway**: Multi-AZ by default
- **Lambda**: Multi-AZ by default
- **S3**: Multi-AZ by default (99.99% availability)
- **DynamoDB**: Multi-AZ by default (99.99% availability)

### Disaster Recovery
- **S3**: Cross-region replication (optional)
- **DynamoDB**: Point-in-time recovery, backups
- **Lambda**: Code in ECR (versioned)
- **CloudWatch**: Log retention for 7 days

## Security Best Practices

### Implemented
✅ API Key authentication
✅ HTTPS/TLS encryption in transit
✅ Encryption at rest (S3, DynamoDB, ECR)
✅ Presigned URLs with expiration
✅ Least privilege IAM policies
✅ No hardcoded credentials
✅ CloudWatch logging enabled
✅ VPC endpoints (optional)

### Recommended Enhancements
- [ ] AWS WAF for API Gateway
- [ ] AWS Shield for DDoS protection
- [ ] AWS Secrets Manager for API keys
- [ ] VPC deployment for Lambda
- [ ] S3 bucket policies with IP restrictions
- [ ] CloudTrail for audit logging
- [ ] AWS Config for compliance monitoring

---

**Architecture Version**: 1.0  
**Last Updated**: March 8, 2026  
**Status**: Production Deployed
