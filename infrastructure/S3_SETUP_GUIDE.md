# S3 Bucket Setup Guide

## Overview

This guide explains how to set up the S3 bucket infrastructure for the Document Policy Processor. The S3 bucket is used to store:

- **documents/**: User-uploaded documents (PDF, PNG, JPG, TXT)
- **embeddings/**: Pre-computed policy embeddings for semantic matching
- **results/**: Processing results and recommendations

## What Was Created

### 1. Python Setup Script (`setup_s3.py`)
A comprehensive Python script that:
- Creates the S3 bucket with proper configuration
- Configures CORS for frontend access
- Creates the folder structure
- Enables versioning for data protection
- Configures lifecycle policies (auto-delete after 30 days)
- Verifies the setup

### 2. CloudFormation Template (`s3-bucket.yaml`)
Infrastructure-as-Code template that defines:
- S3 bucket with encryption and versioning
- CORS configuration
- Lifecycle rules
- Bucket policies for Lambda access
- Security settings (block public access)

### 3. Deployment Scripts
- **deploy-s3.sh**: Bash script for Linux/Mac
- **deploy-s3.bat**: Batch script for Windows
- Both scripts provide interactive deployment with CloudFormation or Python

### 4. Documentation
- **README.md**: Comprehensive infrastructure documentation
- **requirements.txt**: Python dependencies
- **S3_SETUP_GUIDE.md**: This guide

## Quick Start

### Prerequisites

1. **AWS Account**: You need an active AWS account
2. **AWS CLI**: Install from https://aws.amazon.com/cli/
3. **AWS Credentials**: Configure with `aws configure`
4. **Python 3.7+**: For Python script option

### Step 1: Configure AWS Credentials

```bash
aws configure
```

Enter your:
- AWS Access Key ID
- AWS Secret Access Key
- Default region (e.g., us-east-1)
- Default output format (json)

### Step 2: Choose Deployment Method

#### Option A: Quick Deploy (Python Script)

```bash
# Install dependencies
pip install -r infrastructure/requirements.txt

# Run setup script
python infrastructure/setup_s3.py
```

#### Option B: Production Deploy (CloudFormation)

**Linux/Mac:**
```bash
./infrastructure/deploy-s3.sh
```

**Windows:**
```cmd
infrastructure\deploy-s3.bat
```

**Manual CloudFormation:**
```bash
aws cloudformation create-stack \
  --stack-name document-policy-processor-s3 \
  --template-body file://infrastructure/s3-bucket.yaml \
  --parameters ParameterKey=BucketName,ParameterValue=document-policy-processor-uploads \
               ParameterKey=Environment,ParameterValue=dev
```

### Step 3: Verify Setup

```bash
# List bucket contents
aws s3 ls s3://document-policy-processor-uploads/

# Check CORS configuration
aws s3api get-bucket-cors --bucket document-policy-processor-uploads

# Check versioning
aws s3api get-bucket-versioning --bucket document-policy-processor-uploads
```

## Bucket Configuration Details

### CORS Configuration

Allows frontend applications to upload and download files:

```json
{
  "AllowedHeaders": ["*"],
  "AllowedMethods": ["GET", "PUT", "POST", "DELETE", "HEAD"],
  "AllowedOrigins": ["*"],
  "ExposeHeaders": ["ETag"],
  "MaxAgeSeconds": 3000
}
```

**Production Note**: Replace `"*"` in AllowedOrigins with your specific frontend domain.

### Lifecycle Rules

Automatically deletes old files to save costs:

- **documents/**: Deleted after 30 days
- **results/**: Deleted after 30 days
- **embeddings/**: No expiration (persistent)

### Security Settings

- **Encryption**: AES256 server-side encryption
- **Versioning**: Enabled for data recovery
- **Public Access**: Blocked (access via presigned URLs only)
- **Bucket Policy**: Allows Lambda service access

## Folder Structure

```
document-policy-processor-uploads/
│
├── documents/
│   ├── {job_id}_original.pdf
│   ├── {job_id}_original.png
│   └── ...
│
├── embeddings/
│   ├── policy_embeddings.npy
│   ├── policy_metadata.json
│   └── ...
│
└── results/
    ├── {job_id}_result.json
    ├── {job_id}_recommendations.json
    └── ...
```

## Usage in Application

### Upload Document (Python)

```python
import boto3

s3_client = boto3.client('s3')
bucket_name = 'document-policy-processor-uploads'

# Upload file
with open('document.pdf', 'rb') as f:
    s3_client.put_object(
        Bucket=bucket_name,
        Key='documents/job123_original.pdf',
        Body=f,
        ContentType='application/pdf'
    )
```

### Generate Presigned URL (for frontend uploads)

```python
import boto3

s3_client = boto3.client('s3')
bucket_name = 'document-policy-processor-uploads'

# Generate presigned URL (valid for 1 hour)
presigned_url = s3_client.generate_presigned_url(
    'put_object',
    Params={
        'Bucket': bucket_name,
        'Key': 'documents/job123_original.pdf',
        'ContentType': 'application/pdf'
    },
    ExpiresIn=3600
)

# Frontend can now upload directly to this URL
```

### Download File

```python
import boto3

s3_client = boto3.client('s3')
bucket_name = 'document-policy-processor-uploads'

# Download file
s3_client.download_file(
    bucket_name,
    'documents/job123_original.pdf',
    'local_document.pdf'
)
```

### Load Embeddings

```python
import boto3
import numpy as np
import json

s3_client = boto3.client('s3')
bucket_name = 'document-policy-processor-uploads'

# Download embeddings
s3_client.download_file(
    bucket_name,
    'embeddings/policy_embeddings.npy',
    'policy_embeddings.npy'
)

# Load into memory
embeddings = np.load('policy_embeddings.npy')

# Download metadata
response = s3_client.get_object(
    Bucket=bucket_name,
    Key='embeddings/policy_metadata.json'
)
metadata = json.loads(response['Body'].read())
```

## Troubleshooting

### Error: Bucket name already exists

S3 bucket names are globally unique across all AWS accounts. Solutions:

1. **Add suffix**: `document-policy-processor-uploads-{your-account-id}`
2. **Add random string**: `document-policy-processor-uploads-abc123`
3. **Use different name**: `my-doc-policy-processor-uploads`

Update the bucket name in:
- `setup_s3.py`: Change `BUCKET_NAME` variable
- `s3-bucket.yaml`: Change `BucketName` parameter default
- `deploy-s3.sh` / `deploy-s3.bat`: Change `BUCKET_NAME` variable

### Error: Access Denied

Ensure your AWS user/role has these permissions:

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "s3:CreateBucket",
        "s3:PutBucketCors",
        "s3:PutBucketVersioning",
        "s3:PutLifecycleConfiguration",
        "s3:PutBucketPolicy",
        "s3:PutBucketEncryption",
        "s3:PutObject"
      ],
      "Resource": [
        "arn:aws:s3:::document-policy-processor-uploads",
        "arn:aws:s3:::document-policy-processor-uploads/*"
      ]
    }
  ]
}
```

### Error: CORS not working

1. Verify CORS configuration:
   ```bash
   aws s3api get-bucket-cors --bucket document-policy-processor-uploads
   ```

2. Check browser console for CORS errors

3. Ensure frontend sends correct Origin header

4. For production, update AllowedOrigins to your domain:
   ```yaml
   AllowedOrigins:
     - 'https://your-frontend-domain.com'
   ```

### Error: CloudFormation stack failed

1. Check stack events:
   ```bash
   aws cloudformation describe-stack-events \
     --stack-name document-policy-processor-s3 \
     --max-items 10
   ```

2. Common issues:
   - Bucket name already exists
   - Insufficient permissions
   - Invalid parameter values

3. Delete failed stack and retry:
   ```bash
   aws cloudformation delete-stack \
     --stack-name document-policy-processor-s3
   ```

## Cost Estimation

### S3 Storage Costs (us-east-1)

- **Storage**: $0.023 per GB/month
- **PUT requests**: $0.005 per 1,000 requests
- **GET requests**: $0.0004 per 1,000 requests

### Example Monthly Cost

Assuming:
- 1,000 documents uploaded (avg 2MB each) = 2GB
- 10,000 API requests
- Lifecycle deletes after 30 days

**Estimated cost**: ~$0.10 - $0.50 per month

### Cost Optimization

1. **Lifecycle policies**: Auto-delete old files (already configured)
2. **Intelligent-Tiering**: Move infrequently accessed files to cheaper storage
3. **Compression**: Compress embeddings before upload
4. **Monitoring**: Set up billing alerts

## Next Steps

After S3 setup is complete:

1. ✅ **Task 2.1**: S3 buckets created
2. ⏭️ **Task 2.2**: Create DynamoDB tables
3. ⏭️ **Task 2.3**: Set up IAM roles
4. ⏭️ **Task 3.1**: Implement text extraction module
5. ⏭️ **Task 4.2**: Pre-compute and upload policy embeddings

## Additional Resources

- [AWS S3 Documentation](https://docs.aws.amazon.com/s3/)
- [S3 Best Practices](https://docs.aws.amazon.com/AmazonS3/latest/userguide/security-best-practices.html)
- [S3 Pricing](https://aws.amazon.com/s3/pricing/)
- [CloudFormation S3 Reference](https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-s3-bucket.html)
- [Boto3 S3 Documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/s3.html)

## Support

For issues or questions:
1. Check the troubleshooting section above
2. Review AWS CloudWatch logs
3. Check AWS CloudFormation events
4. Consult AWS documentation
5. Ask the development team

---

**Task Status**: ✅ Task 2.1 Complete - S3 buckets for document storage and embeddings created
