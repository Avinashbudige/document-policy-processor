#!/bin/bash

# CloudWatch Monitoring Verification Script
# Verifies that all monitoring components are properly configured

set -e

REGION="${AWS_REGION:-us-east-1}"
FUNCTION_NAME="DocumentPolicyProcessor"
API_NAME="document-policy-processor"
DASHBOARD_NAME="DocumentPolicyProcessor-Dashboard"

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo "=========================================="
echo "CloudWatch Monitoring Verification"
echo "=========================================="
echo ""

PASS_COUNT=0
FAIL_COUNT=0

# Function to check and report
check_component() {
    local name=$1
    local command=$2
    
    if eval "$command" > /dev/null 2>&1; then
        echo -e "${GREEN}✓${NC} $name"
        ((PASS_COUNT++))
        return 0
    else
        echo -e "${RED}✗${NC} $name"
        ((FAIL_COUNT++))
        return 1
    fi
}

# Check 1: Lambda Log Group
echo "Checking Log Groups..."
check_component "Lambda log group exists" \
    "aws logs describe-log-groups --log-group-name-prefix '/aws/lambda/$FUNCTION_NAME' --region $REGION | grep -q '$FUNCTION_NAME'"

# Check 2: Dashboard
echo ""
echo "Checking Dashboard..."
check_component "Dashboard exists" \
    "aws cloudwatch get-dashboard --dashboard-name '$DASHBOARD_NAME' --region $REGION"

# Check 3: Alarms
echo ""
echo "Checking Alarms..."
check_component "High Error Rate alarm" \
    "aws cloudwatch describe-alarms --alarm-names '${FUNCTION_NAME}-HighErrorRate' --region $REGION | grep -q 'HighErrorRate'"

check_component "High Duration alarm" \
    "aws cloudwatch describe-alarms --alarm-names '${FUNCTION_NAME}-HighDuration' --region $REGION | grep -q 'HighDuration'"

check_component "Throttles alarm" \
    "aws cloudwatch describe-alarms --alarm-names '${FUNCTION_NAME}-Throttles' --region $REGION | grep -q 'Throttles'"

check_component "API 5XX Errors alarm" \
    "aws cloudwatch describe-alarms --alarm-names '${API_NAME}-High5XXErrors' --region $REGION | grep -q 'High5XXErrors'"

check_component "API High Latency alarm" \
    "aws cloudwatch describe-alarms --alarm-names '${API_NAME}-HighLatency' --region $REGION | grep -q 'HighLatency'"

# Check 4: Metric Filters
echo ""
echo "Checking Metric Filters..."
check_component "ProcessingTime metric filter" \
    "aws logs describe-metric-filters --log-group-name '/aws/lambda/$FUNCTION_NAME' --region $REGION | grep -q 'ProcessingTime'"

check_component "DocumentUploads metric filter" \
    "aws logs describe-metric-filters --log-group-name '/aws/lambda/$FUNCTION_NAME' --region $REGION | grep -q 'DocumentUploads'"

# Check 5: Log Retention
echo ""
echo "Checking Log Retention..."
RETENTION=$(aws logs describe-log-groups \
    --log-group-name-prefix "/aws/lambda/$FUNCTION_NAME" \
    --region $REGION \
    --query 'logGroups[0].retentionInDays' \
    --output text 2>/dev/null || echo "None")

if [ "$RETENTION" = "7" ]; then
    echo -e "${GREEN}✓${NC} Log retention set to 7 days"
    ((PASS_COUNT++))
elif [ "$RETENTION" = "None" ]; then
    echo -e "${YELLOW}⚠${NC} Log retention not set (logs never expire)"
else
    echo -e "${YELLOW}⚠${NC} Log retention set to $RETENTION days (expected 7)"
fi

# Check 6: Recent Logs
echo ""
echo "Checking Recent Logs..."
RECENT_LOGS=$(aws logs filter-log-events \
    --log-group-name "/aws/lambda/$FUNCTION_NAME" \
    --start-time $(($(date +%s) - 3600))000 \
    --region $REGION \
    --max-items 1 \
    --query 'events[0]' 2>/dev/null || echo "null")

if [ "$RECENT_LOGS" != "null" ] && [ -n "$RECENT_LOGS" ]; then
    echo -e "${GREEN}✓${NC} Recent logs found (Lambda has been invoked)"
    ((PASS_COUNT++))
else
    echo -e "${YELLOW}⚠${NC} No recent logs (Lambda may not have been invoked yet)"
fi

# Check 7: Alarm States
echo ""
echo "Checking Alarm States..."
ALARM_STATES=$(aws cloudwatch describe-alarms \
    --alarm-name-prefix "$FUNCTION_NAME" \
    --region $REGION \
    --query 'MetricAlarms[*].[AlarmName,StateValue]' \
    --output text)

if [ -n "$ALARM_STATES" ]; then
    echo "$ALARM_STATES" | while read -r alarm_name state; do
        if [ "$state" = "OK" ]; then
            echo -e "  ${GREEN}✓${NC} $alarm_name: $state"
        elif [ "$state" = "INSUFFICIENT_DATA" ]; then
            echo -e "  ${YELLOW}⚠${NC} $alarm_name: $state (waiting for data)"
        else
            echo -e "  ${RED}✗${NC} $alarm_name: $state"
        fi
    done
fi

# Summary
echo ""
echo "=========================================="
echo "Verification Summary"
echo "=========================================="
echo ""
echo -e "Passed: ${GREEN}$PASS_COUNT${NC}"
echo -e "Failed: ${RED}$FAIL_COUNT${NC}"
echo ""

if [ $FAIL_COUNT -eq 0 ]; then
    echo -e "${GREEN}✓ All checks passed!${NC}"
    echo ""
    echo "Monitoring is properly configured."
    echo ""
    echo "View Dashboard:"
    echo "  https://console.aws.amazon.com/cloudwatch/home?region=${REGION}#dashboards:name=${DASHBOARD_NAME}"
    echo ""
    echo "View Logs:"
    echo "  aws logs tail /aws/lambda/$FUNCTION_NAME --follow"
    echo ""
    echo "Next Steps:"
    echo "  1. Invoke Lambda to generate metrics"
    echo "  2. Check dashboard for data"
    echo "  3. Proceed to Task 12: End-to-end integration testing"
    echo ""
    exit 0
else
    echo -e "${RED}✗ Some checks failed${NC}"
    echo ""
    echo "Please run the setup script to configure monitoring:"
    echo "  ./setup-cloudwatch-monitoring.sh"
    echo ""
    exit 1
fi
