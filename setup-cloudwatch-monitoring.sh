#!/bin/bash

# CloudWatch Monitoring Setup Script
# Task 11.3: Configure CloudWatch monitoring
# Sets up log groups, dashboards, and alarms for the Document Policy Processor

set -e

echo "=========================================="
echo "CloudWatch Monitoring Setup"
echo "=========================================="
echo ""

# Configuration
FUNCTION_NAME="DocumentPolicyProcessor"
API_NAME="document-policy-processor"
REGION="${AWS_REGION:-us-east-1}"
ALARM_EMAIL="${ALARM_EMAIL:-}"

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Step 1: Ensure log groups exist
echo "Step 1: Verifying log groups..."
echo ""

LAMBDA_LOG_GROUP="/aws/lambda/${FUNCTION_NAME}"
API_LOG_GROUP="/aws/apigateway/${API_NAME}/Prod"

# Check Lambda log group
if aws logs describe-log-groups --log-group-name-prefix "$LAMBDA_LOG_GROUP" --region "$REGION" | grep -q "$LAMBDA_LOG_GROUP"; then
    echo -e "${GREEN}✓${NC} Lambda log group exists: $LAMBDA_LOG_GROUP"
else
    echo -e "${YELLOW}Creating Lambda log group...${NC}"
    aws logs create-log-group --log-group-name "$LAMBDA_LOG_GROUP" --region "$REGION"
    echo -e "${GREEN}✓${NC} Lambda log group created"
fi

# Set retention policy (7 days for cost optimization)
echo "Setting log retention to 7 days..."
aws logs put-retention-policy \
    --log-group-name "$LAMBDA_LOG_GROUP" \
    --retention-in-days 7 \
    --region "$REGION" 2>/dev/null || true

echo ""

# Step 2: Create CloudWatch Dashboard
echo "Step 2: Creating CloudWatch Dashboard..."
echo ""

DASHBOARD_NAME="DocumentPolicyProcessor-Dashboard"

# Create dashboard JSON
cat > /tmp/dashboard.json <<'EOF'
{
    "widgets": [
        {
            "type": "metric",
            "properties": {
                "metrics": [
                    ["AWS/Lambda", "Invocations", {"stat": "Sum", "label": "Total Invocations"}],
                    [".", "Errors", {"stat": "Sum", "label": "Errors"}],
                    [".", "Throttles", {"stat": "Sum", "label": "Throttles"}]
                ],
                "view": "timeSeries",
                "stacked": false,
                "region": "REGION_PLACEHOLDER",
                "title": "Lambda Invocations & Errors",
                "period": 300,
                "yAxis": {
                    "left": {
                        "min": 0
                    }
                }
            },
            "width": 12,
            "height": 6,
            "x": 0,
            "y": 0
        },
        {
            "type": "metric",
            "properties": {
                "metrics": [
                    ["AWS/Lambda", "Duration", {"stat": "Average", "label": "Avg Duration"}],
                    ["...", {"stat": "Maximum", "label": "Max Duration"}],
                    ["...", {"stat": "Minimum", "label": "Min Duration"}]
                ],
                "view": "timeSeries",
                "stacked": false,
                "region": "REGION_PLACEHOLDER",
                "title": "Lambda Duration (ms)",
                "period": 300,
                "yAxis": {
                    "left": {
                        "min": 0
                    }
                }
            },
            "width": 12,
            "height": 6,
            "x": 12,
            "y": 0
        },
        {
            "type": "metric",
            "properties": {
                "metrics": [
                    ["AWS/Lambda", "ConcurrentExecutions", {"stat": "Maximum", "label": "Concurrent Executions"}]
                ],
                "view": "timeSeries",
                "stacked": false,
                "region": "REGION_PLACEHOLDER",
                "title": "Lambda Concurrent Executions",
                "period": 300,
                "yAxis": {
                    "left": {
                        "min": 0
                    }
                }
            },
            "width": 12,
            "height": 6,
            "x": 0,
            "y": 6
        },
        {
            "type": "metric",
            "properties": {
                "metrics": [
                    ["AWS/ApiGateway", "Count", {"stat": "Sum", "label": "API Requests"}],
                    [".", "4XXError", {"stat": "Sum", "label": "4XX Errors"}],
                    [".", "5XXError", {"stat": "Sum", "label": "5XX Errors"}]
                ],
                "view": "timeSeries",
                "stacked": false,
                "region": "REGION_PLACEHOLDER",
                "title": "API Gateway Requests & Errors",
                "period": 300,
                "yAxis": {
                    "left": {
                        "min": 0
                    }
                }
            },
            "width": 12,
            "height": 6,
            "x": 12,
            "y": 6
        },
        {
            "type": "metric",
            "properties": {
                "metrics": [
                    ["AWS/ApiGateway", "Latency", {"stat": "Average", "label": "Avg Latency"}],
                    ["...", {"stat": "p99", "label": "P99 Latency"}]
                ],
                "view": "timeSeries",
                "stacked": false,
                "region": "REGION_PLACEHOLDER",
                "title": "API Gateway Latency (ms)",
                "period": 300,
                "yAxis": {
                    "left": {
                        "min": 0
                    }
                }
            },
            "width": 12,
            "height": 6,
            "x": 0,
            "y": 12
        },
        {
            "type": "log",
            "properties": {
                "query": "SOURCE '/aws/lambda/FUNCTION_NAME_PLACEHOLDER'\n| fields @timestamp, @message\n| filter @message like /ERROR/\n| sort @timestamp desc\n| limit 20",
                "region": "REGION_PLACEHOLDER",
                "title": "Recent Lambda Errors",
                "stacked": false
            },
            "width": 12,
            "height": 6,
            "x": 12,
            "y": 12
        }
    ]
}
EOF

# Replace placeholders
sed -i.bak "s/REGION_PLACEHOLDER/$REGION/g" /tmp/dashboard.json
sed -i.bak "s/FUNCTION_NAME_PLACEHOLDER/$FUNCTION_NAME/g" /tmp/dashboard.json
rm /tmp/dashboard.json.bak

# Create or update dashboard
aws cloudwatch put-dashboard \
    --dashboard-name "$DASHBOARD_NAME" \
    --dashboard-body file:///tmp/dashboard.json \
    --region "$REGION"

echo -e "${GREEN}✓${NC} Dashboard created: $DASHBOARD_NAME"
echo ""

# Step 3: Create CloudWatch Alarms
echo "Step 3: Creating CloudWatch Alarms..."
echo ""

# Alarm 1: Lambda Error Rate
echo "Creating Lambda error rate alarm..."
aws cloudwatch put-metric-alarm \
    --alarm-name "${FUNCTION_NAME}-HighErrorRate" \
    --alarm-description "Alert when Lambda error rate exceeds 10%" \
    --metric-name Errors \
    --namespace AWS/Lambda \
    --statistic Sum \
    --period 300 \
    --evaluation-periods 1 \
    --threshold 5 \
    --comparison-operator GreaterThanThreshold \
    --dimensions Name=FunctionName,Value="$FUNCTION_NAME" \
    --treat-missing-data notBreaching \
    --region "$REGION"

echo -e "${GREEN}✓${NC} Lambda error rate alarm created"

# Alarm 2: Lambda Duration (Timeout Warning)
echo "Creating Lambda duration alarm..."
aws cloudwatch put-metric-alarm \
    --alarm-name "${FUNCTION_NAME}-HighDuration" \
    --alarm-description "Alert when Lambda duration exceeds 240 seconds (80% of timeout)" \
    --metric-name Duration \
    --namespace AWS/Lambda \
    --statistic Average \
    --period 300 \
    --evaluation-periods 1 \
    --threshold 240000 \
    --comparison-operator GreaterThanThreshold \
    --dimensions Name=FunctionName,Value="$FUNCTION_NAME" \
    --treat-missing-data notBreaching \
    --region "$REGION"

echo -e "${GREEN}✓${NC} Lambda duration alarm created"

# Alarm 3: Lambda Throttles
echo "Creating Lambda throttle alarm..."
aws cloudwatch put-metric-alarm \
    --alarm-name "${FUNCTION_NAME}-Throttles" \
    --alarm-description "Alert when Lambda function is throttled" \
    --metric-name Throttles \
    --namespace AWS/Lambda \
    --statistic Sum \
    --period 300 \
    --evaluation-periods 1 \
    --threshold 1 \
    --comparison-operator GreaterThanThreshold \
    --dimensions Name=FunctionName,Value="$FUNCTION_NAME" \
    --treat-missing-data notBreaching \
    --region "$REGION"

echo -e "${GREEN}✓${NC} Lambda throttle alarm created"

# Alarm 4: API Gateway 5XX Errors
echo "Creating API Gateway 5XX error alarm..."
aws cloudwatch put-metric-alarm \
    --alarm-name "${API_NAME}-High5XXErrors" \
    --alarm-description "Alert when API Gateway 5XX error rate is high" \
    --metric-name 5XXError \
    --namespace AWS/ApiGateway \
    --statistic Sum \
    --period 300 \
    --evaluation-periods 1 \
    --threshold 5 \
    --comparison-operator GreaterThanThreshold \
    --dimensions Name=ApiName,Value="$API_NAME" \
    --treat-missing-data notBreaching \
    --region "$REGION"

echo -e "${GREEN}✓${NC} API Gateway 5XX error alarm created"

# Alarm 5: API Gateway High Latency
echo "Creating API Gateway latency alarm..."
aws cloudwatch put-metric-alarm \
    --alarm-name "${API_NAME}-HighLatency" \
    --alarm-description "Alert when API Gateway latency exceeds 10 seconds" \
    --metric-name Latency \
    --namespace AWS/ApiGateway \
    --statistic Average \
    --period 300 \
    --evaluation-periods 2 \
    --threshold 10000 \
    --comparison-operator GreaterThanThreshold \
    --dimensions Name=ApiName,Value="$API_NAME" \
    --treat-missing-data notBreaching \
    --region "$REGION"

echo -e "${GREEN}✓${NC} API Gateway latency alarm created"

echo ""

# Step 4: Configure SNS for alarm notifications (optional)
if [ -n "$ALARM_EMAIL" ]; then
    echo "Step 4: Configuring SNS for alarm notifications..."
    echo ""
    
    SNS_TOPIC_NAME="${FUNCTION_NAME}-Alarms"
    
    # Create SNS topic
    SNS_TOPIC_ARN=$(aws sns create-topic \
        --name "$SNS_TOPIC_NAME" \
        --region "$REGION" \
        --query 'TopicArn' \
        --output text)
    
    echo -e "${GREEN}✓${NC} SNS topic created: $SNS_TOPIC_ARN"
    
    # Subscribe email to topic
    aws sns subscribe \
        --topic-arn "$SNS_TOPIC_ARN" \
        --protocol email \
        --notification-endpoint "$ALARM_EMAIL" \
        --region "$REGION"
    
    echo -e "${YELLOW}⚠${NC}  Email subscription pending confirmation"
    echo "   Check $ALARM_EMAIL for confirmation email"
    echo ""
    
    # Update alarms to send to SNS
    echo "Updating alarms to send notifications..."
    
    for ALARM_NAME in \
        "${FUNCTION_NAME}-HighErrorRate" \
        "${FUNCTION_NAME}-HighDuration" \
        "${FUNCTION_NAME}-Throttles" \
        "${API_NAME}-High5XXErrors" \
        "${API_NAME}-HighLatency"
    do
        aws cloudwatch put-metric-alarm \
            --alarm-name "$ALARM_NAME" \
            --alarm-actions "$SNS_TOPIC_ARN" \
            --region "$REGION" 2>/dev/null || true
    done
    
    echo -e "${GREEN}✓${NC} Alarms configured to send notifications"
    echo ""
else
    echo "Step 4: Skipping SNS configuration (no email provided)"
    echo "   To enable email notifications, run:"
    echo "   ALARM_EMAIL=your@email.com ./setup-cloudwatch-monitoring.sh"
    echo ""
fi

# Step 5: Create metric filters for custom metrics
echo "Step 5: Creating metric filters..."
echo ""

# Metric filter for processing time
aws logs put-metric-filter \
    --log-group-name "$LAMBDA_LOG_GROUP" \
    --filter-name "ProcessingTime" \
    --filter-pattern '[timestamp, request_id, level, msg="Processing completed*", processing_time]' \
    --metric-transformations \
        metricName=ProcessingTime,\
metricNamespace=DocumentPolicyProcessor,\
metricValue='$processing_time',\
unit=Seconds \
    --region "$REGION" 2>/dev/null || true

echo -e "${GREEN}✓${NC} Processing time metric filter created"

# Metric filter for document types
aws logs put-metric-filter \
    --log-group-name "$LAMBDA_LOG_GROUP" \
    --filter-name "DocumentUploads" \
    --filter-pattern '[timestamp, request_id, level, msg="Document uploaded*"]' \
    --metric-transformations \
        metricName=DocumentUploads,\
metricNamespace=DocumentPolicyProcessor,\
metricValue=1,\
unit=Count \
    --region "$REGION" 2>/dev/null || true

echo -e "${GREEN}✓${NC} Document upload metric filter created"

echo ""

# Summary
echo "=========================================="
echo "CloudWatch Monitoring Setup Complete!"
echo "=========================================="
echo ""
echo "Resources Created:"
echo "  • Log Groups: $LAMBDA_LOG_GROUP"
echo "  • Dashboard: $DASHBOARD_NAME"
echo "  • Alarms: 5 alarms created"
echo ""
echo "View Dashboard:"
echo "  https://console.aws.amazon.com/cloudwatch/home?region=${REGION}#dashboards:name=${DASHBOARD_NAME}"
echo ""
echo "View Alarms:"
echo "  https://console.aws.amazon.com/cloudwatch/home?region=${REGION}#alarmsV2:"
echo ""
echo "View Logs:"
echo "  Lambda: aws logs tail $LAMBDA_LOG_GROUP --follow"
echo ""
echo "Next Steps:"
echo "  1. View the dashboard to monitor system health"
echo "  2. Test alarms by triggering errors"
echo "  3. Confirm SNS email subscription (if configured)"
echo "  4. Proceed to Task 12: End-to-end integration testing"
echo ""
