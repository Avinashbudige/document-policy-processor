@echo off
REM Quick Smoke Test - Verifies system is ready

echo ========================================
echo Document Policy Processor - Smoke Test
echo ========================================
echo.

echo [1/8] Python Environment...
py --version
if %ERRORLEVEL% NEQ 0 goto :fail
echo [PASS]
echo.

echo [2/8] Required Packages...
py -c "import boto3, openai, sentence_transformers, pytest" 2>nul
if %ERRORLEVEL% NEQ 0 goto :fail
echo [PASS]
echo.

echo [3/8] Unit Tests (99 tests)...
py -m pytest tests/ -q --tb=no
if %ERRORLEVEL% NEQ 0 goto :fail
echo [PASS]
echo.

echo [4/8] Source Code...
if not exist "src\lambda_handler.py" goto :fail
if not exist "src\text_extractor.py" goto :fail
if not exist "src\policy_matcher.py" goto :fail
if not exist "src\llm_exclusion_checker.py" goto :fail
if not exist "src\recommendation_engine.py" goto :fail
echo [PASS]
echo.

echo [5/8] Configuration Files...
if not exist "src\requirements.txt" goto :fail
if not exist "template.yaml" goto :fail
if not exist "Dockerfile" goto :fail
echo [PASS]
echo.

echo [6/8] Deployment Scripts...
if not exist "deploy-lambda.bat" goto :fail
if not exist "deploy-api-gateway.bat" goto :fail
echo [PASS]
echo.

echo [7/8] Frontend...
if not exist "frontend\app.py" goto :fail
echo [PASS]
echo.

echo [8/8] Demo Materials...
if not exist "demo\DEMO_SCRIPT.md" goto :fail
if not exist "demo\COMPLETE_3MIN_SCRIPT.md" goto :fail
echo [PASS]
echo.

echo ========================================
echo [SUCCESS] All Smoke Tests Passed!
echo ========================================
echo.
echo System Status: READY FOR DEPLOYMENT
echo.
echo Next Steps:
echo 1. Deploy Lambda: deploy-lambda.bat
echo 2. Deploy API Gateway: deploy-api-gateway.bat
echo 3. Start Frontend: cd frontend and streamlit run app.py
echo 4. Record Demo: See demo\VIDEO_CREATION_WALKTHROUGH.md
echo.
exit /b 0

:fail
echo [FAIL]
echo.
echo ========================================
echo [FAILED] Some Tests Failed
echo ========================================
echo Please review the output above.
exit /b 1
