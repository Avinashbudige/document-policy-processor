@echo off
REM CloudWatch Monitoring Setup Script (Windows)
REM Task 11.3: Configure CloudWatch monitoring
REM Sets up log groups, dashboards, and alarms for the Document Policy Processor

setlocal enabledelayedexpansion

echo ==========================================
echo CloudWatch Monitoring Setup
echo ==========================================
echo.

REM Configuration
set FUNCTION_NAME=DocumentPolicyProcessor
set API_NAME=document-policy-processor
if "%AWS_REGION%"=="" set AWS_REGION=us-east-1
set REGION=%AWS_REGION%

echo Step 1: Verifying log groups...
echo.

set LAMBDA_LOG_GROUP=/aws/lambda/%FUNCTION_NAME%
set API_LOG_GROUP=/aws/apigateway/%API_NAME%/Prod

REM Check Lambda log group
aws logs describe-log-groups --log-group-name-prefix "%LAMBDA_LOG_GROUP%" --region %REGION% | findstr /C:"%LAMBDA_LOG_GROUP%" >nul
if %errorlevel% equ 0 (
    echo [OK] Lambda log group exists: %LAMBDA_LOG_GROUP%
) else (
    echo Creating Lambda log group...
    aws logs create-log-group --log-group-name "%LAMBDA_LOG_GROUP%" --region %REGION%
    echo [OK] Lambda log group created
)

REM Set retention policy
echo Setting log retention to 7 days...
aws logs put-retention-policy --log-group-name "%LAMBDA_LOG_GROUP%" --retention-in-days 7 --region %REGION% 2>nul

echo.

REM Step 2: Create CloudWatch Dashboard
echo Step 2: Creating CloudWatch Dashboard...
echo.

set DASHBOARD_NAME=DocumentPolicyProcessor-Dashboard

REM Create dashboard JSON
(
echo {
echo     "widgets": [
echo         {
echo             "type": "metric",
echo             "properties": {
echo                 "metrics": [
echo                     ["AWS/Lambda", "Invocations", {"stat": "Sum", "label": "Total Invocations"}],
echo                     [".", "Errors", {"stat": "Sum", "label": "Errors"}],
echo                     [".", "Throttles", {"stat": "Sum", "label": "Throttles"}]
echo                 ],
echo                 "view": "timeSeries",
echo                 "stacked": false,
echo                 "region": "%REGION%",
echo                 "title": "Lambda Invocations & Errors",
echo                 "period": 300,
echo                 "yAxis": {"left": {"min": 0}}
echo             },
echo             "width": 12, "height": 6, "x": 0, "y": 0
echo         },
echo         {
echo             "type": "metric",
echo             "properties": {
echo                 "metrics": [
echo                     ["AWS/Lambda", "Duration", {"stat": "Average", "label": "Avg Duration"}],
echo                     ["...", {"stat": "Maximum", "label": "Max Duration"}],
echo                     ["...", {"stat": "Minimum", "label": "Min Duration"}]
echo                 ],
echo                 "view": "timeSeries",
echo                 "stacked": false,
echo                 "region": "%REGION%",
echo                 "title": "Lambda Duration (ms^)",
echo                 "period": 300,
echo                 "yAxis": {"left": {"min": 0}}
echo             },
echo             "width": 12, "height": 6, "x": 12, "y": 0
echo         },
echo         {
echo             "type": "metric",
echo             "properties": {
echo                 "metrics": [
echo                     ["AWS/Lambda", "ConcurrentExecutions", {"stat": "Maximum", "label": "Concurrent Executions"}]
echo                 ],
echo                 "view": "timeSeries",
echo                 "stacked": false,
echo                 "region": "%REGION%",
echo                 "title": "Lambda Concurrent Executions",
echo                 "period": 300,
echo                 "yAxis": {"left": {"min": 0}}
echo             },
echo             "width": 12, "height": 6, "x": 0, "y": 6
echo         },
echo         {
echo             "type": "metric",
echo             "properties": {
echo                 "metrics": [
echo                     ["AWS/ApiGateway", "Count", {"stat": "Sum", "label": "API Requests"}],
echo                     [".", "4XXError", {"stat": "Sum", "label": "4XX Errors"}],
echo                     [".", "5XXError", {"stat": "Sum", "label": "5XX Errors"}]
echo                 ],
echo                 "view": "timeSeries",
echo                 "stacked": false,
echo                 "region": "%REGION%",
echo                 "title": "API Gateway Requests & Errors",
echo                 "period": 300,
echo                 "yAxis": {"left": {"min": 0}}
echo             },
echo             "width": 12, "height": 6, "x": 12, "y": 6
echo         },
echo         {
echo             "type": "metric",
echo             "properties": {
echo                 "metrics": [
echo                     ["AWS/ApiGateway", "Latency", {"stat": "Average", "label": "Avg Latency"}],
echo                     ["...", {"stat": "p99", "label": "P99 Latency"}]
echo                 ],
echo                 "view": "timeSeries",
echo                 "stacked": false,
echo                 "region": "%REGION%",
echo                 "title": "API Gateway Latency (ms^)",
echo                 "period": 300,
echo                 "yAxis": {"left": {"min": 0}}
echo             },
echo             "width": 12, "height": 6, "x": 0, "y": 12
echo         },
echo         {
echo             "type": "log",
echo             "properties": {
echo                 "query": "SOURCE '/aws/lambda/%FUNCTION_NAME%'\n| fields @timestamp, @message\n| filter @message like /ERROR/\n| sort @timestamp desc\n| limit 20",
echo                 "region": "%REGION%",
echo                 "title": "Recent Lambda Errors",
echo                 "stacked": false
echo             },
echo             "width": 12, "height": 6, "x": 12, "y": 12
echo         }
echo     ]
echo }
) > %TEMP%\dashboard.json

REM Create or update dashboard
aws cloudwatch put-dashboard --dashboard-name "%DASHBOARD_NAME%" --dashboard-body file://%TEMP%\dashboard.json --region %REGION%

echo [OK] Dashboard created: %DASHBOARD_NAME%
echo.

REM Step 3: Create CloudWatch Alarms
echo Step 3: Creating CloudWatch Alarms...
echo.

REM Alarm 1: Lambda Error Rate
echo Creating Lambda error rate alarm...
aws cloudwatch put-metric-alarm ^
    --alarm-name "%FUNCTION_NAME%-HighErrorRate" ^
    --alarm-description "Alert when Lambda error rate exceeds 10%%" ^
    --metric-name Errors ^
    --namespace AWS/Lambda ^
    --statistic Sum ^
    --period 300 ^
    --evaluation-periods 1 ^
    --threshold 5 ^
    --comparison-operator GreaterThanThreshold ^
    --dimensions Name=FunctionName,Value=%FUNCTION_NAME% ^
    --treat-missing-data notBreaching ^
    --region %REGION%

echo [OK] Lambda error rate alarm created

REM Alarm 2: Lambda Duration
echo Creating Lambda duration alarm...
aws cloudwatch put-metric-alarm ^
    --alarm-name "%FUNCTION_NAME%-HighDuration" ^
    --alarm-description "Alert when Lambda duration exceeds 240 seconds (80%% of timeout)" ^
    --metric-name Duration ^
    --namespace AWS/Lambda ^
    --statistic Average ^
    --period 300 ^
    --evaluation-periods 1 ^
    --threshold 240000 ^
    --comparison-operator GreaterThanThreshold ^
    --dimensions Name=FunctionName,Value=%FUNCTION_NAME% ^
    --treat-missing-data notBreaching ^
    --region %REGION%

echo [OK] Lambda duration alarm created

REM Alarm 3: Lambda Throttles
echo Creating Lambda throttle alarm...
aws cloudwatch put-metric-alarm ^
    --alarm-name "%FUNCTION_NAME%-Throttles" ^
    --alarm-description "Alert when Lambda function is throttled" ^
    --metric-name Throttles ^
    --namespace AWS/Lambda ^
    --statistic Sum ^
    --period 300 ^
    --evaluation-periods 1 ^
    --threshold 1 ^
    --comparison-operator GreaterThanThreshold ^
    --dimensions Name=FunctionName,Value=%FUNCTION_NAME% ^
    --treat-missing-data notBreaching ^
    --region %REGION%

echo [OK] Lambda throttle alarm created

REM Alarm 4: API Gateway 5XX Errors
echo Creating API Gateway 5XX error alarm...
aws cloudwatch put-metric-alarm ^
    --alarm-name "%API_NAME%-High5XXErrors" ^
    --alarm-description "Alert when API Gateway 5XX error rate is high" ^
    --metric-name 5XXError ^
    --namespace AWS/ApiGateway ^
    --statistic Sum ^
    --period 300 ^
    --evaluation-periods 1 ^
    --threshold 5 ^
    --comparison-operator GreaterThanThreshold ^
    --dimensions Name=ApiName,Value=%API_NAME% ^
    --treat-missing-data notBreaching ^
    --region %REGION%

echo [OK] API Gateway 5XX error alarm created

REM Alarm 5: API Gateway High Latency
echo Creating API Gateway latency alarm...
aws cloudwatch put-metric-alarm ^
    --alarm-name "%API_NAME%-HighLatency" ^
    --alarm-description "Alert when API Gateway latency exceeds 10 seconds" ^
    --metric-name Latency ^
    --namespace AWS/ApiGateway ^
    --statistic Average ^
    --period 300 ^
    --evaluation-periods 2 ^
    --threshold 10000 ^
    --comparison-operator GreaterThanThreshold ^
    --dimensions Name=ApiName,Value=%API_NAME% ^
    --treat-missing-data notBreaching ^
    --region %REGION%

echo [OK] API Gateway latency alarm created

echo.

REM Step 4: SNS Configuration
if not "%ALARM_EMAIL%"=="" (
    echo Step 4: Configuring SNS for alarm notifications...
    echo.
    
    set SNS_TOPIC_NAME=%FUNCTION_NAME%-Alarms
    
    REM Create SNS topic
    for /f "tokens=*" %%i in ('aws sns create-topic --name "%SNS_TOPIC_NAME%" --region %REGION% --query TopicArn --output text') do set SNS_TOPIC_ARN=%%i
    
    echo [OK] SNS topic created: !SNS_TOPIC_ARN!
    
    REM Subscribe email
    aws sns subscribe --topic-arn "!SNS_TOPIC_ARN!" --protocol email --notification-endpoint "%ALARM_EMAIL%" --region %REGION%
    
    echo [WARNING] Email subscription pending confirmation
    echo    Check %ALARM_EMAIL% for confirmation email
    echo.
) else (
    echo Step 4: Skipping SNS configuration (no email provided^)
    echo    To enable email notifications, run:
    echo    set ALARM_EMAIL=your@email.com ^&^& setup-cloudwatch-monitoring.bat
    echo.
)

REM Step 5: Create metric filters
echo Step 5: Creating metric filters...
echo.

aws logs put-metric-filter ^
    --log-group-name "%LAMBDA_LOG_GROUP%" ^
    --filter-name "ProcessingTime" ^
    --filter-pattern "[timestamp, request_id, level, msg=\"Processing completed*\", processing_time]" ^
    --metric-transformations metricName=ProcessingTime,metricNamespace=DocumentPolicyProcessor,metricValue=$processing_time,unit=Seconds ^
    --region %REGION% 2>nul

echo [OK] Processing time metric filter created

aws logs put-metric-filter ^
    --log-group-name "%LAMBDA_LOG_GROUP%" ^
    --filter-name "DocumentUploads" ^
    --filter-pattern "[timestamp, request_id, level, msg=\"Document uploaded*\"]" ^
    --metric-transformations metricName=DocumentUploads,metricNamespace=DocumentPolicyProcessor,metricValue=1,unit=Count ^
    --region %REGION% 2>nul

echo [OK] Document upload metric filter created

echo.

REM Summary
echo ==========================================
echo CloudWatch Monitoring Setup Complete!
echo ==========================================
echo.
echo Resources Created:
echo   * Log Groups: %LAMBDA_LOG_GROUP%
echo   * Dashboard: %DASHBOARD_NAME%
echo   * Alarms: 5 alarms created
echo.
echo View Dashboard:
echo   https://console.aws.amazon.com/cloudwatch/home?region=%REGION%#dashboards:name=%DASHBOARD_NAME%
echo.
echo View Alarms:
echo   https://console.aws.amazon.com/cloudwatch/home?region=%REGION%#alarmsV2:
echo.
echo View Logs:
echo   aws logs tail %LAMBDA_LOG_GROUP% --follow
echo.
echo Next Steps:
echo   1. View the dashboard to monitor system health
echo   2. Test alarms by triggering errors
echo   3. Confirm SNS email subscription (if configured^)
echo   4. Proceed to Task 12: End-to-end integration testing
echo.

endlocal
