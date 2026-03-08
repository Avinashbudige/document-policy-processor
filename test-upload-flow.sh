#!/bin/bash

# Test script for document upload flow
# This script tests the complete upload and processing workflow

set -e

# Configuration
API_BASE_URL="${API_BASE_URL:-https://your-api-id.execute-api.us-east-1.amazonaws.com/Prod}"
API_KEY="${API_KEY:-your-api-key-here}"
TEST_FILE="${TEST_FILE:-test-document.pdf}"
SYMPTOMS="${SYMPTOMS:-Fever and cough for 3 days}"

echo "=========================================="
echo "Document Upload Flow Test"
echo "=========================================="
echo ""
echo "API Base URL: $API_BASE_URL"
echo "Test File: $TEST_FILE"
echo "Symptoms: $SYMPTOMS"
echo ""

# Check if test file exists
if [ ! -f "$TEST_FILE" ]; then
    echo "Error: Test file '$TEST_FILE' not found"
    echo "Please create a test file or set TEST_FILE environment variable"
    exit 1
fi

# Get file type
FILE_EXT="${TEST_FILE##*.}"
case "$FILE_EXT" in
    pdf)
        FILE_TYPE="application/pdf"
        ;;
    png)
        FILE_TYPE="image/png"
        ;;
    jpg|jpeg)
        FILE_TYPE="image/jpeg"
        ;;
    txt)
        FILE_TYPE="text/plain"
        ;;
    *)
        echo "Error: Unsupported file type: $FILE_EXT"
        exit 1
        ;;
esac

echo "Step 1: Requesting upload URL..."
echo "----------------------------------------"

UPLOAD_RESPONSE=$(curl -s -X POST "$API_BASE_URL/api/upload-url" \
    -H "X-Api-Key: $API_KEY" \
    -H "Content-Type: application/json" \
    -d "{
        \"filename\": \"$TEST_FILE\",
        \"file_type\": \"$FILE_TYPE\"
    }")

echo "Response: $UPLOAD_RESPONSE"
echo ""

# Extract values from response
UPLOAD_URL=$(echo "$UPLOAD_RESPONSE" | grep -o '"upload_url":"[^"]*"' | cut -d'"' -f4)
DOCUMENT_URL=$(echo "$UPLOAD_RESPONSE" | grep -o '"document_url":"[^"]*"' | cut -d'"' -f4)
JOB_ID=$(echo "$UPLOAD_RESPONSE" | grep -o '"job_id":"[^"]*"' | cut -d'"' -f4)

if [ -z "$UPLOAD_URL" ] || [ -z "$DOCUMENT_URL" ] || [ -z "$JOB_ID" ]; then
    echo "Error: Failed to get upload URL"
    echo "Response: $UPLOAD_RESPONSE"
    exit 1
fi

echo "Upload URL: $UPLOAD_URL"
echo "Document URL: $DOCUMENT_URL"
echo "Job ID: $JOB_ID"
echo ""

echo "Step 2: Uploading file to S3..."
echo "----------------------------------------"

UPLOAD_STATUS=$(curl -s -o /dev/null -w "%{http_code}" -X PUT "$UPLOAD_URL" \
    -H "Content-Type: $FILE_TYPE" \
    --data-binary "@$TEST_FILE")

if [ "$UPLOAD_STATUS" != "200" ]; then
    echo "Error: File upload failed with status $UPLOAD_STATUS"
    exit 1
fi

echo "File uploaded successfully (HTTP $UPLOAD_STATUS)"
echo ""

echo "Step 3: Triggering document processing..."
echo "----------------------------------------"

PROCESS_RESPONSE=$(curl -s -X POST "$API_BASE_URL/api/process-document" \
    -H "X-Api-Key: $API_KEY" \
    -H "Content-Type: application/json" \
    -d "{
        \"job_id\": \"$JOB_ID\",
        \"document_url\": \"$DOCUMENT_URL\",
        \"symptoms\": \"$SYMPTOMS\"
    }")

echo "Response: $PROCESS_RESPONSE"
echo ""

# Check if processing was successful
STATUS=$(echo "$PROCESS_RESPONSE" | grep -o '"status":"[^"]*"' | cut -d'"' -f4)

if [ "$STATUS" = "completed" ]; then
    echo "✓ Processing completed successfully!"
    echo ""
    echo "Recommendations:"
    echo "$PROCESS_RESPONSE" | grep -o '"recommendations":\[.*\]' | head -1
elif [ "$STATUS" = "failed" ]; then
    echo "✗ Processing failed"
    ERROR_MSG=$(echo "$PROCESS_RESPONSE" | grep -o '"error_message":"[^"]*"' | cut -d'"' -f4)
    echo "Error: $ERROR_MSG"
    exit 1
else
    echo "Processing status: $STATUS"
    echo ""
    echo "Step 4: Checking job status..."
    echo "----------------------------------------"
    
    sleep 2
    
    STATUS_RESPONSE=$(curl -s "$API_BASE_URL/api/status/$JOB_ID" \
        -H "X-Api-Key: $API_KEY")
    
    echo "Status: $STATUS_RESPONSE"
    echo ""
    
    echo "Step 5: Getting results..."
    echo "----------------------------------------"
    
    RESULTS_RESPONSE=$(curl -s "$API_BASE_URL/api/results/$JOB_ID" \
        -H "X-Api-Key: $API_KEY")
    
    echo "Results: $RESULTS_RESPONSE"
fi

echo ""
echo "=========================================="
echo "Test completed!"
echo "=========================================="
