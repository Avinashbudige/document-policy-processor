# Infrastructure Setup

This directory contains infrastructure-as-code files for setting up AWS resources for the Document Policy Processor.

## S3 Bucket Setup

The S3 bucket stores uploaded documents, pre-computed policy embeddings, and processing results.

### Bucket Structure

```
document-policy-processor-uploads/
├── documents/          # User-uploaded documents (PDF, PNG, JPG, TXT)
├── embeddings/         # Pre-computed policy embeddings (numpy arrays)
└── results/            # Processing results (JSON files)
```

### Configuration

- **CORS**: Enabled for frontend access (all origins in dev, restrict in production)
- **Versioning**: Enabled for data protection
- **Lifecycle**: Auto-delete documents and results after 30 days
- **Encryption**: Server-side encryption (AES256)
- **Public Access**: Blocked (access via presigned URLs only)

## Deployment Options

### Option 1: Python Script (Quickest)

Use the Python script for quick setup:

```bash
# Install boto3 if not already installed
pip install boto3

# Configure AWS credentials
aws configure

# Run the setup script
python infrastructure/setup_s3.py
```

The script will:
1. Create the S3 bucket
2. Configure CORS
3. Create folder structure
4. Enable versioning
5. Configure lifecycle policies
6. Verify the setup

### Option 2: CloudFormation (Recommended for Production)

Use CloudFormation for reproducible infrastructure:

```bash
# Deploy the stack
aws cloudformation create-stack \
  --stack-name document-policy-processor-s3 \
  --template-body file://infrastructure/s3-bucket.yaml \
  --parameters ParameterKey=BucketName,ParameterValue=document-policy-processor-uploads \
               ParameterKey=Environment,ParameterValue=dev

# Check stack status
aws cloudformation describe-stacks \
  --stack-name document-policy-processor-s3 \
  --query 'Stacks[0].StackStatus'

# Get outputs
aws cloudformation describe-stacks \
  --stack-name document-policy-processor-s3 \
  --query 'Stacks[0].Outputs'
```

To update the stack:

```bash
aws cloudformation update-stack \
  --stack-name document-policy-processor-s3 \
  --template-body file://infrastructure/s3-bucket.yaml
```

To delete the stack:

```bash
# Empty the bucket first
aws s3 rm s3://document-policy-processor-uploads --recursive

# Delete the stack
aws cloudformation delete-stack \
  --stack-name document-policy-processor-s3
```

### Option 3: AWS Console (Manual)

1. Go to [S3 Console](https://s3.console.aws.amazon.com/s3/)
2. Click "Create bucket"
3. Bucket name: `document-policy-processor-uploads`
4. Region: Choose your preferred region
5. Enable "Bucket Versioning"
6. Enable "Server-side encryption" (AES256)
7. Block all public access
8. Click "Create bucket"
9. Go to bucket → Permissions → CORS configuration
10. Add the CORS configuration from `s3-bucket.yaml`
11. Go to Management → Lifecycle rules
12. Add lifecycle rules for documents/ and results/ folders (30 days expiration)
13. Create folders: Upload empty files named `documents/`, `embeddings/`, `results/`

## Verification

After deployment, verify the setup:

```bash
# Check bucket exists
aws s3 ls s3://document-policy-processor-uploads/

# Check CORS configuration
aws s3api get-bucket-cors --bucket document-policy-processor-uploads

# Check versioning
aws s3api get-bucket-versioning --bucket document-policy-processor-uploads

# Check lifecycle configuration
aws s3api get-bucket-lifecycle-configuration --bucket document-policy-processor-uploads
```

## Creating Folder Structure

S3 doesn't have real folders, but we create empty objects with trailing slashes:

```bash
# Create folders using AWS CLI
aws s3api put-object --bucket document-policy-processor-uploads --key documents/
aws s3api put-object --bucket document-policy-processor-uploads --key embeddings/
aws s3api put-object --bucket document-policy-processor-uploads --key results/
```

Or use the Python script which handles this automatically.

## Security Considerations

### Development Environment
- CORS allows all origins (`*`) for easy testing
- Bucket is private (no public access)
- Access via presigned URLs or IAM roles

### Production Environment
- Update CORS to allow only your frontend domain
- Use CloudFront for content delivery
- Enable CloudTrail logging for audit
- Use KMS encryption instead of AES256
- Implement bucket policies for least privilege access

## Troubleshooting

### Bucket Name Already Exists
S3 bucket names are globally unique. If the name is taken:
1. Choose a different name (e.g., add your AWS account ID or random suffix)
2. Update `BUCKET_NAME` in `setup_s3.py` or `BucketName` parameter in CloudFormation

### Permission Denied
Ensure your AWS credentials have these permissions:
- `s3:CreateBucket`
- `s3:PutBucketCors`
- `s3:PutBucketVersioning`
- `s3:PutLifecycleConfiguration`
- `s3:PutObject`

### CORS Not Working
- Verify CORS configuration: `aws s3api get-bucket-cors --bucket <bucket-name>`
- Check that your frontend is sending the correct Origin header
- Ensure AllowedOrigins includes your frontend domain

## DynamoDB Tables Setup

The Document Policy Processor uses two DynamoDB tables for storing policy data and tracking processing jobs.

### Quick Setup

**On Linux/Mac:**
```bash
cd infrastructure
chmod +x deploy-dynamodb.sh
./deploy-dynamodb.sh
```

**On Windows:**
```cmd
cd infrastructure
deploy-dynamodb.bat
```

See [DYNAMODB_SETUP_GUIDE.md](DYNAMODB_SETUP_GUIDE.md) for detailed instructions.

### Tables Created

1. **DocumentPolicyProcessor-Policies**
   - Stores insurance policy information
   - Partition Key: `policy_id`
   - Includes 10 sample policies

2. **DocumentPolicyProcessor-ProcessingJobs**
   - Tracks document processing jobs
   - Partition Key: `job_id`
   - TTL enabled (7 days auto-cleanup)

## IAM Roles Setup

The Document Policy Processor requires IAM roles for Lambda and API Gateway to access AWS services.

### Quick Setup

**On Linux/Mac:**
```bash
cd infrastructure
chmod +x deploy-iam.sh
./deploy-iam.sh
```

**On Windows:**
```cmd
cd infrastructure
deploy-iam.bat
```

See [IAM_SETUP_GUIDE.md](IAM_SETUP_GUIDE.md) for detailed instructions.

### Roles Created

1. **DocumentPolicyProcessor-Lambda-dev**
   - Lambda execution role with S3, DynamoDB, Textract, CloudWatch permissions

2. **DocumentPolicyProcessor-ApiGateway-dev**
   - API Gateway role for Lambda invocation and logging

## Pre-computing Policy Embeddings

After setting up S3 and DynamoDB, you need to pre-compute embeddings for all policies in the database. This enables fast semantic matching during document processing.

### Prerequisites

1. S3 bucket created and configured
2. DynamoDB Policies table populated with sample policies
3. Python dependencies installed:
   ```bash
   pip install -r requirements.txt
   ```

### Running the Script

**Basic usage (uses defaults):**
```bash
python infrastructure/precompute_embeddings.py
```

**With custom parameters:**
```bash
python infrastructure/precompute_embeddings.py \
  --region us-east-1 \
  --bucket document-policy-processor-uploads \
  --table DocumentPolicyProcessor-Policies \
  --model all-MiniLM-L6-v2
```

### What the Script Does

1. **Fetches policies** from DynamoDB table
2. **Generates embeddings** using sentence-transformers model (all-MiniLM-L6-v2)
3. **Uploads to S3**:
   - `embeddings/policy_embeddings.json` - Embedding vectors for each policy
   - `embeddings/policy_metadata.json` - Policy metadata (text, category, exclusions)
   - `embeddings/embeddings_info.json` - Summary information

### Output Files

**policy_embeddings.json:**
```json
{
  "POL-001": [0.123, -0.456, 0.789, ...],
  "POL-002": [0.234, -0.567, 0.890, ...],
  ...
}
```

**policy_metadata.json:**
```json
{
  "POL-001": {
    "policy_id": "POL-001",
    "policy_name": "Basic Health Insurance",
    "policy_text": "Covers hospitalization...",
    "category": "health",
    "coverage_details": {...},
    "exclusions": [...]
  },
  ...
}
```

**embeddings_info.json:**
```json
{
  "model_name": "all-MiniLM-L6-v2",
  "embedding_dimension": 384,
  "num_policies": 10,
  "policy_ids": ["POL-001", "POL-002", ...],
  "generated_at": "2026-01-24T..."
}
```

### Verification

After running the script, verify the embeddings were uploaded:

```bash
# List files in embeddings folder
aws s3 ls s3://document-policy-processor-uploads/embeddings/

# Download and inspect embeddings info
aws s3 cp s3://document-policy-processor-uploads/embeddings/embeddings_info.json - | python -m json.tool
```

### Using Embeddings in Lambda

The PolicyMatcher class automatically loads these embeddings:

```python
from policy_matcher import PolicyMatcher

# Initialize matcher
matcher = PolicyMatcher(embedding_model='all-MiniLM-L6-v2')

# Load pre-computed embeddings from S3
matcher.load_policy_embeddings(
    bucket_name='document-policy-processor-uploads',
    embeddings_key='embeddings/policy_embeddings.json',
    metadata_key='embeddings/policy_metadata.json'
)

# Generate embedding for query text
query_embedding = matcher.generate_embedding("I need surgery coverage")

# Find similar policies
matches = matcher.find_similar_policies(query_embedding, top_k=5)
```

### Troubleshooting

**Error: "No policies found in DynamoDB table"**
- Run `python infrastructure/setup_dynamodb.py` first to populate sample policies

**Error: "Failed to upload embeddings to S3"**
- Verify S3 bucket exists: `aws s3 ls s3://document-policy-processor-uploads/`
- Check IAM permissions for S3 PutObject

**Error: "Model download failed"**
- Ensure internet connection is available
- The sentence-transformers model (~80MB) will be downloaded on first run
- Model is cached locally for subsequent runs

**Memory issues**
- The script loads all policies into memory
- For large policy databases (>1000 policies), consider batch processing

### Re-generating Embeddings

You should re-generate embeddings when:
- New policies are added to DynamoDB
- Existing policies are updated
- You want to use a different embedding model

Simply run the script again - it will overwrite the existing files in S3.

## Next Steps

After setting up infrastructure:
1. ✓ S3 bucket created
2. ✓ DynamoDB tables created
3. ✓ IAM roles created
4. ✓ Policy embeddings pre-computed
5. → Create Lambda functions (task 8.1)
6. → Configure API Gateway (task 9.1)
7. → Implement document processing logic

## Resources

- [AWS S3 Documentation](https://docs.aws.amazon.com/s3/)
- [S3 CORS Configuration](https://docs.aws.amazon.com/AmazonS3/latest/userguide/cors.html)
- [S3 Lifecycle Configuration](https://docs.aws.amazon.com/AmazonS3/latest/userguide/object-lifecycle-mgmt.html)
- [CloudFormation S3 Reference](https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-s3-bucket.html)
