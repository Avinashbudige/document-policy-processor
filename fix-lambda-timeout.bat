@echo off
REM Fix Lambda Cold Start Timeout Issue

echo ========================================
echo   FIXING LAMBDA COLD START TIMEOUT
echo ========================================
echo.

echo This script will:
echo 1. Increase Lambda timeout to 15 minutes
echo 2. Increase memory to 3GB (faster CPU)
echo 3. Enable provisioned concurrency (keeps warm)
echo.
echo Cost: ~$15-20/month for provisioned concurrency
echo.
pause

echo.
echo Step 1: Increasing timeout to 900 seconds (15 minutes)...
aws lambda update-function-configuration ^
  --function-name DocumentPolicyProcessor ^
  --timeout 900 ^
  --region us-east-1

echo.
echo Step 2: Increasing memory to 3008 MB (3GB)...
aws lambda update-function-configuration ^
  --function-name DocumentPolicyProcessor ^
  --memory-size 3008 ^
  --region us-east-1

echo.
echo Step 3: Enabling provisioned concurrency (keeps Lambda warm)...
echo This will cost ~$15-20/month but eliminates cold starts.
echo.
set /p ENABLE_PC="Enable provisioned concurrency? (y/n): "

if /i "%ENABLE_PC%"=="y" (
    aws lambda put-provisioned-concurrency-config ^
      --function-name DocumentPolicyProcessor ^
      --provisioned-concurrent-executions 1 ^
      --qualifier $LATEST ^
      --region us-east-1
    echo.
    echo Provisioned concurrency enabled!
) else (
    echo.
    echo Skipping provisioned concurrency.
    echo Note: First requests will still have cold starts.
)

echo.
echo ========================================
echo   LAMBDA CONFIGURATION UPDATED
echo ========================================
echo.
echo Changes applied:
echo - Timeout: 900 seconds (15 minutes)
echo - Memory: 3008 MB (3 GB)
if /i "%ENABLE_PC%"=="y" (
    echo - Provisioned Concurrency: 1 instance
)
echo.
echo Your Lambda should now handle cold starts better!
echo.
pause
