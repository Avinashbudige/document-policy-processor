@echo off
REM Test script for API Gateway endpoints (Windows)
REM This script tests all API Gateway endpoints after deployment

setlocal enabledelayedexpansion

REM Configuration
set API_BASE_URL=
set API_KEY=
set TEST_JOB_ID=test-%RANDOM%

REM Parse command line arguments
:parse_args
if "%~1"=="" goto validate_inputs
if "%~1"=="--api-url" (
    set API_BASE_URL=%~2
    shift
    shift
    goto parse_args
)
if "%~1"=="--api-key" (
    set API_KEY=%~2
    shift
    shift
    goto parse_args
)
echo Unknown option: %~1
echo Usage: %~nx0 --api-url ^<url^> --api-key ^<key^>
exit /b 1

:validate_inputs
if "%API_BASE_URL%"=="" (
    echo Error: API base URL is required
    echo Usage: %~nx0 --api-url ^<url^> --api-key ^<key^>
    exit /b 1
)

if "%API_KEY%"=="" (
    echo Warning: No API key provided. Some tests will fail.
)

echo ==========================================
echo API Gateway Endpoint Tests
echo ==========================================
echo API Base URL: %API_BASE_URL%
echo Test Job ID: %TEST_JOB_ID%
echo.

REM Test 1: Health Check
echo Test 1: Health Check (GET /api/health)
curl -s "%API_BASE_URL%/api/health"
echo.
echo.

REM Test 2: Get Status (should return 404 for non-existent job)
echo Test 2: Get Status for non-existent job (GET /api/status/{jobId})
if not "%API_KEY%"=="" (
    curl -s -H "X-Api-Key: %API_KEY%" "%API_BASE_URL%/api/status/non-existent-job"
) else (
    echo Skipped (no API key)
)
echo.
echo.

REM Test 3: Get Results (should return 404 for non-existent job)
echo Test 3: Get Results for non-existent job (GET /api/results/{jobId})
if not "%API_KEY%"=="" (
    curl -s -H "X-Api-Key: %API_KEY%" "%API_BASE_URL%/api/results/non-existent-job"
) else (
    echo Skipped (no API key)
)
echo.
echo.

REM Test 4: Process Document (validation error - missing fields)
echo Test 4: Process Document with missing fields (POST /api/process-document)
if not "%API_KEY%"=="" (
    curl -s -X POST -H "X-Api-Key: %API_KEY%" -H "Content-Type: application/json" -d "{}" "%API_BASE_URL%/api/process-document"
) else (
    echo Skipped (no API key)
)
echo.
echo.

REM Test 5: Process Document (validation error - invalid S3 URL)
echo Test 5: Process Document with invalid S3 URL (POST /api/process-document)
if not "%API_KEY%"=="" (
    curl -s -X POST -H "X-Api-Key: %API_KEY%" -H "Content-Type: application/json" -d "{\"job_id\":\"%TEST_JOB_ID%\",\"document_url\":\"invalid-url\",\"symptoms\":\"Test symptoms\"}" "%API_BASE_URL%/api/process-document"
) else (
    echo Skipped (no API key)
)
echo.
echo.

REM Test 6: CORS Headers
echo Test 6: CORS Headers
curl -s -I "%API_BASE_URL%/api/health" | findstr /i "access-control"
echo.
echo.

REM Test 7: API Key Authentication (should fail without key)
echo Test 7: API Key Authentication (should fail without key)
curl -s -X POST -H "Content-Type: application/json" -d "{\"job_id\":\"%TEST_JOB_ID%\",\"document_url\":\"s3://bucket/key\",\"symptoms\":\"Test\"}" "%API_BASE_URL%/api/process-document"
echo.
echo.

REM Summary
echo ==========================================
echo Test Summary
echo ==========================================
echo All basic endpoint tests completed.
echo.
echo Next steps:
echo 1. Upload a test document to S3
echo 2. Test the full document processing flow
echo 3. Monitor CloudWatch logs for any errors
echo.

endlocal
