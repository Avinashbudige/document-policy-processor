# CloudWatch Monitoring Quick Reference

## Quick Setup

### Linux/Mac
```bash
chmod +x setup-cloudwatch-monitoring.sh
./setup-cloudwatch-monitoring.sh
```

### Windows
```cmd
setup-cloudwatch-monitoring.bat
```

### With Email Notifications
```bash
# Linux/Mac
ALARM_EMAIL=your@email.com ./setup-cloudwatch-monitoring.sh

# Windows
set ALARM_EMAIL=your@email.com && setup-cloudwatch-monitoring.bat
```

## Dashboard Access

**Direct Link:**
```
https://console.aws.amazon.com/cloudwatch/home?region=us-east-1#dashboards:name=DocumentPolicyProcessor-Dashboard
```

**CLI:**
```bash
aws cloudwatch get-dashboard \
  --dashboard-name DocumentPolicyProcessor-Dashboard \
  --region us-east-1
```

## View Logs

### Lambda Logs (Live Tail)
```bash
aws logs tail /aws/lambda/DocumentPolicyProcessor --follow
```

### Recent Errors Only
```bash
aws logs tail /aws/lambda/DocumentPolicyProcessor \
  --filter-pattern "ERROR" \
  --follow
```

### Last 100 Lines
```bash
aws logs tail /aws/lambda/DocumentPolicyProcessor --since 1h
```

### API Gateway Logs
```bash
aws logs tail /aws/apigateway/document-policy-processor/Prod --follow
```

## Check Alarms

### List All Alarms
```bash
aws cloudwatch describe-alarms \
  --alarm-name-prefix "DocumentPolicyProcessor" \
  --region us-east-1
```

### Check Alarm State
```bash
aws cloudwatch describe-alarms \
  --alarm-names "DocumentPolicyProcessor-HighErrorRate" \
  --query 'MetricAlarms[0].StateValue' \
  --output text
```

### View Alarm History
```bash
aws cloudwatch describe-alarm-history \
  --alarm-name "DocumentPolicyProcessor-HighErrorRate" \
  --max-records 10
```

## Key Metrics

### Lambda Invocations (Last Hour)
```bash
aws cloudwatch get-metric-statistics \
  --namespace AWS/Lambda \
  --metric-name Invocations \
  --dimensions Name=FunctionName,Value=DocumentPolicyProcessor \
  --start-time $(date -u -d '1 hour ago' +%Y-%m-%dT%H:%M:%S) \
  --end-time $(date -u +%Y-%m-%dT%H:%M:%S) \
  --period 300 \
  --statistics Sum
```

### Lambda Error Rate
```bash
aws cloudwatch get-metric-statistics \
  --namespace AWS/Lambda \
  --metric-name Errors \
  --dimensions Name=FunctionName,Value=DocumentPolicyProcessor \
  --start-time $(date -u -d '1 hour ago' +%Y-%m-%dT%H:%M:%S) \
  --end-time $(date -u +%Y-%m-%dT%H:%M:%S) \
  --period 300 \
  --statistics Sum
```

### Lambda Duration (Average)
```bash
aws cloudwatch get-metric-statistics \
  --namespace AWS/Lambda \
  --metric-name Duration \
  --dimensions Name=FunctionName,Value=DocumentPolicyProcessor \
  --start-time $(date -u -d '1 hour ago' +%Y-%m-%dT%H:%M:%S) \
  --end-time $(date -u +%Y-%m-%dT%H:%M:%S) \
  --period 300 \
  --statistics Average,Maximum
```

### API Gateway Request Count
```bash
aws cloudwatch get-metric-statistics \
  --namespace AWS/ApiGateway \
  --metric-name Count \
  --dimensions Name=ApiName,Value=document-policy-processor \
  --start-time $(date -u -d '1 hour ago' +%Y-%m-%dT%H:%M:%S) \
  --end-time $(date -u +%Y-%m-%dT%H:%M:%S) \
  --period 300 \
  --statistics Sum
```

## Configured Alarms

| Alarm Name | Metric | Threshold | Description |
|------------|--------|-----------|-------------|
| **DocumentPolicyProcessor-HighErrorRate** | Lambda Errors | > 5 errors in 5 min | High error rate alert |
| **DocumentPolicyProcessor-HighDuration** | Lambda Duration | > 240 seconds | Near timeout warning |
| **DocumentPolicyProcessor-Throttles** | Lambda Throttles | > 1 throttle in 5 min | Function throttled |
| **document-policy-processor-High5XXErrors** | API 5XX Errors | > 5 errors in 5 min | Server errors |
| **document-policy-processor-HighLatency** | API Latency | > 10 seconds | High latency warning |

## Dashboard Widgets

The dashboard includes:

1. **Lambda Invocations & Errors** - Total invocations, errors, and throttles
2. **Lambda Duration** - Average, max, and min execution time
3. **Lambda Concurrent Executions** - Number of concurrent executions
4. **API Gateway Requests & Errors** - Request count, 4XX and 5XX errors
5. **API Gateway Latency** - Average and P99 latency
6. **Recent Lambda Errors** - Log insights query showing recent errors

## Custom Metrics

The setup creates custom metric filters:

### Processing Time
Tracks document processing duration from Lambda logs.

**Namespace:** `DocumentPolicyProcessor`  
**Metric:** `ProcessingTime`  
**Unit:** Seconds

### Document Uploads
Counts successful document uploads.

**Namespace:** `DocumentPolicyProcessor`  
**Metric:** `DocumentUploads`  
**Unit:** Count

## Log Insights Queries

### Find Slow Requests
```
fields @timestamp, @message
| filter @message like /Processing completed/
| parse @message /processing_time: (?<duration>\d+)/
| filter duration > 30
| sort @timestamp desc
| limit 20
```

### Error Analysis
```
fields @timestamp, @message
| filter @message like /ERROR/
| stats count() by bin(5m)
```

### Request Volume by Endpoint
```
fields @timestamp, @message
| filter @message like /httpMethod/
| parse @message /"httpMethod":"(?<method>[^"]+)"/
| parse @message /"path":"(?<path>[^"]+)"/
| stats count() by method, path
```

### Average Processing Time
```
fields @timestamp, @message
| filter @message like /Processing completed/
| parse @message /processing_time: (?<duration>\d+)/
| stats avg(duration) as avg_duration, max(duration) as max_duration
```

## Troubleshooting

### High Error Rate
1. Check recent errors:
   ```bash
   aws logs tail /aws/lambda/DocumentPolicyProcessor --filter-pattern "ERROR" --since 1h
   ```
2. Review alarm history
3. Check Lambda configuration (memory, timeout)
4. Verify environment variables

### High Latency
1. Check Lambda duration metrics
2. Review cold start frequency
3. Check external API response times (OpenAI, Textract)
4. Consider increasing Lambda memory

### Missing Metrics
1. Verify log groups exist
2. Check metric filter configuration
3. Ensure Lambda is being invoked
4. Wait 5-10 minutes for metrics to appear

### Alarm Not Triggering
1. Check alarm state: `aws cloudwatch describe-alarms`
2. Verify metric data exists
3. Check alarm threshold and evaluation periods
4. Review alarm configuration

## Cost Optimization

### Log Retention
Logs are set to 7-day retention to minimize costs.

**Change retention:**
```bash
aws logs put-retention-policy \
  --log-group-name /aws/lambda/DocumentPolicyProcessor \
  --retention-in-days 14
```

### Disable Alarms (if needed)
```bash
aws cloudwatch disable-alarm-actions \
  --alarm-names "DocumentPolicyProcessor-HighErrorRate"
```

### Delete Dashboard (if needed)
```bash
aws cloudwatch delete-dashboards \
  --dashboard-names DocumentPolicyProcessor-Dashboard
```

## Email Notifications

If you configured email notifications:

1. Check your email for AWS SNS confirmation
2. Click the confirmation link
3. Alarms will now send emails when triggered

**Test alarm notification:**
```bash
aws cloudwatch set-alarm-state \
  --alarm-name "DocumentPolicyProcessor-HighErrorRate" \
  --state-value ALARM \
  --state-reason "Testing alarm notification"
```

## Monitoring Best Practices

1. **Check dashboard daily** during active development
2. **Review error logs** when alarms trigger
3. **Monitor costs** in CloudWatch billing
4. **Set up SNS notifications** for production
5. **Create custom metrics** for business KPIs
6. **Use Log Insights** for deep analysis
7. **Archive old logs** to S3 for long-term storage

## Next Steps

1. ✓ Configure CloudWatch monitoring (Task 11.3)
2. ⏭ End-to-end integration testing (Task 12)
3. ⏭ Create demo video (Task 13)
4. ⏭ Write project documentation (Task 14)

## Support Resources

- **Full Documentation:** [TASK_11.3_CLOUDWATCH_MONITORING.md](TASK_11.3_CLOUDWATCH_MONITORING.md)
- **Lambda Deployment:** [LAMBDA_DEPLOYMENT_QUICK_REFERENCE.md](LAMBDA_DEPLOYMENT_QUICK_REFERENCE.md)
- **API Gateway:** [API_GATEWAY_QUICK_REFERENCE.md](API_GATEWAY_QUICK_REFERENCE.md)
- **AWS CloudWatch Docs:** https://docs.aws.amazon.com/cloudwatch/

---

**Last Updated:** January 2025  
**Task:** 11.3 Configure CloudWatch monitoring  
**Status:** Complete ✓
