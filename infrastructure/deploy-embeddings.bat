@echo off
REM Deploy script for pre-computing policy embeddings (Windows)
REM This script generates embeddings for all policies in DynamoDB and uploads them to S3

setlocal enabledelayedexpansion

echo ========================================================================
echo Pre-compute Policy Embeddings - Deployment Script
echo ========================================================================
echo.

REM Configuration
if "%AWS_REGION%"=="" (
    set REGION=us-east-1
) else (
    set REGION=%AWS_REGION%
)

if "%S3_BUCKET%"=="" (
    set BUCKET=document-policy-processor-uploads
) else (
    set BUCKET=%S3_BUCKET%
)

if "%DYNAMODB_TABLE%"=="" (
    set TABLE=DocumentPolicyProcessor-Policies
) else (
    set TABLE=%DYNAMODB_TABLE%
)

if "%EMBEDDING_MODEL%"=="" (
    set MODEL=all-MiniLM-L6-v2
) else (
    set MODEL=%EMBEDDING_MODEL%
)

echo Configuration:
echo   Region:        %REGION%
echo   S3 Bucket:     %BUCKET%
echo   DynamoDB Table: %TABLE%
echo   Model:         %MODEL%
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo X Python is not installed. Please install Python 3.8 or higher.
    exit /b 1
)
echo + Python is installed

REM Check if AWS CLI is installed
aws --version >nul 2>&1
if errorlevel 1 (
    echo X AWS CLI is not installed. Please install AWS CLI.
    exit /b 1
)
echo + AWS CLI is installed

REM Check AWS credentials
aws sts get-caller-identity >nul 2>&1
if errorlevel 1 (
    echo X AWS credentials are not configured. Please run 'aws configure'.
    exit /b 1
)
echo + AWS credentials are configured

REM Check if requirements are installed
echo.
echo Checking Python dependencies...
python -c "import sentence_transformers" >nul 2>&1
if errorlevel 1 (
    echo ! sentence-transformers not installed. Installing dependencies...
    pip install -r requirements.txt
) else (
    echo + Python dependencies are installed
)

REM Check if DynamoDB table exists
echo.
echo Checking DynamoDB table...
aws dynamodb describe-table --table-name %TABLE% --region %REGION% >nul 2>&1
if errorlevel 1 (
    echo X DynamoDB table '%TABLE%' does not exist.
    echo Please run setup_dynamodb.py first to create the table and populate policies.
    exit /b 1
)
echo + DynamoDB table exists

REM Check if S3 bucket exists
echo.
echo Checking S3 bucket...
aws s3 ls s3://%BUCKET% >nul 2>&1
if errorlevel 1 (
    echo X S3 bucket '%BUCKET%' does not exist.
    echo Please run setup_s3.py first to create the bucket.
    exit /b 1
)
echo + S3 bucket exists

REM Run the precompute embeddings script
echo.
echo ========================================================================
echo Running precompute_embeddings.py...
echo ========================================================================
echo.

python precompute_embeddings.py --region %REGION% --bucket %BUCKET% --table %TABLE% --model %MODEL%

if errorlevel 1 (
    echo.
    echo ========================================================================
    echo X Failed to pre-compute embeddings
    echo ========================================================================
    echo.
    exit /b 1
) else (
    echo.
    echo ========================================================================
    echo + Embeddings pre-computed and uploaded successfully!
    echo ========================================================================
    echo.
    echo Verification:
    echo   aws s3 ls s3://%BUCKET%/embeddings/
    echo.
)

endlocal
