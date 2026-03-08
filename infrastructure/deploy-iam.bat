@echo off
REM Deploy IAM roles for Document Policy Processor
REM This script can use either CloudFormation or Python boto3

setlocal enabledelayedexpansion

echo ==========================================
echo Document Policy Processor - IAM Setup
echo ==========================================
echo.

REM Configuration
set STACK_NAME=document-policy-processor-iam
set TEMPLATE_FILE=iam-roles.yaml
set ENVIRONMENT=dev
set S3_BUCKET_NAME=document-policy-processor-uploads

REM Check if AWS CLI is installed
where aws >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo ❌ AWS CLI is not installed. Please install it first.
    echo    Visit: https://aws.amazon.com/cli/
    exit /b 1
)

REM Check AWS credentials
echo 🔍 Checking AWS credentials...
aws sts get-caller-identity >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo ❌ AWS credentials not configured. Please run 'aws configure'
    exit /b 1
)

for /f "tokens=*" %%a in ('aws sts get-caller-identity --query Account --output text') do set ACCOUNT_ID=%%a
for /f "tokens=*" %%a in ('aws configure get region') do set REGION=%%a
if "%REGION%"=="" set REGION=us-east-1

echo ✅ AWS credentials configured
echo    Account: %ACCOUNT_ID%
echo    Region: %REGION%
echo.

REM Ask user which method to use
echo Choose deployment method:
echo   1) CloudFormation (recommended for production)
echo   2) Python script (faster, more flexible)
echo.
set /p choice="Enter choice (1 or 2): "

if "%choice%"=="1" (
    echo.
    echo 📦 Deploying IAM roles using CloudFormation...
    echo.
    
    REM Check if stack exists
    aws cloudformation describe-stacks --stack-name %STACK_NAME% >nul 2>nul
    if %ERRORLEVEL% EQU 0 (
        echo ⚠️  Stack already exists. Updating...
        aws cloudformation update-stack ^
            --stack-name %STACK_NAME% ^
            --template-body file://%TEMPLATE_FILE% ^
            --parameters ^
                ParameterKey=Environment,ParameterValue=%ENVIRONMENT% ^
                ParameterKey=S3BucketName,ParameterValue=%S3_BUCKET_NAME% ^
            --capabilities CAPABILITY_NAMED_IAM
        
        echo ⏳ Waiting for stack update to complete...
        aws cloudformation wait stack-update-complete --stack-name %STACK_NAME%
    ) else (
        echo 📦 Creating new stack...
        aws cloudformation create-stack ^
            --stack-name %STACK_NAME% ^
            --template-body file://%TEMPLATE_FILE% ^
            --parameters ^
                ParameterKey=Environment,ParameterValue=%ENVIRONMENT% ^
                ParameterKey=S3BucketName,ParameterValue=%S3_BUCKET_NAME% ^
            --capabilities CAPABILITY_NAMED_IAM
        
        echo ⏳ Waiting for stack creation to complete...
        aws cloudformation wait stack-create-complete --stack-name %STACK_NAME%
    )
    
    echo.
    echo ✅ CloudFormation deployment complete!
    echo.
    echo 📋 Stack Outputs:
    aws cloudformation describe-stacks ^
        --stack-name %STACK_NAME% ^
        --query "Stacks[0].Outputs[*].[OutputKey,OutputValue]" ^
        --output table
) else if "%choice%"=="2" (
    echo.
    echo 🐍 Deploying IAM roles using Python script...
    echo.
    
    REM Check if Python is installed
    where python >nul 2>nul
    if %ERRORLEVEL% NEQ 0 (
        echo ❌ Python is not installed. Please install it first.
        exit /b 1
    )
    
    REM Check if boto3 is installed
    python -c "import boto3" >nul 2>nul
    if %ERRORLEVEL% NEQ 0 (
        echo 📦 Installing boto3...
        pip install boto3
    )
    
    REM Run the Python setup script
    python setup_iam.py
) else (
    echo ❌ Invalid choice. Please run the script again and choose 1 or 2.
    exit /b 1
)

echo.
echo ==========================================
echo ✅ IAM Setup Complete!
echo ==========================================
echo.
echo 💡 Next Steps:
echo   1. Create Lambda functions using the Lambda execution role
echo   2. Configure API Gateway with the API Gateway role
echo   3. Test permissions by uploading a document
echo.

endlocal
