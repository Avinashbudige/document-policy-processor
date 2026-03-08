# Policy Embeddings Setup Guide

This guide explains how to pre-compute policy embeddings for the Document Policy Processor. Pre-computing embeddings enables fast semantic matching during document processing without needing to generate embeddings on-the-fly.

## Overview

The pre-compute embeddings process:
1. Fetches all policies from DynamoDB
2. Generates semantic embeddings using sentence-transformers
3. Stores embeddings and metadata in S3 for fast retrieval

## Prerequisites

Before running the embeddings script, ensure you have:

### 1. AWS Infrastructure Setup

- ✓ S3 bucket created (`document-policy-processor-uploads`)
- ✓ DynamoDB Policies table created and populated
- ✓ AWS credentials configured with appropriate permissions

### 2. Python Environment

- Python 3.8 or higher
- Required packages (install with `pip install -r requirements.txt`):
  - `boto3` - AWS SDK
  - `sentence-transformers` - Embedding generation
  - `numpy` - Numerical operations
  - `torch` - PyTorch (required by sentence-transformers)

### 3. AWS Permissions

Your AWS credentials need these permissions:
- `dynamodb:Scan` on the Policies table
- `s3:PutObject` on the S3 bucket
- `s3:GetObject` on the S3 bucket (for verification)

## Quick Start

### Option 1: Using Deployment Script (Recommended)

**On Linux/Mac:**
```bash
cd infrastructure
chmod +x deploy-embeddings.sh
./deploy-embeddings.sh
```

**On Windows:**
```cmd
cd infrastructure
deploy-embeddings.bat
```

The script will:
- Check prerequisites
- Install dependencies if needed
- Run the embeddings generation
- Verify the upload

### Option 2: Manual Execution

```bash
cd infrastructure

# Install dependencies
pip install -r requirements.txt

# Run the script with default settings
python precompute_embeddings.py

# Or with custom parameters
python precompute_embeddings.py \
  --region us-east-1 \
  --bucket document-policy-processor-uploads \
  --table DocumentPolicyProcessor-Policies \
  --model all-MiniLM-L6-v2
```

## Command-Line Options

```
python precompute_embeddings.py [OPTIONS]

Options:
  --region REGION       AWS region (default: us-east-1)
  --bucket BUCKET       S3 bucket name (default: document-policy-processor-uploads)
  --table TABLE         DynamoDB table name (default: DocumentPolicyProcessor-Policies)
  --model MODEL         Embedding model name (default: all-MiniLM-L6-v2)
  -h, --help           Show help message
```

## Output Files

The script creates three files in S3:

### 1. policy_embeddings.json

Contains the embedding vectors for each policy:

```json
{
  "POL-001": [0.123, -0.456, 0.789, ...],
  "POL-002": [0.234, -0.567, 0.890, ...],
  ...
}
```

- **Location**: `s3://bucket-name/embeddings/policy_embeddings.json`
- **Format**: JSON object mapping policy_id to embedding vector (list of floats)
- **Size**: ~150KB for 10 policies (384-dimensional embeddings)

### 2. policy_metadata.json

Contains the full policy information:

```json
{
  "POL-001": {
    "policy_id": "POL-001",
    "policy_name": "Basic Health Insurance",
    "policy_text": "Covers hospitalization, surgery, and emergency care...",
    "category": "health",
    "coverage_details": {
      "hospitalization": true,
      "surgery": true,
      ...
    },
    "exclusions": [
      "Pre-existing conditions (first 2 years)",
      ...
    ],
    "created_at": "2026-01-24T12:00:00.000000"
  },
  ...
}
```

- **Location**: `s3://bucket-name/embeddings/policy_metadata.json`
- **Format**: JSON object mapping policy_id to policy metadata
- **Size**: ~20KB for 10 policies

### 3. embeddings_info.json

Contains summary information:

```json
{
  "model_name": "all-MiniLM-L6-v2",
  "embedding_dimension": 384,
  "num_policies": 10,
  "policy_ids": ["POL-001", "POL-002", ...],
  "generated_at": "2026-01-24T12:00:00.000000"
}
```

- **Location**: `s3://bucket-name/embeddings/embeddings_info.json`
- **Format**: JSON object with metadata about the embeddings
- **Size**: ~1KB

## Verification

After running the script, verify the embeddings were uploaded:

```bash
# List files in embeddings folder
aws s3 ls s3://document-policy-processor-uploads/embeddings/

# Expected output:
# 2026-01-24 12:00:00     150000 policy_embeddings.json
# 2026-01-24 12:00:00      20000 policy_metadata.json
# 2026-01-24 12:00:00       1000 embeddings_info.json

# Download and inspect embeddings info
aws s3 cp s3://document-policy-processor-uploads/embeddings/embeddings_info.json - | python -m json.tool

# Download and check embeddings count
aws s3 cp s3://document-policy-processor-uploads/embeddings/policy_embeddings.json - | python -c "import json, sys; data=json.load(sys.stdin); print(f'Embeddings: {len(data)}')"
```

## Using Embeddings in Lambda

Once embeddings are pre-computed, use them in your Lambda function:

```python
from policy_matcher import PolicyMatcher

# Initialize matcher
matcher = PolicyMatcher(embedding_model='all-MiniLM-L6-v2')

# Load pre-computed embeddings from S3 (cached in Lambda memory)
matcher.load_policy_embeddings(
    bucket_name='document-policy-processor-uploads',
    embeddings_key='embeddings/policy_embeddings.json',
    metadata_key='embeddings/policy_metadata.json'
)

# Generate embedding for query text
query_text = "I need surgery coverage for my heart condition"
query_embedding = matcher.generate_embedding(query_text)

# Find similar policies
matches = matcher.find_similar_policies(
    query_embedding, 
    top_k=5,
    threshold=0.6
)

# Process matches
for match in matches:
    print(f"Policy: {match.policy_name}")
    print(f"Similarity: {match.similarity_score:.2f}")
    print(f"Text: {match.policy_text}")
```

## Embedding Model

### Default Model: all-MiniLM-L6-v2

- **Dimension**: 384
- **Size**: ~80MB
- **Speed**: Fast (suitable for Lambda)
- **Quality**: Good for semantic similarity
- **Source**: [sentence-transformers/all-MiniLM-L6-v2](https://huggingface.co/sentence-transformers/all-MiniLM-L6-v2)

### Alternative Models

You can use different models by specifying the `--model` parameter:

```bash
# Larger, more accurate model (768 dimensions)
python precompute_embeddings.py --model all-mpnet-base-v2

# Smaller, faster model (256 dimensions)
python precompute_embeddings.py --model paraphrase-MiniLM-L3-v2
```

**Note**: If you change the model, you must:
1. Re-generate all embeddings
2. Update the model name in your Lambda function
3. Ensure Lambda has enough memory for the model

## Troubleshooting

### Error: "No policies found in DynamoDB table"

**Cause**: The DynamoDB table is empty or doesn't exist.

**Solution**:
```bash
# Create table and populate with sample policies
python infrastructure/setup_dynamodb.py
```

### Error: "Failed to upload embeddings to S3"

**Cause**: S3 bucket doesn't exist or insufficient permissions.

**Solution**:
```bash
# Create S3 bucket
python infrastructure/setup_s3.py

# Or check IAM permissions
aws iam get-user-policy --user-name YOUR_USER --policy-name YOUR_POLICY
```

### Error: "Model download failed"

**Cause**: No internet connection or HuggingFace Hub is unreachable.

**Solution**:
- Ensure internet connection is available
- The model (~80MB) will be downloaded on first run
- Model is cached locally in `~/.cache/torch/sentence_transformers/`
- Subsequent runs will use the cached model

### Error: "Memory error" or "Out of memory"

**Cause**: Not enough RAM to load all policies and generate embeddings.

**Solution**:
- For large policy databases (>1000 policies), modify the script to process in batches
- Close other applications to free up memory
- Use a machine with more RAM

### Warning: "Verification failed"

**Cause**: Mismatch between embeddings and metadata files.

**Solution**:
- Re-run the script to regenerate both files
- Check S3 bucket for partial uploads
- Verify network connection during upload

## Performance

### Generation Time

- **10 policies**: ~5-10 seconds
- **100 policies**: ~30-60 seconds
- **1000 policies**: ~5-10 minutes

Time includes:
- Model loading (~2 seconds)
- DynamoDB scan (~1 second)
- Embedding generation (varies by policy length)
- S3 upload (~1 second)

### Lambda Cold Start

When Lambda loads embeddings:
- **First invocation (cold start)**: ~2-3 seconds
- **Subsequent invocations (warm)**: <100ms (cached in memory)

## Re-generating Embeddings

You should re-generate embeddings when:

1. **New policies added**: After adding policies to DynamoDB
2. **Policies updated**: After modifying policy text
3. **Model changed**: When switching to a different embedding model
4. **Periodic refresh**: Monthly or quarterly to ensure consistency

To re-generate:
```bash
# Simply run the script again - it will overwrite existing files
python precompute_embeddings.py
```

## Best Practices

1. **Version Control**: Keep track of which model version was used
2. **Backup**: Store embeddings in version-controlled S3 bucket
3. **Monitoring**: Set up CloudWatch alarms for S3 upload failures
4. **Testing**: Test embeddings with sample queries before deploying
5. **Documentation**: Document when embeddings were last generated

## Integration with CI/CD

Add embeddings generation to your deployment pipeline:

```yaml
# Example GitHub Actions workflow
- name: Pre-compute embeddings
  run: |
    cd infrastructure
    python precompute_embeddings.py \
      --region ${{ secrets.AWS_REGION }} \
      --bucket ${{ secrets.S3_BUCKET }} \
      --table ${{ secrets.DYNAMODB_TABLE }}
```

## Cost Considerations

### AWS Costs

- **DynamoDB Scan**: ~$0.00025 per scan (10 policies)
- **S3 Storage**: ~$0.023 per GB per month (~0.2MB = negligible)
- **S3 PUT Requests**: ~$0.005 per 1000 requests (3 files = negligible)
- **Data Transfer**: Free within same region

**Total cost**: < $0.01 per run

### Compute Costs

- **Local execution**: Free (uses your machine)
- **Lambda execution**: Not applicable (run locally, not in Lambda)

## Next Steps

After pre-computing embeddings:

1. ✓ Embeddings generated and uploaded to S3
2. → Implement Lambda function that uses PolicyMatcher
3. → Test semantic matching with sample queries
4. → Deploy Lambda function with API Gateway
5. → Monitor embedding cache performance in CloudWatch

## Resources

- [Sentence Transformers Documentation](https://www.sbert.net/)
- [all-MiniLM-L6-v2 Model Card](https://huggingface.co/sentence-transformers/all-MiniLM-L6-v2)
- [AWS S3 Documentation](https://docs.aws.amazon.com/s3/)
- [AWS DynamoDB Documentation](https://docs.aws.amazon.com/dynamodb/)
