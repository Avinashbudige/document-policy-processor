#!/bin/bash
# Deploy script for pre-computing policy embeddings
# This script generates embeddings for all policies in DynamoDB and uploads them to S3

set -e  # Exit on error

echo "========================================================================"
echo "Pre-compute Policy Embeddings - Deployment Script"
echo "========================================================================"
echo ""

# Configuration
REGION="${AWS_REGION:-us-east-1}"
BUCKET="${S3_BUCKET:-document-policy-processor-uploads}"
TABLE="${DYNAMODB_TABLE:-DocumentPolicyProcessor-Policies}"
MODEL="${EMBEDDING_MODEL:-all-MiniLM-L6-v2}"

echo "Configuration:"
echo "  Region:        $REGION"
echo "  S3 Bucket:     $BUCKET"
echo "  DynamoDB Table: $TABLE"
echo "  Model:         $MODEL"
echo ""

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "✗ Python 3 is not installed. Please install Python 3.8 or higher."
    exit 1
fi

echo "✓ Python 3 is installed"

# Check if AWS CLI is installed
if ! command -v aws &> /dev/null; then
    echo "✗ AWS CLI is not installed. Please install AWS CLI."
    exit 1
fi

echo "✓ AWS CLI is installed"

# Check AWS credentials
if ! aws sts get-caller-identity &> /dev/null; then
    echo "✗ AWS credentials are not configured. Please run 'aws configure'."
    exit 1
fi

echo "✓ AWS credentials are configured"

# Check if requirements are installed
echo ""
echo "Checking Python dependencies..."
if ! python3 -c "import sentence_transformers" &> /dev/null; then
    echo "⚠ sentence-transformers not installed. Installing dependencies..."
    pip install -r requirements.txt
else
    echo "✓ Python dependencies are installed"
fi

# Check if DynamoDB table exists
echo ""
echo "Checking DynamoDB table..."
if ! aws dynamodb describe-table --table-name "$TABLE" --region "$REGION" &> /dev/null; then
    echo "✗ DynamoDB table '$TABLE' does not exist."
    echo "Please run setup_dynamodb.py first to create the table and populate policies."
    exit 1
fi

echo "✓ DynamoDB table exists"

# Check if S3 bucket exists
echo ""
echo "Checking S3 bucket..."
if ! aws s3 ls "s3://$BUCKET" &> /dev/null; then
    echo "✗ S3 bucket '$BUCKET' does not exist."
    echo "Please run setup_s3.py first to create the bucket."
    exit 1
fi

echo "✓ S3 bucket exists"

# Run the precompute embeddings script
echo ""
echo "========================================================================"
echo "Running precompute_embeddings.py..."
echo "========================================================================"
echo ""

python3 precompute_embeddings.py \
    --region "$REGION" \
    --bucket "$BUCKET" \
    --table "$TABLE" \
    --model "$MODEL"

exit_code=$?

if [ $exit_code -eq 0 ]; then
    echo ""
    echo "========================================================================"
    echo "✓ Embeddings pre-computed and uploaded successfully!"
    echo "========================================================================"
    echo ""
    echo "Verification:"
    echo "  aws s3 ls s3://$BUCKET/embeddings/"
    echo ""
else
    echo ""
    echo "========================================================================"
    echo "✗ Failed to pre-compute embeddings"
    echo "========================================================================"
    echo ""
    exit $exit_code
fi
