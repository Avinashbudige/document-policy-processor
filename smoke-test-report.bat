@echo off
REM Quick Smoke Test Report - Tests what can be verified locally
REM This script runs tests that don't require AWS deployment

echo ========================================
echo Document Policy Processor - Smoke Test Report
echo ========================================
echo Date: %date% %time%
echo.

setlocal enabledelayedexpansion
set "TOTAL_TESTS=0"
set "PASSED_TESTS=0"
set "FAILED_TESTS=0"
set "SKIPPED_TESTS=0"

REM Test 1: Python Environment
echo [TEST 1/8] Python Environment
echo ----------------------------------------
py --version >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    py --version
    echo [PASS] Python is installed
    set /a PASSED_TESTS+=1
) else (
    echo [FAIL] Python is not installed
    set /a FAILED_TESTS+=1
)
set /a TOTAL_TESTS+=1
echo.

REM Test 2: Required Python Packages
echo [TEST 2/8] Required Python Packages
echo ----------------------------------------
py -c "import boto3, openai, sentence_transformers, pytest" 2>nul
if %ERRORLEVEL% EQU 0 (
    echo [PASS] All required packages are installed
    set /a PASSED_TESTS+=1
) else (
    echo [FAIL] Some required packages are missing
    echo Run: pip install -r src/requirements.txt
    set /a FAILED_TESTS+=1
)
set /a TOTAL_TESTS+=1
echo.

REM Test 3: Unit Tests
echo [TEST 3/8] Unit Tests (99 tests)
echo ----------------------------------------
py -m pytest tests/ -q --tb=no 2>nul
if %ERRORLEVEL% EQU 0 (
    echo [PASS] All unit tests passed
    set /a PASSED_TESTS+=1
) else (
    echo [FAIL] Some unit tests failed
    echo Run: py -m pytest tests/ -v for details
    set /a FAILED_TESTS+=1
)
set /a TOTAL_TESTS+=1
echo.

REM Test 4: Source Code Structure
echo [TEST 4/8] Source Code Structure
echo ----------------------------------------
set "MISSING_FILES=0"
if not exist "src\lambda_handler.py" set /a MISSING_FILES+=1
if not exist "src\text_extractor.py" set /a MISSING_FILES+=1
if not exist "src\policy_matcher.py" set /a MISSING_FILES+=1
if not exist "src\llm_exclusion_checker.py" set /a MISSING_FILES+=1
if not exist "src\recommendation_engine.py" set /a MISSING_FILES+=1

if %MISSING_FILES% EQU 0 (
    echo [PASS] All source files present
    set /a PASSED_TESTS+=1
) else (
    echo [FAIL] %MISSING_FILES% source files missing
    set /a FAILED_TESTS+=1
)
set /a TOTAL_TESTS+=1
echo.

REM Test 5: Configuration Files
echo [TEST 5/8] Configuration Files
echo ----------------------------------------
set "MISSING_CONFIG=0"
if not exist "src\requirements.txt" set /a MISSING_CONFIG+=1
if not exist "template.yaml" set /a MISSING_CONFIG+=1
if not exist "Dockerfile" set /a MISSING_CONFIG+=1

if %MISSING_CONFIG% EQU 0 (
    echo [PASS] All configuration files present
    set /a PASSED_TESTS+=1
) else (
    echo [FAIL] %MISSING_CONFIG% configuration files missing
    set /a FAILED_TESTS+=1
)
set /a TOTAL_TESTS+=1
echo.

REM Test 6: Deployment Scripts
echo [TEST 6/8] Deployment Scripts
echo ----------------------------------------
set "MISSING_SCRIPTS=0"
if not exist "deploy-lambda.bat" set /a MISSING_SCRIPTS+=1
if not exist "deploy-api-gateway.bat" set /a MISSING_SCRIPTS+=1
if not exist "test-api-gateway.bat" set /a MISSING_SCRIPTS+=1

if %MISSING_SCRIPTS% EQU 0 (
    echo [PASS] All deployment scripts present
    set /a PASSED_TESTS+=1
) else (
    echo [FAIL] %MISSING_SCRIPTS% deployment scripts missing
    set /a FAILED_TESTS+=1
)
set /a TOTAL_TESTS+=1
echo.

REM Test 7: Frontend Files
echo [TEST 7/8] Frontend Files
echo ----------------------------------------
if exist "frontend\app.py" (
    echo [PASS] Frontend application exists
    set /a PASSED_TESTS+=1
) else if exist "frontend\index.html" (
    echo [PASS] Frontend HTML exists
    set /a PASSED_TESTS+=1
) else (
    echo [FAIL] No frontend files found
    set /a FAILED_TESTS+=1
)
set /a TOTAL_TESTS+=1
echo.

REM Test 8: Demo Materials
echo [TEST 8/8] Demo Materials
echo ----------------------------------------
set "MISSING_DEMO=0"
if not exist "demo\DEMO_SCRIPT.md" set /a MISSING_DEMO+=1
if not exist "demo\COMPLETE_3MIN_SCRIPT.md" set /a MISSING_DEMO+=1
if not exist "demo\VIDEO_CREATION_WALKTHROUGH.md" set /a MISSING_DEMO+=1

if %MISSING_DEMO% EQU 0 (
    echo [PASS] All demo materials present
    set /a PASSED_TESTS+=1
) else (
    echo [FAIL] %MISSING_DEMO% demo files missing
    set /a FAILED_TESTS+=1
)
set /a TOTAL_TESTS+=1
echo.

REM Summary
echo ========================================
echo Smoke Test Summary
echo ========================================
echo Total Tests: %TOTAL_TESTS%
echo Passed: %PASSED_TESTS%
echo Failed: %FAILED_TESTS%
echo Skipped: %SKIPPED_TESTS%
echo.

if !FAILED_TESTS! EQU 0 (
    echo [SUCCESS] All smoke tests passed!
    echo.
    echo System Status: READY FOR DEPLOYMENT
    echo.
    echo Next Steps:
    echo 1. Deploy Lambda: deploy-lambda.bat
    echo 2. Deploy API Gateway: deploy-api-gateway.bat
    echo 3. Deploy Frontend: cd frontend and streamlit run app.py
    echo 4. Record Demo Video: See demo\VIDEO_CREATION_WALKTHROUGH.md
    exit /b 0
) else (
    echo [WARNING] !FAILED_TESTS! test(s) failed
    echo.
    echo System Status: NEEDS ATTENTION
    echo.
    echo Review the failed tests above and fix issues before deployment.
    exit /b 1
)

endlocal
