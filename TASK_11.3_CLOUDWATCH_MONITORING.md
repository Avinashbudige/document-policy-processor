# Task 11.3: CloudWatch Monitoring Configuration

## Overview

This document provides comprehensive guidance for configuring CloudWatch monitoring for the Document Policy Processor. The monitoring setup includes log groups, dashboards, alarms, and custom metrics to ensure system health and performance visibility.

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Quick Start](#quick-start)
3. [Components](#components)
4. [Setup Process](#setup-process)
5. [Dashboard Details](#dashboard-details)
6. [Alarms Configuration](#alarms-configuration)
7. [Custom Metrics](#custom-metrics)
8. [Log Insights Queries](#log-insights-queries)
9. [Monitoring Best Practices](#monitoring-best-practices)
10. [Troubleshooting](#troubleshooting)
11. [Cost Considerations](#cost-considerations)

## Prerequisites

Before setting up CloudWatch monitoring, ensure:

- ✓ Lambda function deployed (Task 11.1)
- ✓ API Gateway deployed (Task 11.2)
- ✓ AWS CLI configured with appropriate permissions
- ✓ IAM permissions for CloudWatch (logs, dashboards, alarms, metrics)

## Quick Start

### Automated Setup

The fastest way to configure monitoring is using the provided scripts:

**Linux/Mac:**
```bash
chmod +x setup-cloudwatch-monitoring.sh
./setup-cloudwatch-monitoring.sh
```

**Windows:**
```cmd
setup-cloudwatch-monitoring.bat
```

**With Email Notifications:**
```bash
# Linux/Mac
ALARM_EMAIL=your@email.com ./setup-cloudwatch-monitoring.sh

# Windows
set ALARM_EMAIL=your@email.com && setup-cloudwatch-monitoring.bat
```

### Manual Setup

If you prefer manual configuration, follow the [Setup Process](#setup-process) section below.

## Components

The monitoring setup includes:

### 1. Log Groups

| Log Group | Purpose | Retention |
|-----------|---------|-----------|
| `/aws/lambda/DocumentPolicyProcessor` | Lambda function logs | 7 days |
| `/aws/apigateway/document-policy-processor/Prod` | API Gateway access logs | 7 days |

### 2. CloudWatch Dashboard

**Name:** `DocumentPolicyProcessor-Dashboard`

**Widgets:**
- Lambda invocations, errors, and throttles
- Lambda duration (avg, max, min)
- Lambda concurrent executions
- API Gateway requests and errors (4XX, 5XX)
- API Gateway latency (avg, P99)
- Recent Lambda errors (Log Insights query)

### 3. CloudWatch Alarms

| Alarm | Metric | Threshold | Evaluation Period |
|-------|--------|-----------|-------------------|
| High Error Rate | Lambda Errors | > 5 errors | 5 minutes |
| High Duration | Lambda Duration | > 240 seconds | 5 minutes |
| Throttles | Lambda Throttles | > 1 throttle | 5 minutes |
| API 5XX Errors | API Gateway 5XXError | > 5 errors | 5 minutes |
| High Latency | API Gateway Latency | > 10 seconds | 10 minutes (2 periods) |

### 4. Custom Metrics

| Metric | Namespace | Description |
|--------|-----------|-------------|
| ProcessingTime | DocumentPolicyProcessor | Document processing duration |
| DocumentUploads | DocumentPolicyProcessor | Count of document uploads |

### 5. SNS Topic (Optional)

**Name:** `DocumentPolicyProcessor-Alarms`

**Purpose:** Email notifications for alarm triggers

## Setup Process

### Step 1: Verify Log Groups

Check if log groups exist:

```bash
aws logs describe-log-groups \
  --log-group-name-prefix "/aws/lambda/DocumentPolicyProcessor" \
  --region us-east-1
```

Create if missing:

```bash
aws logs create-log-group \
  --log-group-name "/aws/lambda/DocumentPolicyProcessor" \
  --region us-east-1
```

Set retention policy:

```bash
aws logs put-retention-policy \
  --log-group-name "/aws/lambda/DocumentPolicyProcessor" \
  --retention-in-days 7 \
  --region us-east-1
```

### Step 2: Create CloudWatch Dashboard

The dashboard provides a unified view of system health. See [dashboard.json](setup-cloudwatch-monitoring.sh) for the complete configuration.

**Create dashboard:**

```bash
aws cloudwatch put-dashboard \
  --dashboard-name "DocumentPolicyProcessor-Dashboard" \
  --dashboard-body file://dashboard.json \
  --region us-east-1
```

**Access dashboard:**

```
https://console.aws.amazon.com/cloudwatch/home?region=us-east-1#dashboards:name=DocumentPolicyProcessor-Dashboard
```

### Step 3: Create CloudWatch Alarms

#### Alarm 1: High Error Rate

Triggers when Lambda function has more than 5 errors in 5 minutes.

```bash
aws cloudwatch put-metric-alarm \
  --alarm-name "DocumentPolicyProcessor-HighErrorRate" \
  --alarm-description "Alert when Lambda error rate exceeds 10%" \
  --metric-name Errors \
  --namespace AWS/Lambda \
  --statistic Sum \
  --period 300 \
  --evaluation-periods 1 \
  --threshold 5 \
  --comparison-operator GreaterThanThreshold \
  --dimensions Name=FunctionName,Value=DocumentPolicyProcessor \
  --treat-missing-data notBreaching \
  --region us-east-1
```

**Why this matters:** High error rates indicate bugs, configuration issues, or external service failures.

#### Alarm 2: High Duration

Triggers when Lambda execution time exceeds 240 seconds (80% of 300s timeout).

```bash
aws cloudwatch put-metric-alarm \
  --alarm-name "DocumentPolicyProcessor-HighDuration" \
  --alarm-description "Alert when Lambda duration exceeds 240 seconds" \
  --metric-name Duration \
  --namespace AWS/Lambda \
  --statistic Average \
  --period 300 \
  --evaluation-periods 1 \
  --threshold 240000 \
  --comparison-operator GreaterThanThreshold \
  --dimensions Name=FunctionName,Value=DocumentPolicyProcessor \
  --treat-missing-data notBreaching \
  --region us-east-1
```

**Why this matters:** Near-timeout executions may fail, causing poor user experience.

#### Alarm 3: Throttles

Triggers when Lambda function is throttled (concurrent execution limit reached).

```bash
aws cloudwatch put-metric-alarm \
  --alarm-name "DocumentPolicyProcessor-Throttles" \
  --alarm-description "Alert when Lambda function is throttled" \
  --metric-name Throttles \
  --namespace AWS/Lambda \
  --statistic Sum \
  --period 300 \
  --evaluation-periods 1 \
  --threshold 1 \
  --comparison-operator GreaterThanThreshold \
  --dimensions Name=FunctionName,Value=DocumentPolicyProcessor \
  --treat-missing-data notBreaching \
  --region us-east-1
```

**Why this matters:** Throttling means requests are being rejected due to capacity limits.

#### Alarm 4: API Gateway 5XX Errors

Triggers when API Gateway returns more than 5 server errors in 5 minutes.

```bash
aws cloudwatch put-metric-alarm \
  --alarm-name "document-policy-processor-High5XXErrors" \
  --alarm-description "Alert when API Gateway 5XX error rate is high" \
  --metric-name 5XXError \
  --namespace AWS/ApiGateway \
  --statistic Sum \
  --period 300 \
  --evaluation-periods 1 \
  --threshold 5 \
  --comparison-operator GreaterThanThreshold \
  --dimensions Name=ApiName,Value=document-policy-processor \
  --treat-missing-data notBreaching \
  --region us-east-1
```

**Why this matters:** 5XX errors indicate backend failures or misconfigurations.

#### Alarm 5: High Latency

Triggers when API Gateway latency exceeds 10 seconds for 2 consecutive periods.

```bash
aws cloudwatch put-metric-alarm \
  --alarm-name "document-policy-processor-HighLatency" \
  --alarm-description "Alert when API Gateway latency exceeds 10 seconds" \
  --metric-name Latency \
  --namespace AWS/ApiGateway \
  --statistic Average \
  --period 300 \
  --evaluation-periods 2 \
  --threshold 10000 \
  --comparison-operator GreaterThanThreshold \
  --dimensions Name=ApiName,Value=document-policy-processor \
  --treat-missing-data notBreaching \
  --region us-east-1
```

**Why this matters:** High latency degrades user experience and may indicate performance issues.

### Step 4: Configure SNS for Email Notifications (Optional)

Create SNS topic:

```bash
SNS_TOPIC_ARN=$(aws sns create-topic \
  --name "DocumentPolicyProcessor-Alarms" \
  --region us-east-1 \
  --query 'TopicArn' \
  --output text)

echo $SNS_TOPIC_ARN
```

Subscribe email:

```bash
aws sns subscribe \
  --topic-arn "$SNS_TOPIC_ARN" \
  --protocol email \
  --notification-endpoint "your@email.com" \
  --region us-east-1
```

**Important:** Check your email and confirm the subscription.

Update alarms to send notifications:

```bash
aws cloudwatch put-metric-alarm \
  --alarm-name "DocumentPolicyProcessor-HighErrorRate" \
  --alarm-actions "$SNS_TOPIC_ARN" \
  --region us-east-1
```

Repeat for all alarms.

### Step 5: Create Metric Filters

Metric filters extract custom metrics from log data.

#### Processing Time Filter

Extracts processing duration from Lambda logs:

```bash
aws logs put-metric-filter \
  --log-group-name "/aws/lambda/DocumentPolicyProcessor" \
  --filter-name "ProcessingTime" \
  --filter-pattern '[timestamp, request_id, level, msg="Processing completed*", processing_time]' \
  --metric-transformations \
    metricName=ProcessingTime,\
metricNamespace=DocumentPolicyProcessor,\
metricValue='$processing_time',\
unit=Seconds \
  --region us-east-1
```

**Log format expected:**
```
2025-01-24T12:00:00Z abc123 INFO Processing completed in 45.2 seconds
```

#### Document Upload Filter

Counts document uploads:

```bash
aws logs put-metric-filter \
  --log-group-name "/aws/lambda/DocumentPolicyProcessor" \
  --filter-name "DocumentUploads" \
  --filter-pattern '[timestamp, request_id, level, msg="Document uploaded*"]' \
  --metric-transformations \
    metricName=DocumentUploads,\
metricNamespace=DocumentPolicyProcessor,\
metricValue=1,\
unit=Count \
  --region us-east-1
```

## Dashboard Details

### Widget 1: Lambda Invocations & Errors

**Metrics:**
- Total invocations (sum)
- Errors (sum)
- Throttles (sum)

**Purpose:** Monitor overall Lambda activity and error rate.

**What to look for:**
- Sudden spikes in errors
- Throttling events
- Unusual invocation patterns

### Widget 2: Lambda Duration

**Metrics:**
- Average duration
- Maximum duration
- Minimum duration

**Purpose:** Track execution time and identify performance issues.

**What to look for:**
- Increasing average duration (performance degradation)
- Max duration approaching timeout (300s)
- High variance between min and max (cold starts)

### Widget 3: Lambda Concurrent Executions

**Metrics:**
- Maximum concurrent executions

**Purpose:** Monitor concurrency and capacity.

**What to look for:**
- Approaching account limits (default: 1000)
- Sudden spikes indicating traffic bursts

### Widget 4: API Gateway Requests & Errors

**Metrics:**
- Total requests (sum)
- 4XX errors (sum)
- 5XX errors (sum)

**Purpose:** Monitor API health and client/server errors.

**What to look for:**
- High 4XX rate (client errors, auth issues)
- Any 5XX errors (server failures)
- Request volume trends

### Widget 5: API Gateway Latency

**Metrics:**
- Average latency
- P99 latency

**Purpose:** Track API response times.

**What to look for:**
- P99 latency > 5 seconds (poor user experience)
- Increasing latency trends
- Latency spikes during peak hours

### Widget 6: Recent Lambda Errors

**Type:** Log Insights query

**Query:**
```
SOURCE '/aws/lambda/DocumentPolicyProcessor'
| fields @timestamp, @message
| filter @message like /ERROR/
| sort @timestamp desc
| limit 20
```

**Purpose:** Quick view of recent errors for debugging.

## Alarms Configuration

### Alarm States

- **OK:** Metric is within threshold
- **ALARM:** Metric has breached threshold
- **INSUFFICIENT_DATA:** Not enough data to evaluate

### Alarm Actions

When an alarm triggers:

1. **State changes to ALARM**
2. **SNS notification sent** (if configured)
3. **Email received** with alarm details
4. **CloudWatch console shows alarm state**

### Testing Alarms

Test alarm notifications:

```bash
aws cloudwatch set-alarm-state \
  --alarm-name "DocumentPolicyProcessor-HighErrorRate" \
  --state-value ALARM \
  --state-reason "Testing alarm notification"
```

### Viewing Alarm History

```bash
aws cloudwatch describe-alarm-history \
  --alarm-name "DocumentPolicyProcessor-HighErrorRate" \
  --max-records 10
```

## Custom Metrics

### Viewing Custom Metrics

**Processing Time:**
```bash
aws cloudwatch get-metric-statistics \
  --namespace DocumentPolicyProcessor \
  --metric-name ProcessingTime \
  --start-time $(date -u -d '1 hour ago' +%Y-%m-%dT%H:%M:%S) \
  --end-time $(date -u +%Y-%m-%dT%H:%M:%S) \
  --period 300 \
  --statistics Average,Maximum
```

**Document Uploads:**
```bash
aws cloudwatch get-metric-statistics \
  --namespace DocumentPolicyProcessor \
  --metric-name DocumentUploads \
  --start-time $(date -u -d '1 hour ago' +%Y-%m-%dT%H:%M:%S) \
  --end-time $(date -u +%Y-%m-%dT%H:%M:%S) \
  --period 300 \
  --statistics Sum
```

### Creating Additional Custom Metrics

To add more custom metrics:

1. **Add logging in Lambda code:**
   ```python
   logger.info(f"Policy matched: {policy_id}")
   ```

2. **Create metric filter:**
   ```bash
   aws logs put-metric-filter \
     --log-group-name "/aws/lambda/DocumentPolicyProcessor" \
     --filter-name "PolicyMatches" \
     --filter-pattern '[timestamp, request_id, level, msg="Policy matched*", policy_id]' \
     --metric-transformations \
       metricName=PolicyMatches,\
metricNamespace=DocumentPolicyProcessor,\
metricValue=1,\
unit=Count
   ```

## Log Insights Queries

### Query 1: Find Slow Requests

```
fields @timestamp, @message
| filter @message like /Processing completed/
| parse @message /processing_time: (?<duration>\d+)/
| filter duration > 30
| sort @timestamp desc
| limit 20
```

**Purpose:** Identify requests taking longer than 30 seconds.

### Query 2: Error Analysis

```
fields @timestamp, @message
| filter @message like /ERROR/
| stats count() by bin(5m)
```

**Purpose:** Visualize error frequency over time.

### Query 3: Request Volume by Endpoint

```
fields @timestamp, @message
| filter @message like /httpMethod/
| parse @message /"httpMethod":"(?<method>[^"]+)"/
| parse @message /"path":"(?<path>[^"]+)"/
| stats count() by method, path
```

**Purpose:** Understand which endpoints are most used.

### Query 4: Average Processing Time

```
fields @timestamp, @message
| filter @message like /Processing completed/
| parse @message /processing_time: (?<duration>\d+)/
| stats avg(duration) as avg_duration, max(duration) as max_duration
```

**Purpose:** Calculate average and max processing times.

### Query 5: Cold Start Analysis

```
fields @timestamp, @message, @initDuration
| filter @type = "REPORT"
| stats count(@initDuration) as cold_starts, avg(@initDuration) as avg_cold_start
```

**Purpose:** Measure cold start frequency and duration.

## Monitoring Best Practices

### 1. Regular Dashboard Reviews

- Check dashboard daily during development
- Review weekly in production
- Look for trends, not just current values

### 2. Set Appropriate Thresholds

- Start conservative, adjust based on actual behavior
- Consider business impact when setting thresholds
- Use percentiles (P95, P99) for latency metrics

### 3. Use Composite Alarms

Combine multiple metrics for smarter alerting:

```bash
aws cloudwatch put-composite-alarm \
  --alarm-name "DocumentPolicyProcessor-Critical" \
  --alarm-rule "ALARM(DocumentPolicyProcessor-HighErrorRate) OR ALARM(DocumentPolicyProcessor-Throttles)"
```

### 4. Log Structured Data

Use JSON logging for easier parsing:

```python
import json
logger.info(json.dumps({
    "event": "processing_completed",
    "duration": 45.2,
    "document_type": "pdf",
    "policy_matches": 3
}))
```

### 5. Archive Old Logs

Export logs to S3 for long-term storage:

```bash
aws logs create-export-task \
  --log-group-name "/aws/lambda/DocumentPolicyProcessor" \
  --from 1640995200000 \
  --to 1643673600000 \
  --destination "document-policy-processor-logs" \
  --destination-prefix "lambda-logs/"
```

### 6. Monitor Costs

CloudWatch costs can add up:

- Set log retention policies
- Use metric filters sparingly
- Archive old logs to S3
- Delete unused dashboards and alarms

## Troubleshooting

### Issue: No Metrics Appearing

**Possible causes:**
- Lambda not being invoked
- Metric filters misconfigured
- Insufficient permissions

**Solutions:**
1. Verify Lambda is running: `aws lambda invoke --function-name DocumentPolicyProcessor test.json`
2. Check metric filter syntax
3. Wait 5-10 minutes for metrics to appear
4. Verify IAM permissions for CloudWatch

### Issue: Alarms Not Triggering

**Possible causes:**
- Threshold too high
- Insufficient data
- Alarm disabled

**Solutions:**
1. Check alarm state: `aws cloudwatch describe-alarms`
2. Verify metric data exists
3. Test alarm manually: `aws cloudwatch set-alarm-state`
4. Review alarm configuration

### Issue: High CloudWatch Costs

**Possible causes:**
- Too many custom metrics
- Long log retention
- Frequent Log Insights queries

**Solutions:**
1. Reduce log retention to 7 days
2. Limit custom metrics to essential ones
3. Use metric filters instead of frequent queries
4. Archive old logs to S3

### Issue: Missing Log Data

**Possible causes:**
- Log group doesn't exist
- Lambda execution role lacks permissions
- Logs not being written

**Solutions:**
1. Verify log group exists
2. Check Lambda execution role has `logs:CreateLogStream` and `logs:PutLogEvents`
3. Add logging statements to Lambda code
4. Check Lambda configuration

## Cost Considerations

### CloudWatch Pricing (us-east-1)

| Component | Cost | Notes |
|-----------|------|-------|
| **Log Ingestion** | $0.50/GB | First 5GB free |
| **Log Storage** | $0.03/GB/month | After retention period |
| **Custom Metrics** | $0.30/metric/month | First 10 metrics free |
| **Dashboard** | $3/month | First 3 dashboards free |
| **Alarms** | $0.10/alarm/month | First 10 alarms free |
| **Log Insights Queries** | $0.005/GB scanned | |

### Estimated Monthly Cost

**Assumptions:**
- 1000 Lambda invocations/day
- 1MB logs per invocation
- 7-day retention
- 5 alarms
- 1 dashboard
- 2 custom metrics

**Calculation:**
- Log ingestion: 30GB × $0.50 = $15.00
- Log storage: ~1GB × $0.03 = $0.03
- Custom metrics: 0 (under free tier)
- Dashboard: 0 (under free tier)
- Alarms: 0 (under free tier)

**Total: ~$15/month**

### Cost Optimization Tips

1. **Reduce log retention** to 3-7 days
2. **Filter logs before ingestion** (if possible)
3. **Use metric filters** instead of Log Insights queries
4. **Archive old logs** to S3 ($0.023/GB/month)
5. **Delete unused dashboards** and alarms
6. **Limit custom metrics** to essential ones

## Verification

After setup, verify everything is working:

### 1. Check Log Groups
```bash
aws logs describe-log-groups --log-group-name-prefix "/aws/lambda/DocumentPolicyProcessor"
```

### 2. View Dashboard
```bash
aws cloudwatch get-dashboard --dashboard-name DocumentPolicyProcessor-Dashboard
```

### 3. List Alarms
```bash
aws cloudwatch describe-alarms --alarm-name-prefix "DocumentPolicyProcessor"
```

### 4. Test Lambda and Check Logs
```bash
# Invoke Lambda
aws lambda invoke --function-name DocumentPolicyProcessor \
  --payload '{"httpMethod":"GET","path":"/api/health"}' \
  response.json

# View logs
aws logs tail /aws/lambda/DocumentPolicyProcessor --since 5m
```

### 5. Verify Metrics
```bash
# Check Lambda invocations
aws cloudwatch get-metric-statistics \
  --namespace AWS/Lambda \
  --metric-name Invocations \
  --dimensions Name=FunctionName,Value=DocumentPolicyProcessor \
  --start-time $(date -u -d '1 hour ago' +%Y-%m-%dT%H:%M:%S) \
  --end-time $(date -u +%Y-%m-%dT%H:%M:%S) \
  --period 300 \
  --statistics Sum
```

## Next Steps

After completing CloudWatch monitoring setup:

1. ✓ **Task 11.3 Complete** - CloudWatch monitoring configured
2. **Task 12** - End-to-end integration testing
3. **Task 13** - Create demo video
4. **Task 14** - Write project documentation

## Support Resources

- **Quick Reference:** [CLOUDWATCH_MONITORING_QUICK_REFERENCE.md](CLOUDWATCH_MONITORING_QUICK_REFERENCE.md)
- **Lambda Deployment:** [LAMBDA_DEPLOYMENT_QUICK_REFERENCE.md](LAMBDA_DEPLOYMENT_QUICK_REFERENCE.md)
- **API Gateway:** [API_GATEWAY_QUICK_REFERENCE.md](API_GATEWAY_QUICK_REFERENCE.md)
- **AWS CloudWatch Docs:** https://docs.aws.amazon.com/cloudwatch/
- **CloudWatch Logs Insights:** https://docs.aws.amazon.com/AmazonCloudWatch/latest/logs/AnalyzingLogData.html

## Summary

CloudWatch monitoring provides essential visibility into the Document Policy Processor's health and performance. The setup includes:

- **Log groups** with 7-day retention for cost optimization
- **Dashboard** with 6 widgets covering Lambda and API Gateway metrics
- **5 alarms** for error rates, duration, throttles, and latency
- **Custom metrics** for processing time and document uploads
- **Optional SNS notifications** for alarm alerts

This monitoring foundation ensures you can quickly identify and resolve issues, maintain system health, and provide a reliable service to users.

---

**Task:** 11.3 Configure CloudWatch monitoring  
**Status:** Complete ✓  
**Last Updated:** January 2025
