#!/bin/bash

# Test Frontend Deployment
# This script tests if the deployed frontend is working correctly

set -e

echo "🧪 Frontend Deployment Test"
echo "==========================="
echo ""

# Prompt for frontend URL
read -p "Enter your frontend URL (e.g., https://your-app.streamlit.app): " frontend_url
if [ -z "$frontend_url" ]; then
    echo "❌ Error: Frontend URL is required"
    exit 1
fi

# Remove trailing slash
frontend_url=${frontend_url%/}

echo ""
echo "Testing: $frontend_url"
echo ""

# Test 1: Basic connectivity
echo "Test 1: Basic Connectivity"
echo "=========================="
http_code=$(curl -s -o /dev/null -w "%{http_code}" "$frontend_url" || echo "000")

if [ "$http_code" = "200" ]; then
    echo "✅ PASS: Frontend is accessible (HTTP $http_code)"
else
    echo "❌ FAIL: Frontend returned HTTP $http_code"
    exit 1
fi

# Test 2: Check if page loads
echo ""
echo "Test 2: Page Content"
echo "===================="
content=$(curl -s "$frontend_url")

if echo "$content" | grep -q "Document Policy Processor"; then
    echo "✅ PASS: Page contains expected title"
else
    echo "❌ FAIL: Page title not found"
    echo "This might be a Streamlit app (content loaded via JavaScript)"
    echo "Manual verification required"
fi

# Test 3: Check for common errors
echo ""
echo "Test 3: Error Detection"
echo "======================"
errors_found=0

if echo "$content" | grep -qi "error"; then
    echo "⚠️  WARNING: Found 'error' in page content"
    errors_found=$((errors_found + 1))
fi

if echo "$content" | grep -qi "404"; then
    echo "⚠️  WARNING: Found '404' in page content"
    errors_found=$((errors_found + 1))
fi

if echo "$content" | grep -qi "500"; then
    echo "⚠️  WARNING: Found '500' in page content"
    errors_found=$((errors_found + 1))
fi

if [ $errors_found -eq 0 ]; then
    echo "✅ PASS: No obvious errors detected"
else
    echo "⚠️  Found $errors_found potential issues"
fi

# Test 4: SSL/HTTPS check
echo ""
echo "Test 4: SSL/HTTPS"
echo "================="
if [[ "$frontend_url" == https://* ]]; then
    echo "✅ PASS: Using HTTPS"
    
    # Check SSL certificate
    if command -v openssl &> /dev/null; then
        domain=$(echo "$frontend_url" | sed -e 's|^https://||' -e 's|/.*||')
        if echo | openssl s_client -servername "$domain" -connect "$domain:443" 2>/dev/null | grep -q "Verify return code: 0"; then
            echo "✅ PASS: Valid SSL certificate"
        else
            echo "⚠️  WARNING: SSL certificate validation failed"
        fi
    fi
else
    echo "⚠️  WARNING: Not using HTTPS (HTTP only)"
fi

# Test 5: Response time
echo ""
echo "Test 5: Response Time"
echo "===================="
response_time=$(curl -s -o /dev/null -w "%{time_total}" "$frontend_url")
response_time_ms=$(echo "$response_time * 1000" | bc)

echo "Response time: ${response_time_ms} ms"

if (( $(echo "$response_time < 3" | bc -l) )); then
    echo "✅ PASS: Good response time (< 3s)"
elif (( $(echo "$response_time < 10" | bc -l) )); then
    echo "⚠️  WARNING: Slow response time (3-10s)"
else
    echo "❌ FAIL: Very slow response time (> 10s)"
fi

# Test 6: Mobile responsiveness (basic check)
echo ""
echo "Test 6: Mobile Responsiveness"
echo "============================="
mobile_content=$(curl -s -A "Mozilla/5.0 (iPhone; CPU iPhone OS 14_0 like Mac OS X)" "$frontend_url")

if [ ${#mobile_content} -gt 1000 ]; then
    echo "✅ PASS: Page loads on mobile user agent"
else
    echo "⚠️  WARNING: Mobile content seems incomplete"
fi

# Test 7: Check for API configuration
echo ""
echo "Test 7: API Configuration"
echo "========================"
if echo "$content" | grep -q "your-api-gateway-url"; then
    echo "❌ FAIL: API URL not configured (still has placeholder)"
    echo "Update the API_BASE_URL in your configuration"
elif echo "$content" | grep -q "amazonaws.com"; then
    echo "✅ PASS: API URL appears to be configured"
else
    echo "⚠️  WARNING: Cannot verify API configuration"
    echo "This is normal for Streamlit apps (config in secrets)"
fi

# Summary
echo ""
echo "================================"
echo "Test Summary"
echo "================================"
echo ""
echo "Frontend URL: $frontend_url"
echo "HTTP Status: $http_code"
echo "Response Time: ${response_time_ms} ms"
echo "HTTPS: $(if [[ "$frontend_url" == https://* ]]; then echo "Yes"; else echo "No"; fi)"
echo ""
echo "📋 Manual Tests Required:"
echo "========================"
echo "1. Open $frontend_url in a browser"
echo "2. Upload a test document (PDF, PNG, JPG, or TXT)"
echo "3. Enter test symptoms"
echo "4. Click 'Process Document'"
echo "5. Verify results are displayed"
echo "6. Check browser console for errors (F12)"
echo "7. Test on mobile device"
echo ""
echo "✅ Automated tests complete!"
echo ""

# Exit with success if basic connectivity works
if [ "$http_code" = "200" ]; then
    exit 0
else
    exit 1
fi
