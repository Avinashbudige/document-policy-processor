@echo off
REM Comprehensive Smoke Test Suite for Document Policy Processor
REM This script runs all smoke tests to verify the system is working

echo ========================================
echo Document Policy Processor - Smoke Tests
echo ========================================
echo.

REM Set error handling
setlocal enabledelayedexpansion
set "TOTAL_TESTS=0"
set "PASSED_TESTS=0"
set "FAILED_TESTS=0"

echo [1/7] Testing Python Unit Tests...
echo ========================================
cd tests
python -m pytest -v --tb=short
if %ERRORLEVEL% EQU 0 (
    echo [PASS] Unit tests passed
    set /a PASSED_TESTS+=1
) else (
    echo [FAIL] Unit tests failed
    set /a FAILED_TESTS+=1
)
set /a TOTAL_TESTS+=1
cd ..
echo.

echo [2/7] Testing Lambda Function Locally...
echo ========================================
call test-lambda-local.bat
if %ERRORLEVEL% EQU 0 (
    echo [PASS] Lambda local test passed
    set /a PASSED_TESTS+=1
) else (
    echo [FAIL] Lambda local test failed
    set /a FAILED_TESTS+=1
)
set /a TOTAL_TESTS+=1
echo.

echo [3/7] Verifying Lambda Deployment...
echo ========================================
call verify-lambda-deployment.bat
if %ERRORLEVEL% EQU 0 (
    echo [PASS] Lambda deployment verified
    set /a PASSED_TESTS+=1
) else (
    echo [FAIL] Lambda deployment verification failed
    set /a FAILED_TESTS+=1
)
set /a TOTAL_TESTS+=1
echo.

echo [4/7] Testing API Gateway...
echo ========================================
call test-api-gateway.bat
if %ERRORLEVEL% EQU 0 (
    echo [PASS] API Gateway test passed
    set /a PASSED_TESTS+=1
) else (
    echo [FAIL] API Gateway test failed
    set /a FAILED_TESTS+=1
)
set /a TOTAL_TESTS+=1
echo.

echo [5/7] Testing Upload Flow...
echo ========================================
call test-upload-flow.bat
if %ERRORLEVEL% EQU 0 (
    echo [PASS] Upload flow test passed
    set /a PASSED_TESTS+=1
) else (
    echo [FAIL] Upload flow test failed
    set /a FAILED_TESTS+=1
)
set /a TOTAL_TESTS+=1
echo.

echo [6/7] Verifying CloudWatch Monitoring...
echo ========================================
call verify-cloudwatch-monitoring.bat
if %ERRORLEVEL% EQU 0 (
    echo [PASS] CloudWatch monitoring verified
    set /a PASSED_TESTS+=1
) else (
    echo [FAIL] CloudWatch monitoring verification failed
    set /a FAILED_TESTS+=1
)
set /a TOTAL_TESTS+=1
echo.

echo [7/7] Testing Frontend...
echo ========================================
cd frontend
if exist test-deployment.bat (
    call test-deployment.bat
    if %ERRORLEVEL% EQU 0 (
        echo [PASS] Frontend test passed
        set /a PASSED_TESTS+=1
    ) else (
        echo [FAIL] Frontend test failed
        set /a FAILED_TESTS+=1
    )
) else (
    echo [SKIP] Frontend test script not found
    echo [INFO] Checking if frontend is accessible...
    curl -s -o nul -w "%%{http_code}" http://localhost:8501 > temp_status.txt
    set /p STATUS=<temp_status.txt
    del temp_status.txt
    if "!STATUS!"=="200" (
        echo [PASS] Frontend is accessible
        set /a PASSED_TESTS+=1
    ) else (
        echo [FAIL] Frontend is not accessible
        set /a FAILED_TESTS+=1
    )
)
set /a TOTAL_TESTS+=1
cd ..
echo.

echo ========================================
echo Smoke Test Summary
echo ========================================
echo Total Tests: %TOTAL_TESTS%
echo Passed: %PASSED_TESTS%
echo Failed: %FAILED_TESTS%
echo.

if %FAILED_TESTS% EQU 0 (
    echo [SUCCESS] All smoke tests passed! System is ready.
    exit /b 0
) else (
    echo [WARNING] Some tests failed. Review the output above.
    exit /b 1
)
