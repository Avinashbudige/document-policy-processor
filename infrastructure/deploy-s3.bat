@echo off
REM Deploy S3 bucket for Document Policy Processor (Windows)

setlocal enabledelayedexpansion

REM Configuration
set BUCKET_NAME=document-policy-processor-uploads
set REGION=us-east-1
set STACK_NAME=document-policy-processor-s3

echo ==========================================
echo Document Policy Processor - S3 Deployment
echo ==========================================
echo.
echo Bucket Name: %BUCKET_NAME%
echo Region: %REGION%
echo Stack Name: %STACK_NAME%
echo.

REM Check if AWS CLI is installed
where aws >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] AWS CLI is not installed
    echo Please install AWS CLI: https://aws.amazon.com/cli/
    exit /b 1
)

REM Check if AWS credentials are configured
aws sts get-caller-identity >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] AWS credentials are not configured
    echo Please run: aws configure
    exit /b 1
)

echo [OK] AWS CLI configured
echo.

REM Ask user for deployment method
echo Choose deployment method:
echo 1) CloudFormation (recommended)
echo 2) Python script
echo 3) Exit
set /p choice="Enter choice [1-3]: "

if "%choice%"=="1" goto cloudformation
if "%choice%"=="2" goto python
if "%choice%"=="3" goto exit
echo Invalid choice
exit /b 1

:cloudformation
echo.
echo Deploying with CloudFormation...

REM Check if stack exists
aws cloudformation describe-stacks --stack-name %STACK_NAME% --region %REGION% >nul 2>nul
if %ERRORLEVEL% EQU 0 (
    echo Stack already exists. Updating...
    aws cloudformation update-stack ^
        --stack-name %STACK_NAME% ^
        --template-body file://infrastructure/s3-bucket.yaml ^
        --parameters ParameterKey=BucketName,ParameterValue=%BUCKET_NAME% ^
                     ParameterKey=Environment,ParameterValue=dev ^
        --region %REGION%
    
    echo Waiting for stack update to complete...
    aws cloudformation wait stack-update-complete ^
        --stack-name %STACK_NAME% ^
        --region %REGION%
) else (
    echo Creating new stack...
    aws cloudformation create-stack ^
        --stack-name %STACK_NAME% ^
        --template-body file://infrastructure/s3-bucket.yaml ^
        --parameters ParameterKey=BucketName,ParameterValue=%BUCKET_NAME% ^
                     ParameterKey=Environment,ParameterValue=dev ^
        --region %REGION%
    
    echo Waiting for stack creation to complete...
    aws cloudformation wait stack-create-complete ^
        --stack-name %STACK_NAME% ^
        --region %REGION%
)

echo.
echo [OK] CloudFormation deployment complete
echo.
echo Stack Outputs:
aws cloudformation describe-stacks ^
    --stack-name %STACK_NAME% ^
    --region %REGION% ^
    --query "Stacks[0].Outputs[*].[OutputKey,OutputValue]" ^
    --output table

REM Create folders
echo.
echo Creating folder structure...
aws s3api put-object --bucket %BUCKET_NAME% --key documents/ --region %REGION%
aws s3api put-object --bucket %BUCKET_NAME% --key embeddings/ --region %REGION%
aws s3api put-object --bucket %BUCKET_NAME% --key results/ --region %REGION%
echo [OK] Folders created

goto complete

:python
echo.
echo Deploying with Python script...

REM Check if Python is installed
where python >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Python is not installed
    exit /b 1
)

REM Check if boto3 is installed
python -c "import boto3" >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo Installing boto3...
    pip install boto3
)

REM Run the Python script
python infrastructure\setup_s3.py

goto complete

:exit
echo Exiting...
exit /b 0

:complete
echo.
echo ==========================================
echo [OK] Deployment Complete!
echo ==========================================
echo.
echo Bucket URL: https://%BUCKET_NAME%.s3.%REGION%.amazonaws.com
echo Console URL: https://s3.console.aws.amazon.com/s3/buckets/%BUCKET_NAME%
echo.
echo Next steps:
echo 1. Set up DynamoDB tables (task 2.2)
echo 2. Set up IAM roles (task 2.3)
echo 3. Implement Lambda functions
