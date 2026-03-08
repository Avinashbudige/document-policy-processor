@echo off
REM Local Lambda Testing Script (Windows)
REM Tests the Lambda function locally using Docker before deploying to AWS

setlocal enabledelayedexpansion

echo ==========================================
echo Local Lambda Testing
echo ==========================================

REM Configuration
set IMAGE_NAME=document-policy-processor
set IMAGE_TAG=test
set CONTAINER_NAME=lambda-test
set PORT=9000

REM Check if Docker is running
docker info >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Docker is not running. Please start Docker and try again.
    exit /b 1
)

REM Step 1: Build the Docker image
echo.
echo Step 1: Building Docker image...
docker build -t %IMAGE_NAME%:%IMAGE_TAG% .

REM Step 2: Stop and remove existing container if running
echo.
echo Step 2: Cleaning up existing containers...
docker stop %CONTAINER_NAME% 2>nul
docker rm %CONTAINER_NAME% 2>nul

REM Step 3: Run the container
echo.
echo Step 3: Starting Lambda container...
echo Container will listen on http://localhost:%PORT%

REM Check if AWS credentials are available
if "%AWS_ACCESS_KEY_ID%"=="" (
    echo WARNING: AWS credentials not found in environment variables.
    echo The Lambda function will not be able to access AWS services.
    echo Set AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY before running this script.
)

REM Check if OpenAI API key is available
if "%OPENAI_API_KEY%"=="" (
    echo WARNING: OPENAI_API_KEY not found in environment variables.
    echo The Lambda function will not be able to use LLM features.
)

REM Set defaults for optional variables
if "%AWS_REGION%"=="" set AWS_REGION=us-east-1
if "%S3_BUCKET_NAME%"=="" set S3_BUCKET_NAME=document-policy-processor-uploads
if "%DYNAMODB_TABLE_JOBS%"=="" set DYNAMODB_TABLE_JOBS=ProcessingJobs
if "%EMBEDDING_MODEL%"=="" set EMBEDDING_MODEL=all-MiniLM-L6-v2
if "%LLM_MODEL%"=="" set LLM_MODEL=gpt-3.5-turbo

docker run -d ^
    --name %CONTAINER_NAME% ^
    -p %PORT%:8080 ^
    -e AWS_ACCESS_KEY_ID=%AWS_ACCESS_KEY_ID% ^
    -e AWS_SECRET_ACCESS_KEY=%AWS_SECRET_ACCESS_KEY% ^
    -e AWS_SESSION_TOKEN=%AWS_SESSION_TOKEN% ^
    -e AWS_REGION=%AWS_REGION% ^
    -e S3_BUCKET_NAME=%S3_BUCKET_NAME% ^
    -e DYNAMODB_TABLE_JOBS=%DYNAMODB_TABLE_JOBS% ^
    -e EMBEDDING_MODEL=%EMBEDDING_MODEL% ^
    -e LLM_MODEL=%LLM_MODEL% ^
    -e OPENAI_API_KEY=%OPENAI_API_KEY% ^
    %IMAGE_NAME%:%IMAGE_TAG%

echo Container started successfully!

REM Wait for container to be ready
echo.
echo Waiting for Lambda runtime to initialize...
timeout /t 5 /nobreak >nul

REM Step 4: Test the function
echo.
echo Step 4: Testing Lambda function...
echo Sending test event from test-event.json...

if not exist test-event.json (
    echo ERROR: test-event.json not found. Creating a sample test event...
    (
        echo {
        echo   "body": {
        echo     "job_id": "test-job-12345",
        echo     "document_url": "s3://document-policy-processor-uploads/documents/sample-policy.pdf",
        echo     "symptoms": "Experiencing chest pain and shortness of breath for the past week"
        echo   }
        echo }
    ) > test-event.json
)

REM Invoke the function
curl -s -XPOST "http://localhost:%PORT%/2015-03-31/functions/function/invocations" -d @test-event.json > response.json

echo.
echo ==========================================
echo Lambda Response:
echo ==========================================
type response.json
echo.

REM Step 5: Show container logs
echo.
echo ==========================================
echo Container Logs:
echo ==========================================
docker logs %CONTAINER_NAME%

REM Step 6: Cleanup prompt
echo.
echo ==========================================
echo Testing Complete!
echo ==========================================
echo.
echo Container is still running. To view logs:
echo   docker logs -f %CONTAINER_NAME%
echo.
echo To stop and remove the container:
echo   docker stop %CONTAINER_NAME% ^&^& docker rm %CONTAINER_NAME%
echo.
echo ==========================================

endlocal
