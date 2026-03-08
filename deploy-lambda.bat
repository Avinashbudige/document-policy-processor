@echo off
REM Lambda Deployment Script for Document Policy Processor (Windows)
REM This script builds and deploys the Lambda function as a container image

setlocal enabledelayedexpansion

REM Configuration
if "%AWS_REGION%"=="" set AWS_REGION=us-east-1
if "%IMAGE_TAG%"=="" set IMAGE_TAG=latest
set ECR_REPOSITORY_NAME=document-policy-processor
set LAMBDA_FUNCTION_NAME=DocumentPolicyProcessor

REM Get AWS Account ID
for /f "tokens=*" %%i in ('aws sts get-caller-identity --query Account --output text') do set AWS_ACCOUNT_ID=%%i

echo ==========================================
echo Lambda Deployment Configuration
echo ==========================================
echo AWS Region: %AWS_REGION%
echo AWS Account ID: %AWS_ACCOUNT_ID%
echo ECR Repository: %ECR_REPOSITORY_NAME%
echo Lambda Function: %LAMBDA_FUNCTION_NAME%
echo Image Tag: %IMAGE_TAG%
echo ==========================================

REM Step 1: Create ECR repository if it doesn't exist
echo.
echo Step 1: Creating ECR repository (if not exists)...
aws ecr describe-repositories --repository-names %ECR_REPOSITORY_NAME% --region %AWS_REGION% 2>nul || (
    aws ecr create-repository ^
        --repository-name %ECR_REPOSITORY_NAME% ^
        --region %AWS_REGION% ^
        --image-scanning-configuration scanOnPush=true
)

set ECR_URI=%AWS_ACCOUNT_ID%.dkr.ecr.%AWS_REGION%.amazonaws.com/%ECR_REPOSITORY_NAME%
echo ECR URI: %ECR_URI%

REM Step 2: Authenticate Docker to ECR
echo.
echo Step 2: Authenticating Docker to ECR...
for /f "tokens=*" %%i in ('aws ecr get-login-password --region %AWS_REGION%') do (
    echo %%i | docker login --username AWS --password-stdin %ECR_URI%
)

REM Step 3: Build Docker image
echo.
echo Step 3: Building Docker image...
docker build -t %ECR_REPOSITORY_NAME%:%IMAGE_TAG% .

REM Step 4: Tag image for ECR
echo.
echo Step 4: Tagging image for ECR...
docker tag %ECR_REPOSITORY_NAME%:%IMAGE_TAG% %ECR_URI%:%IMAGE_TAG%

REM Step 5: Push image to ECR
echo.
echo Step 5: Pushing image to ECR...
docker push %ECR_URI%:%IMAGE_TAG%

REM Step 6: Update or create Lambda function
echo.
echo Step 6: Updating Lambda function...

REM Check if Lambda function exists
aws lambda get-function --function-name %LAMBDA_FUNCTION_NAME% --region %AWS_REGION% 2>nul
if %errorlevel% equ 0 (
    echo Updating existing Lambda function...
    aws lambda update-function-code ^
        --function-name %LAMBDA_FUNCTION_NAME% ^
        --image-uri %ECR_URI%:%IMAGE_TAG% ^
        --region %AWS_REGION%
    
    echo Waiting for Lambda update to complete...
    aws lambda wait function-updated ^
        --function-name %LAMBDA_FUNCTION_NAME% ^
        --region %AWS_REGION%
) else (
    echo Creating new Lambda function...
    
    REM Get the Lambda execution role ARN
    for /f "tokens=*" %%i in ('aws iam get-role --role-name DocumentPolicyProcessor-Lambda-dev --query "Role.Arn" --output text 2^>nul') do set LAMBDA_ROLE_ARN=%%i
    
    if "!LAMBDA_ROLE_ARN!"=="" (
        echo ERROR: Lambda execution role not found. Please run infrastructure setup first.
        exit /b 1
    )
    
    aws lambda create-function ^
        --function-name %LAMBDA_FUNCTION_NAME% ^
        --package-type Image ^
        --code ImageUri=%ECR_URI%:%IMAGE_TAG% ^
        --role !LAMBDA_ROLE_ARN! ^
        --timeout 300 ^
        --memory-size 2048 ^
        --environment "Variables={S3_BUCKET_NAME=document-policy-processor-uploads,DYNAMODB_TABLE_JOBS=ProcessingJobs,EMBEDDING_MODEL=all-MiniLM-L6-v2,LLM_MODEL=gpt-3.5-turbo}" ^
        --region %AWS_REGION%
    
    echo Waiting for Lambda creation to complete...
    aws lambda wait function-active ^
        --function-name %LAMBDA_FUNCTION_NAME% ^
        --region %AWS_REGION%
)

echo.
echo ==========================================
echo Deployment Complete!
echo ==========================================
echo Lambda Function ARN:
aws lambda get-function --function-name %LAMBDA_FUNCTION_NAME% --region %AWS_REGION% --query "Configuration.FunctionArn" --output text
echo.
echo To test the function, run:
echo aws lambda invoke --function-name %LAMBDA_FUNCTION_NAME% --payload file://test-event.json response.json
echo ==========================================

endlocal
