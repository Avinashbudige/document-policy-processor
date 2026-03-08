@echo off
REM API Gateway Deployment Script for Document Policy Processor (Windows)
REM This script deploys the API Gateway using AWS SAM

setlocal enabledelayedexpansion

echo ==========================================
echo API Gateway Deployment Script
echo Document Policy Processor
echo ==========================================
echo.

REM Check prerequisites
echo Checking prerequisites...

REM Check AWS CLI
where aws >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo X AWS CLI not found. Please install it first.
    exit /b 1
)
echo + AWS CLI found

REM Check SAM CLI
where sam >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo X AWS SAM CLI not found. Please install it first.
    echo    Install: pip install aws-sam-cli
    exit /b 1
)
echo + SAM CLI found

REM Check AWS credentials
aws sts get-caller-identity >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo X AWS credentials not configured. Run 'aws configure' first.
    exit /b 1
)
echo + AWS credentials configured

REM Get AWS account info
for /f "tokens=*" %%i in ('aws sts get-caller-identity --query Account --output text') do set AWS_ACCOUNT_ID=%%i
if not defined AWS_REGION set AWS_REGION=us-east-1
echo + AWS Account: %AWS_ACCOUNT_ID%
echo + AWS Region: %AWS_REGION%
echo.

REM Check for OpenAI API key
if not defined OPENAI_API_KEY (
    echo Warning: OPENAI_API_KEY environment variable not set
    set /p OPENAI_API_KEY="Enter your OpenAI API key: "
    if not defined OPENAI_API_KEY (
        echo X OpenAI API key is required
        exit /b 1
    )
)
echo + OpenAI API key configured
echo.

REM Set default parameters
if not defined S3_BUCKET_NAME set S3_BUCKET_NAME=document-policy-processor-uploads
if not defined DYNAMODB_TABLE_JOBS set DYNAMODB_TABLE_JOBS=ProcessingJobs
if not defined EMBEDDING_MODEL set EMBEDDING_MODEL=all-MiniLM-L6-v2
if not defined LLM_MODEL set LLM_MODEL=gpt-3.5-turbo
if not defined STACK_NAME set STACK_NAME=document-policy-processor

echo Deployment Configuration:
echo   Stack Name: %STACK_NAME%
echo   S3 Bucket: %S3_BUCKET_NAME%
echo   DynamoDB Table: %DYNAMODB_TABLE_JOBS%
echo   Embedding Model: %EMBEDDING_MODEL%
echo   LLM Model: %LLM_MODEL%
echo.

REM Ask for confirmation
set /p CONFIRM="Proceed with deployment? (y/n) "
if /i not "%CONFIRM%"=="y" (
    echo Deployment cancelled
    exit /b 0
)

REM Build SAM application
echo.
echo ==========================================
echo Step 1: Building SAM Application
echo ==========================================
sam build

if %ERRORLEVEL% NEQ 0 (
    echo X SAM build failed
    exit /b 1
)
echo + SAM build completed

REM Deploy SAM application
echo.
echo ==========================================
echo Step 2: Deploying to AWS
echo ==========================================

REM Check if samconfig.toml exists
if exist samconfig.toml (
    echo Using existing SAM configuration...
    sam deploy --parameter-overrides "S3BucketName=%S3_BUCKET_NAME%" "DynamoDBTableJobs=%DYNAMODB_TABLE_JOBS%" "EmbeddingModel=%EMBEDDING_MODEL%" "LLMModel=%LLM_MODEL%" "OpenAIAPIKey=%OPENAI_API_KEY%"
) else (
    echo Running guided deployment (first time)...
    sam deploy --guided --parameter-overrides "S3BucketName=%S3_BUCKET_NAME%" "DynamoDBTableJobs=%DYNAMODB_TABLE_JOBS%" "EmbeddingModel=%EMBEDDING_MODEL%" "LLMModel=%LLM_MODEL%" "OpenAIAPIKey=%OPENAI_API_KEY%"
)

if %ERRORLEVEL% NEQ 0 (
    echo X SAM deployment failed
    exit /b 1
)

REM Get deployment outputs
echo.
echo ==========================================
echo Step 3: Retrieving Deployment Information
echo ==========================================

REM Get API endpoint
for /f "tokens=*" %%i in ('aws cloudformation describe-stacks --stack-name %STACK_NAME% --query "Stacks[0].Outputs[?OutputKey==`ApiEndpoint`].OutputValue" --output text --region %AWS_REGION%') do set API_ENDPOINT=%%i

REM Get API Key ID
for /f "tokens=*" %%i in ('aws cloudformation describe-stacks --stack-name %STACK_NAME% --query "Stacks[0].Outputs[?OutputKey==`ApiKey`].OutputValue" --output text --region %AWS_REGION%') do set API_KEY_ID=%%i

REM Get actual API key value
echo Retrieving API key...
for /f "tokens=*" %%i in ('aws apigateway get-api-key --api-key %API_KEY_ID% --include-value --query value --output text --region %AWS_REGION%') do set API_KEY=%%i

REM Display results
echo.
echo ==========================================
echo Deployment Complete!
echo ==========================================
echo.
echo API Gateway Base URL:
echo   %API_ENDPOINT%
echo.
echo API Key:
echo   %API_KEY%
echo.
echo Endpoints:
echo   Health Check:      GET  %API_ENDPOINT%/api/health (no auth)
echo   Upload URL:        POST %API_ENDPOINT%/api/upload-url
echo   Process Document:  POST %API_ENDPOINT%/api/process-document
echo   Job Status:        GET  %API_ENDPOINT%/api/status/{jobId}
echo   Job Results:       GET  %API_ENDPOINT%/api/results/{jobId}
echo.
echo Authentication:
echo   Include header: X-Api-Key: %API_KEY%
echo.

REM Save to file
(
echo API Gateway Deployment Information
echo Generated: %date% %time%
echo.
echo API Gateway Base URL:
echo %API_ENDPOINT%
echo.
echo API Key:
echo %API_KEY%
echo.
echo Endpoints:
echo - Health Check:      GET  %API_ENDPOINT%/api/health (no auth required^)
echo - Upload URL:        POST %API_ENDPOINT%/api/upload-url (auth required^)
echo - Process Document:  POST %API_ENDPOINT%/api/process-document (auth required^)
echo - Job Status:        GET  %API_ENDPOINT%/api/status/{jobId} (auth required^)
echo - Job Results:       GET  %API_ENDPOINT%/api/results/{jobId} (auth required^)
echo.
echo Authentication:
echo Include header: X-Api-Key: %API_KEY%
echo.
echo Rate Limits:
echo - 10 requests per second
echo - Burst: 20 requests
echo - Daily quota: 1000 requests
echo.
echo Example curl command:
echo curl -X GET "%API_ENDPOINT%/api/health"
echo.
echo curl -X POST "%API_ENDPOINT%/api/upload-url" ^
echo   -H "Content-Type: application/json" ^
echo   -H "X-Api-Key: %API_KEY%" ^
echo   -d "{\"filename\":\"test.pdf\",\"file_type\":\"application/pdf\"}"
) > API_DEPLOYMENT_INFO.txt

echo + Deployment information saved to: API_DEPLOYMENT_INFO.txt
echo.

REM Test health endpoint
echo ==========================================
echo Step 4: Testing API Gateway
echo ==========================================
echo.
echo Testing health endpoint...

curl -s -w "\n%%{http_code}" "%API_ENDPOINT%/api/health" > health_test.tmp
for /f "tokens=*" %%i in (health_test.tmp) do set LAST_LINE=%%i
set HTTP_CODE=%LAST_LINE%

if "%HTTP_CODE%"=="200" (
    echo + Health check passed!
    type health_test.tmp | findstr /v "200"
) else (
    echo Warning: Health check returned status: %HTTP_CODE%
    type health_test.tmp
)
del health_test.tmp

echo.
echo ==========================================
echo Next Steps
echo ==========================================
echo.
echo 1. Test all endpoints:
echo    test-api-gateway.bat
echo.
echo 2. Update frontend configuration:
echo    - API Base URL: %API_ENDPOINT%
echo    - API Key: %API_KEY%
echo.
echo 3. View CloudWatch logs:
echo    aws logs tail /aws/lambda/DocumentPolicyProcessor --follow
echo.
echo 4. Monitor API Gateway:
echo    aws logs tail /aws/apigateway/%STACK_NAME%/Prod --follow
echo.
echo ==========================================

endlocal
