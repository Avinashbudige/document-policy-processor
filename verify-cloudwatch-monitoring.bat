@echo off
REM CloudWatch Monitoring Verification Script (Windows)
REM Verifies that all monitoring components are properly configured

setlocal enabledelayedexpansion

if "%AWS_REGION%"=="" set AWS_REGION=us-east-1
set REGION=%AWS_REGION%
set FUNCTION_NAME=DocumentPolicyProcessor
set API_NAME=document-policy-processor
set DASHBOARD_NAME=DocumentPolicyProcessor-Dashboard

set PASS_COUNT=0
set FAIL_COUNT=0

echo ==========================================
echo CloudWatch Monitoring Verification
echo ==========================================
echo.

REM Check 1: Lambda Log Group
echo Checking Log Groups...
aws logs describe-log-groups --log-group-name-prefix "/aws/lambda/%FUNCTION_NAME%" --region %REGION% | findstr /C:"%FUNCTION_NAME%" >nul
if %errorlevel% equ 0 (
    echo [OK] Lambda log group exists
    set /a PASS_COUNT+=1
) else (
    echo [FAIL] Lambda log group missing
    set /a FAIL_COUNT+=1
)

echo.

REM Check 2: Dashboard
echo Checking Dashboard...
aws cloudwatch get-dashboard --dashboard-name "%DASHBOARD_NAME%" --region %REGION% >nul 2>&1
if %errorlevel% equ 0 (
    echo [OK] Dashboard exists
    set /a PASS_COUNT+=1
) else (
    echo [FAIL] Dashboard missing
    set /a FAIL_COUNT+=1
)

echo.

REM Check 3: Alarms
echo Checking Alarms...

aws cloudwatch describe-alarms --alarm-names "%FUNCTION_NAME%-HighErrorRate" --region %REGION% | findstr /C:"HighErrorRate" >nul
if %errorlevel% equ 0 (
    echo [OK] High Error Rate alarm
    set /a PASS_COUNT+=1
) else (
    echo [FAIL] High Error Rate alarm missing
    set /a FAIL_COUNT+=1
)

aws cloudwatch describe-alarms --alarm-names "%FUNCTION_NAME%-HighDuration" --region %REGION% | findstr /C:"HighDuration" >nul
if %errorlevel% equ 0 (
    echo [OK] High Duration alarm
    set /a PASS_COUNT+=1
) else (
    echo [FAIL] High Duration alarm missing
    set /a FAIL_COUNT+=1
)

aws cloudwatch describe-alarms --alarm-names "%FUNCTION_NAME%-Throttles" --region %REGION% | findstr /C:"Throttles" >nul
if %errorlevel% equ 0 (
    echo [OK] Throttles alarm
    set /a PASS_COUNT+=1
) else (
    echo [FAIL] Throttles alarm missing
    set /a FAIL_COUNT+=1
)

aws cloudwatch describe-alarms --alarm-names "%API_NAME%-High5XXErrors" --region %REGION% | findstr /C:"High5XXErrors" >nul
if %errorlevel% equ 0 (
    echo [OK] API 5XX Errors alarm
    set /a PASS_COUNT+=1
) else (
    echo [FAIL] API 5XX Errors alarm missing
    set /a FAIL_COUNT+=1
)

aws cloudwatch describe-alarms --alarm-names "%API_NAME%-HighLatency" --region %REGION% | findstr /C:"HighLatency" >nul
if %errorlevel% equ 0 (
    echo [OK] API High Latency alarm
    set /a PASS_COUNT+=1
) else (
    echo [FAIL] API High Latency alarm missing
    set /a FAIL_COUNT+=1
)

echo.

REM Check 4: Metric Filters
echo Checking Metric Filters...

aws logs describe-metric-filters --log-group-name "/aws/lambda/%FUNCTION_NAME%" --region %REGION% | findstr /C:"ProcessingTime" >nul
if %errorlevel% equ 0 (
    echo [OK] ProcessingTime metric filter
    set /a PASS_COUNT+=1
) else (
    echo [FAIL] ProcessingTime metric filter missing
    set /a FAIL_COUNT+=1
)

aws logs describe-metric-filters --log-group-name "/aws/lambda/%FUNCTION_NAME%" --region %REGION% | findstr /C:"DocumentUploads" >nul
if %errorlevel% equ 0 (
    echo [OK] DocumentUploads metric filter
    set /a PASS_COUNT+=1
) else (
    echo [FAIL] DocumentUploads metric filter missing
    set /a FAIL_COUNT+=1
)

echo.

REM Check 5: Log Retention
echo Checking Log Retention...
for /f "tokens=*" %%i in ('aws logs describe-log-groups --log-group-name-prefix "/aws/lambda/%FUNCTION_NAME%" --region %REGION% --query "logGroups[0].retentionInDays" --output text 2^>nul') do set RETENTION=%%i

if "%RETENTION%"=="7" (
    echo [OK] Log retention set to 7 days
    set /a PASS_COUNT+=1
) else if "%RETENTION%"=="None" (
    echo [WARNING] Log retention not set (logs never expire^)
) else (
    echo [WARNING] Log retention set to %RETENTION% days (expected 7^)
)

echo.

REM Summary
echo ==========================================
echo Verification Summary
echo ==========================================
echo.
echo Passed: %PASS_COUNT%
echo Failed: %FAIL_COUNT%
echo.

if %FAIL_COUNT% equ 0 (
    echo [OK] All checks passed!
    echo.
    echo Monitoring is properly configured.
    echo.
    echo View Dashboard:
    echo   https://console.aws.amazon.com/cloudwatch/home?region=%REGION%#dashboards:name=%DASHBOARD_NAME%
    echo.
    echo View Logs:
    echo   aws logs tail /aws/lambda/%FUNCTION_NAME% --follow
    echo.
    echo Next Steps:
    echo   1. Invoke Lambda to generate metrics
    echo   2. Check dashboard for data
    echo   3. Proceed to Task 12: End-to-end integration testing
    echo.
    exit /b 0
) else (
    echo [FAIL] Some checks failed
    echo.
    echo Please run the setup script to configure monitoring:
    echo   setup-cloudwatch-monitoring.bat
    echo.
    exit /b 1
)

endlocal
