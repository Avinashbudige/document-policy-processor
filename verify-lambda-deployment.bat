@echo off
REM Lambda Deployment Verification Script (Windows)
REM This script verifies that the Lambda function is properly deployed and configured

setlocal enabledelayedexpansion

REM Configuration
if "%LAMBDA_FUNCTION_NAME%"=="" set LAMBDA_FUNCTION_NAME=DocumentPolicyProcessor
if "%AWS_REGION%"=="" set AWS_REGION=us-east-1

echo ==========================================
echo Lambda Deployment Verification
echo ==========================================
echo Function Name: %LAMBDA_FUNCTION_NAME%
echo AWS Region: %AWS_REGION%
echo ==========================================
echo.

REM Test counters
set TESTS_PASSED=0
set TESTS_FAILED=0

REM Test 1: Check if Lambda function exists
echo Test 1: Checking if Lambda function exists...
aws lambda get-function --function-name %LAMBDA_FUNCTION_NAME% --region %AWS_REGION% >nul 2>&1
if %errorlevel% equ 0 (
    echo [PASS] Lambda function exists
    set /a TESTS_PASSED+=1
) else (
    echo [FAIL] Lambda function not found
    set /a TESTS_FAILED+=1
    echo Please deploy the Lambda function first using deploy-lambda.bat
    exit /b 1
)
echo.

REM Test 2: Check Lambda configuration
echo Test 2: Checking Lambda configuration...
aws lambda get-function-configuration --function-name %LAMBDA_FUNCTION_NAME% --region %AWS_REGION% > config.json

REM Check memory size
for /f "tokens=*" %%i in ('type config.json ^| jq -r ".MemorySize"') do set MEMORY_SIZE=%%i
if "%MEMORY_SIZE%"=="2048" (
    echo [PASS] Memory size is 2048 MB
    set /a TESTS_PASSED+=1
) else (
    echo [FAIL] Memory size is %MEMORY_SIZE% MB ^(expected 2048 MB^)
    set /a TESTS_FAILED+=1
)

REM Check timeout
for /f "tokens=*" %%i in ('type config.json ^| jq -r ".Timeout"') do set TIMEOUT=%%i
if "%TIMEOUT%"=="300" (
    echo [PASS] Timeout is 300 seconds
    set /a TESTS_PASSED+=1
) else (
    echo [FAIL] Timeout is %TIMEOUT% seconds ^(expected 300 seconds^)
    set /a TESTS_FAILED+=1
)

REM Check package type
for /f "tokens=*" %%i in ('type config.json ^| jq -r ".PackageType"') do set PACKAGE_TYPE=%%i
if "%PACKAGE_TYPE%"=="Image" (
    echo [PASS] Package type is Image
    set /a TESTS_PASSED+=1
) else (
    echo [FAIL] Package type is %PACKAGE_TYPE% ^(expected Image^)
    set /a TESTS_FAILED+=1
)

REM Check state
for /f "tokens=*" %%i in ('type config.json ^| jq -r ".State"') do set STATE=%%i
if "%STATE%"=="Active" (
    echo [PASS] Function state is Active
    set /a TESTS_PASSED+=1
) else (
    echo [FAIL] Function state is %STATE% ^(expected Active^)
    set /a TESTS_FAILED+=1
)
echo.

REM Test 3: Check environment variables
echo Test 3: Checking environment variables...

REM Check S3_BUCKET_NAME
type config.json | jq -e ".Environment.Variables.S3_BUCKET_NAME" >nul 2>&1
if %errorlevel% equ 0 (
    for /f "tokens=*" %%i in ('type config.json ^| jq -r ".Environment.Variables.S3_BUCKET_NAME"') do set S3_BUCKET=%%i
    echo [PASS] S3_BUCKET_NAME is set: !S3_BUCKET!
    set /a TESTS_PASSED+=1
) else (
    echo [FAIL] S3_BUCKET_NAME is not set
    set /a TESTS_FAILED+=1
)

REM Check DYNAMODB_TABLE_JOBS
type config.json | jq -e ".Environment.Variables.DYNAMODB_TABLE_JOBS" >nul 2>&1
if %errorlevel% equ 0 (
    for /f "tokens=*" %%i in ('type config.json ^| jq -r ".Environment.Variables.DYNAMODB_TABLE_JOBS"') do set DYNAMODB_TABLE=%%i
    echo [PASS] DYNAMODB_TABLE_JOBS is set: !DYNAMODB_TABLE!
    set /a TESTS_PASSED+=1
) else (
    echo [FAIL] DYNAMODB_TABLE_JOBS is not set
    set /a TESTS_FAILED+=1
)

REM Check EMBEDDING_MODEL
type config.json | jq -e ".Environment.Variables.EMBEDDING_MODEL" >nul 2>&1
if %errorlevel% equ 0 (
    for /f "tokens=*" %%i in ('type config.json ^| jq -r ".Environment.Variables.EMBEDDING_MODEL"') do set EMBEDDING_MODEL=%%i
    echo [PASS] EMBEDDING_MODEL is set: !EMBEDDING_MODEL!
    set /a TESTS_PASSED+=1
) else (
    echo [FAIL] EMBEDDING_MODEL is not set
    set /a TESTS_FAILED+=1
)

REM Check LLM_MODEL
type config.json | jq -e ".Environment.Variables.LLM_MODEL" >nul 2>&1
if %errorlevel% equ 0 (
    for /f "tokens=*" %%i in ('type config.json ^| jq -r ".Environment.Variables.LLM_MODEL"') do set LLM_MODEL=%%i
    echo [PASS] LLM_MODEL is set: !LLM_MODEL!
    set /a TESTS_PASSED+=1
) else (
    echo [FAIL] LLM_MODEL is not set
    set /a TESTS_FAILED+=1
)

REM Check OPENAI_API_KEY
type config.json | jq -e ".Environment.Variables.OPENAI_API_KEY" >nul 2>&1
if %errorlevel% equ 0 (
    echo [PASS] OPENAI_API_KEY is set
    set /a TESTS_PASSED+=1
) else (
    echo [FAIL] OPENAI_API_KEY is not set
    set /a TESTS_FAILED+=1
)
echo.

REM Test 4: Test health check endpoint
echo Test 4: Testing health check endpoint...
echo {"httpMethod":"GET","path":"/api/health","headers":{},"queryStringParameters":null,"body":null} > test-health-check.json

aws lambda invoke --function-name %LAMBDA_FUNCTION_NAME% --payload file://test-health-check.json --region %AWS_REGION% response-health.json >nul 2>&1
if %errorlevel% equ 0 (
    for /f "tokens=*" %%i in ('type response-health.json ^| jq -r ".statusCode"') do set STATUS_CODE=%%i
    if "!STATUS_CODE!"=="200" (
        echo [PASS] Health check endpoint returns 200
        set /a TESTS_PASSED+=1
        
        for /f "tokens=*" %%i in ('type response-health.json ^| jq -r ".body" ^| jq -r ".status"') do set HEALTH_STATUS=%%i
        if "!HEALTH_STATUS!"=="healthy" (
            echo [PASS] Health check status is 'healthy'
            set /a TESTS_PASSED+=1
        ) else (
            echo [FAIL] Health check status is '!HEALTH_STATUS!' ^(expected 'healthy'^)
            set /a TESTS_FAILED+=1
        )
    ) else (
        echo [FAIL] Health check endpoint returns !STATUS_CODE! ^(expected 200^)
        set /a TESTS_FAILED+=1
    )
) else (
    echo [FAIL] Failed to invoke health check endpoint
    set /a TESTS_FAILED+=1
)
echo.

REM Test 5: Test upload URL generation
echo Test 5: Testing upload URL generation...
echo {"httpMethod":"POST","path":"/api/upload-url","headers":{"Content-Type":"application/json"},"body":"{\"filename\":\"test-document.pdf\",\"file_type\":\"application/pdf\"}"} > test-upload-url.json

aws lambda invoke --function-name %LAMBDA_FUNCTION_NAME% --payload file://test-upload-url.json --region %AWS_REGION% response-upload.json >nul 2>&1
if %errorlevel% equ 0 (
    for /f "tokens=*" %%i in ('type response-upload.json ^| jq -r ".statusCode"') do set STATUS_CODE=%%i
    if "!STATUS_CODE!"=="200" (
        echo [PASS] Upload URL generation returns 200
        set /a TESTS_PASSED+=1
        
        type response-upload.json | jq -r ".body" | jq -e ".upload_url" >nul 2>&1
        if !errorlevel! equ 0 (
            echo [PASS] Upload URL is generated
            set /a TESTS_PASSED+=1
        ) else (
            echo [FAIL] Upload URL is not present in response
            set /a TESTS_FAILED+=1
        )
    ) else (
        echo [FAIL] Upload URL generation returns !STATUS_CODE! ^(expected 200^)
        set /a TESTS_FAILED+=1
    )
) else (
    echo [FAIL] Failed to invoke upload URL generation endpoint
    set /a TESTS_FAILED+=1
)
echo.

REM Test 6: Check IAM role permissions
echo Test 6: Checking IAM role permissions...
for /f "tokens=*" %%i in ('type config.json ^| jq -r ".Role"') do set ROLE_ARN=%%i
for /f "tokens=* delims=/" %%i in ("%ROLE_ARN%") do set ROLE_NAME=%%i

aws iam get-role --role-name %ROLE_NAME% >nul 2>&1
if %errorlevel% equ 0 (
    echo [PASS] IAM role exists: %ROLE_NAME%
    set /a TESTS_PASSED+=1
    
    aws iam list-attached-role-policies --role-name %ROLE_NAME% --query "AttachedPolicies[*].PolicyName" --output text > policies.txt
    for /f %%i in (policies.txt) do (
        echo [PASS] IAM role has attached policies
        set /a TESTS_PASSED+=1
        goto :policies_done
    )
    echo [FAIL] IAM role has no attached policies
    set /a TESTS_FAILED+=1
    :policies_done
) else (
    echo [FAIL] IAM role not found: %ROLE_NAME%
    set /a TESTS_FAILED+=1
)
echo.

REM Test 7: Check CloudWatch log group
echo Test 7: Checking CloudWatch log group...
set LOG_GROUP=/aws/lambda/%LAMBDA_FUNCTION_NAME%
aws logs describe-log-groups --log-group-name-prefix %LOG_GROUP% --region %AWS_REGION% | jq -e ".logGroups[] | select(.logGroupName == \"%LOG_GROUP%\")" >nul 2>&1
if %errorlevel% equ 0 (
    echo [PASS] CloudWatch log group exists
    set /a TESTS_PASSED+=1
) else (
    echo [FAIL] CloudWatch log group not found
    set /a TESTS_FAILED+=1
)
echo.

REM Test 8: Check ECR image
echo Test 8: Checking ECR image...
for /f "tokens=*" %%i in ('type config.json ^| jq -r ".CodeSha256"') do set IMAGE_URI=%%i
if not "%IMAGE_URI%"=="null" (
    if not "%IMAGE_URI%"=="" (
        echo [PASS] Container image is configured
        set /a TESTS_PASSED+=1
    ) else (
        echo [FAIL] Container image is not configured
        set /a TESTS_FAILED+=1
    )
) else (
    echo [FAIL] Container image is not configured
    set /a TESTS_FAILED+=1
)
echo.

REM Cleanup temporary files
del /q config.json test-health-check.json response-health.json test-upload-url.json response-upload.json policies.txt 2>nul

REM Summary
echo ==========================================
echo Verification Summary
echo ==========================================
echo Tests Passed: %TESTS_PASSED%
echo Tests Failed: %TESTS_FAILED%
echo ==========================================
echo.

if %TESTS_FAILED% equ 0 (
    echo [SUCCESS] All tests passed! Lambda function is properly deployed.
    echo.
    echo Next steps:
    echo 1. Deploy API Gateway ^(Task 11.2^)
    echo 2. Configure CloudWatch monitoring ^(Task 11.3^)
    echo 3. Run end-to-end integration tests ^(Task 12^)
    exit /b 0
) else (
    echo [ERROR] Some tests failed. Please review the errors above.
    echo.
    echo Common fixes:
    echo - Run deploy-lambda.bat to deploy/update the function
    echo - Check environment variables are set correctly
    echo - Verify IAM role has necessary permissions
    echo - Check CloudWatch logs for detailed errors
    exit /b 1
)

endlocal
