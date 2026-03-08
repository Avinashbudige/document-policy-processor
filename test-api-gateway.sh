#!/bin/bash

# Test script for API Gateway endpoints
# This script tests all API Gateway endpoints after deployment

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configuration
API_BASE_URL=""
API_KEY=""
TEST_JOB_ID="test-$(date +%s)"

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --api-url)
            API_BASE_URL="$2"
            shift 2
            ;;
        --api-key)
            API_KEY="$2"
            shift 2
            ;;
        *)
            echo "Unknown option: $1"
            echo "Usage: $0 --api-url <url> --api-key <key>"
            exit 1
            ;;
    esac
done

# Validate inputs
if [ -z "$API_BASE_URL" ]; then
    echo -e "${RED}Error: API base URL is required${NC}"
    echo "Usage: $0 --api-url <url> --api-key <key>"
    exit 1
fi

if [ -z "$API_KEY" ]; then
    echo -e "${YELLOW}Warning: No API key provided. Some tests will fail.${NC}"
fi

echo "=========================================="
echo "API Gateway Endpoint Tests"
echo "=========================================="
echo "API Base URL: $API_BASE_URL"
echo "Test Job ID: $TEST_JOB_ID"
echo ""

# Test 1: Health Check
echo -e "${YELLOW}Test 1: Health Check (GET /api/health)${NC}"
RESPONSE=$(curl -s -w "\n%{http_code}" "$API_BASE_URL/api/health")
HTTP_CODE=$(echo "$RESPONSE" | tail -n1)
BODY=$(echo "$RESPONSE" | head -n-1)

if [ "$HTTP_CODE" -eq 200 ]; then
    echo -e "${GREEN}✓ Health check passed${NC}"
    echo "Response: $BODY"
else
    echo -e "${RED}✗ Health check failed (HTTP $HTTP_CODE)${NC}"
    echo "Response: $BODY"
fi
echo ""

# Test 2: Get Status (should return 404 for non-existent job)
echo -e "${YELLOW}Test 2: Get Status for non-existent job (GET /api/status/{jobId})${NC}"
if [ -n "$API_KEY" ]; then
    RESPONSE=$(curl -s -w "\n%{http_code}" \
        -H "X-Api-Key: $API_KEY" \
        "$API_BASE_URL/api/status/non-existent-job")
    HTTP_CODE=$(echo "$RESPONSE" | tail -n1)
    BODY=$(echo "$RESPONSE" | head -n-1)
    
    if [ "$HTTP_CODE" -eq 404 ]; then
        echo -e "${GREEN}✓ Correctly returned 404 for non-existent job${NC}"
        echo "Response: $BODY"
    else
        echo -e "${RED}✗ Expected 404, got HTTP $HTTP_CODE${NC}"
        echo "Response: $BODY"
    fi
else
    echo -e "${YELLOW}⊘ Skipped (no API key)${NC}"
fi
echo ""

# Test 3: Get Results (should return 404 for non-existent job)
echo -e "${YELLOW}Test 3: Get Results for non-existent job (GET /api/results/{jobId})${NC}"
if [ -n "$API_KEY" ]; then
    RESPONSE=$(curl -s -w "\n%{http_code}" \
        -H "X-Api-Key: $API_KEY" \
        "$API_BASE_URL/api/results/non-existent-job")
    HTTP_CODE=$(echo "$RESPONSE" | tail -n1)
    BODY=$(echo "$RESPONSE" | head -n-1)
    
    if [ "$HTTP_CODE" -eq 404 ]; then
        echo -e "${GREEN}✓ Correctly returned 404 for non-existent job${NC}"
        echo "Response: $BODY"
    else
        echo -e "${RED}✗ Expected 404, got HTTP $HTTP_CODE${NC}"
        echo "Response: $BODY"
    fi
else
    echo -e "${YELLOW}⊘ Skipped (no API key)${NC}"
fi
echo ""

# Test 4: Process Document (validation error - missing fields)
echo -e "${YELLOW}Test 4: Process Document with missing fields (POST /api/process-document)${NC}"
if [ -n "$API_KEY" ]; then
    RESPONSE=$(curl -s -w "\n%{http_code}" \
        -X POST \
        -H "X-Api-Key: $API_KEY" \
        -H "Content-Type: application/json" \
        -d '{}' \
        "$API_BASE_URL/api/process-document")
    HTTP_CODE=$(echo "$RESPONSE" | tail -n1)
    BODY=$(echo "$RESPONSE" | head -n-1)
    
    if [ "$HTTP_CODE" -eq 400 ]; then
        echo -e "${GREEN}✓ Correctly returned 400 for missing fields${NC}"
        echo "Response: $BODY"
    else
        echo -e "${RED}✗ Expected 400, got HTTP $HTTP_CODE${NC}"
        echo "Response: $BODY"
    fi
else
    echo -e "${YELLOW}⊘ Skipped (no API key)${NC}"
fi
echo ""

# Test 5: Process Document (validation error - invalid S3 URL)
echo -e "${YELLOW}Test 5: Process Document with invalid S3 URL (POST /api/process-document)${NC}"
if [ -n "$API_KEY" ]; then
    RESPONSE=$(curl -s -w "\n%{http_code}" \
        -X POST \
        -H "X-Api-Key: $API_KEY" \
        -H "Content-Type: application/json" \
        -d "{
            \"job_id\": \"$TEST_JOB_ID\",
            \"document_url\": \"invalid-url\",
            \"symptoms\": \"Test symptoms\"
        }" \
        "$API_BASE_URL/api/process-document")
    HTTP_CODE=$(echo "$RESPONSE" | tail -n1)
    BODY=$(echo "$RESPONSE" | head -n-1)
    
    if [ "$HTTP_CODE" -eq 400 ]; then
        echo -e "${GREEN}✓ Correctly returned 400 for invalid S3 URL${NC}"
        echo "Response: $BODY"
    else
        echo -e "${RED}✗ Expected 400, got HTTP $HTTP_CODE${NC}"
        echo "Response: $BODY"
    fi
else
    echo -e "${YELLOW}⊘ Skipped (no API key)${NC}"
fi
echo ""

# Test 6: CORS Headers
echo -e "${YELLOW}Test 6: CORS Headers${NC}"
RESPONSE=$(curl -s -I "$API_BASE_URL/api/health")
if echo "$RESPONSE" | grep -qi "access-control-allow-origin"; then
    echo -e "${GREEN}✓ CORS headers present${NC}"
    echo "$RESPONSE" | grep -i "access-control"
else
    echo -e "${RED}✗ CORS headers missing${NC}"
fi
echo ""

# Test 7: API Key Authentication
echo -e "${YELLOW}Test 7: API Key Authentication (should fail without key)${NC}"
RESPONSE=$(curl -s -w "\n%{http_code}" \
    -X POST \
    -H "Content-Type: application/json" \
    -d "{
        \"job_id\": \"$TEST_JOB_ID\",
        \"document_url\": \"s3://bucket/key\",
        \"symptoms\": \"Test\"
    }" \
    "$API_BASE_URL/api/process-document")
HTTP_CODE=$(echo "$RESPONSE" | tail -n1)
BODY=$(echo "$RESPONSE" | head -n-1)

if [ "$HTTP_CODE" -eq 403 ]; then
    echo -e "${GREEN}✓ Correctly returned 403 without API key${NC}"
    echo "Response: $BODY"
else
    echo -e "${RED}✗ Expected 403, got HTTP $HTTP_CODE${NC}"
    echo "Response: $BODY"
fi
echo ""

# Summary
echo "=========================================="
echo "Test Summary"
echo "=========================================="
echo "All basic endpoint tests completed."
echo ""
echo "Next steps:"
echo "1. Upload a test document to S3"
echo "2. Test the full document processing flow"
echo "3. Monitor CloudWatch logs for any errors"
echo ""
