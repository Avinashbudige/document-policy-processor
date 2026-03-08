#!/bin/bash

# Deployment Validation Script
# Checks if all prerequisites are met before deployment

set -e

echo "=========================================="
echo "Deployment Prerequisites Validation"
echo "=========================================="

ERRORS=0
WARNINGS=0

# Check Docker
echo ""
echo "Checking Docker..."
if command -v docker &> /dev/null; then
    echo "✓ Docker is installed"
    if docker info &> /dev/null; then
        echo "✓ Docker daemon is running"
        DOCKER_VERSION=$(docker --version)
        echo "  Version: $DOCKER_VERSION"
    else
        echo "✗ Docker daemon is not running"
        ERRORS=$((ERRORS + 1))
    fi
else
    echo "✗ Docker is not installed"
    ERRORS=$((ERRORS + 1))
fi

# Check AWS CLI
echo ""
echo "Checking AWS CLI..."
if command -v aws &> /dev/null; then
    echo "✓ AWS CLI is installed"
    AWS_VERSION=$(aws --version)
    echo "  Version: $AWS_VERSION"
    
    # Check AWS credentials
    if aws sts get-caller-identity &> /dev/null; then
        echo "✓ AWS credentials are configured"
        AWS_ACCOUNT=$(aws sts get-caller-identity --query Account --output text)
        AWS_USER=$(aws sts get-caller-identity --query Arn --output text)
        echo "  Account: $AWS_ACCOUNT"
        echo "  User: $AWS_USER"
    else
        echo "✗ AWS credentials are not configured"
        ERRORS=$((ERRORS + 1))
    fi
else
    echo "✗ AWS CLI is not installed"
    ERRORS=$((ERRORS + 1))
fi

# Check required files
echo ""
echo "Checking required files..."
REQUIRED_FILES=(
    "Dockerfile"
    "src/requirements.txt"
    "src/lambda_handler.py"
    "src/text_extractor.py"
    "src/policy_matcher.py"
    "src/llm_exclusion_checker.py"
    "src/recommendation_engine.py"
)

for file in "${REQUIRED_FILES[@]}"; do
    if [ -f "$file" ]; then
        echo "✓ $file exists"
    else
        echo "✗ $file is missing"
        ERRORS=$((ERRORS + 1))
    fi
done

# Check infrastructure
echo ""
echo "Checking AWS infrastructure..."

# Check S3 bucket
S3_BUCKET="document-policy-processor-uploads"
if aws s3 ls "s3://$S3_BUCKET" &> /dev/null; then
    echo "✓ S3 bucket exists: $S3_BUCKET"
else
    echo "⚠ S3 bucket not found: $S3_BUCKET"
    echo "  Run infrastructure setup scripts first"
    WARNINGS=$((WARNINGS + 1))
fi

# Check DynamoDB tables
DYNAMODB_TABLES=("Policies" "ProcessingJobs")
for table in "${DYNAMODB_TABLES[@]}"; do
    if aws dynamodb describe-table --table-name "$table" &> /dev/null 2>&1; then
        echo "✓ DynamoDB table exists: $table"
    else
        echo "⚠ DynamoDB table not found: $table"
        echo "  Run infrastructure setup scripts first"
        WARNINGS=$((WARNINGS + 1))
    fi
done

# Check IAM role
IAM_ROLE="DocumentPolicyProcessorLambdaRole"
if aws iam get-role --role-name "$IAM_ROLE" &> /dev/null 2>&1; then
    echo "✓ IAM role exists: $IAM_ROLE"
else
    echo "⚠ IAM role not found: $IAM_ROLE"
    echo "  Run infrastructure setup scripts first"
    WARNINGS=$((WARNINGS + 1))
fi

# Check environment variables
echo ""
echo "Checking environment variables..."

if [ -n "$OPENAI_API_KEY" ]; then
    echo "✓ OPENAI_API_KEY is set"
else
    echo "⚠ OPENAI_API_KEY is not set"
    echo "  Set this before deployment or configure in Lambda"
    WARNINGS=$((WARNINGS + 1))
fi

# Check disk space
echo ""
echo "Checking disk space..."
AVAILABLE_SPACE=$(df -h . | awk 'NR==2 {print $4}')
echo "  Available space: $AVAILABLE_SPACE"
echo "  Required: ~5GB for Docker build"

# Summary
echo ""
echo "=========================================="
echo "Validation Summary"
echo "=========================================="
echo "Errors: $ERRORS"
echo "Warnings: $WARNINGS"
echo ""

if [ $ERRORS -eq 0 ]; then
    if [ $WARNINGS -eq 0 ]; then
        echo "✓ All checks passed! Ready to deploy."
        echo ""
        echo "To deploy, run:"
        echo "  ./deploy-lambda.sh"
        exit 0
    else
        echo "⚠ Some warnings found. You can proceed but may encounter issues."
        echo ""
        echo "To deploy anyway, run:"
        echo "  ./deploy-lambda.sh"
        exit 0
    fi
else
    echo "✗ Validation failed. Please fix the errors above before deploying."
    exit 1
fi
