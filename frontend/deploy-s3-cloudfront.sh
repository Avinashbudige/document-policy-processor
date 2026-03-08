#!/bin/bash

# Deploy Static HTML to S3 + CloudFront
# This script deploys the static HTML version to AWS S3 and CloudFront

set -e

echo "🚀 S3 + CloudFront Deployment Script"
echo "====================================="
echo ""

# Check if AWS CLI is installed
if ! command -v aws &> /dev/null; then
    echo "❌ Error: AWS CLI is not installed"
    echo "Install it from: https://aws.amazon.com/cli/"
    exit 1
fi

# Check if AWS credentials are configured
if ! aws sts get-caller-identity &> /dev/null; then
    echo "❌ Error: AWS credentials not configured"
    echo "Run: aws configure"
    exit 1
fi

echo "✅ AWS CLI configured"

# Check if index.html exists
if [ ! -f "index.html" ]; then
    echo "❌ Error: index.html not found. Please run this script from the frontend/ directory."
    exit 1
fi

# Prompt for configuration
echo ""
echo "📋 Configuration"
echo "==============="
read -p "Enter a unique bucket name (e.g., doc-policy-frontend-12345): " bucket_name
if [ -z "$bucket_name" ]; then
    echo "❌ Error: Bucket name is required"
    exit 1
fi

read -p "Enter your API Gateway URL: " api_url
if [ -z "$api_url" ]; then
    echo "❌ Error: API Gateway URL is required"
    exit 1
fi

read -p "AWS Region (default: us-east-1): " aws_region
aws_region=${aws_region:-us-east-1}

read -p "Create CloudFront distribution? (y/n, default: y): " create_cloudfront
create_cloudfront=${create_cloudfront:-y}

# Update index.html with API URL
echo ""
echo "📝 Updating index.html with API URL..."
if [[ "$OSTYPE" == "darwin"* ]]; then
    # macOS
    sed -i '' "s|const API_BASE_URL = '.*';|const API_BASE_URL = '$api_url';|g" index.html
else
    # Linux
    sed -i "s|const API_BASE_URL = '.*';|const API_BASE_URL = '$api_url';|g" index.html
fi
echo "✅ API URL updated in index.html"

# Create S3 bucket
echo ""
echo "🪣 Creating S3 bucket..."
if aws s3 mb "s3://$bucket_name" --region "$aws_region" 2>/dev/null; then
    echo "✅ Bucket created: $bucket_name"
else
    echo "⚠️  Bucket already exists or creation failed"
fi

# Enable static website hosting
echo "🌐 Enabling static website hosting..."
aws s3 website "s3://$bucket_name" \
    --index-document index.html \
    --error-document index.html

# Create bucket policy for public read access
echo "🔓 Setting bucket policy for public access..."
cat > /tmp/bucket-policy.json << EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "PublicReadGetObject",
      "Effect": "Allow",
      "Principal": "*",
      "Action": "s3:GetObject",
      "Resource": "arn:aws:s3:::$bucket_name/*"
    }
  ]
}
EOF

aws s3api put-bucket-policy \
    --bucket "$bucket_name" \
    --policy file:///tmp/bucket-policy.json

rm /tmp/bucket-policy.json

# Upload files
echo "📤 Uploading files to S3..."
aws s3 cp index.html "s3://$bucket_name/" \
    --content-type "text/html" \
    --cache-control "max-age=300"

echo "✅ Files uploaded"

# Get S3 website URL
website_url="http://$bucket_name.s3-website-$aws_region.amazonaws.com"
echo ""
echo "✅ S3 Website URL: $website_url"

# Create CloudFront distribution if requested
if [ "$create_cloudfront" = "y" ]; then
    echo ""
    echo "☁️  Creating CloudFront distribution..."
    echo "This may take 10-15 minutes..."
    
    # Create CloudFront distribution config
    cat > /tmp/cf-config.json << EOF
{
  "CallerReference": "$(date +%s)",
  "Comment": "Document Policy Processor Frontend",
  "Enabled": true,
  "DefaultRootObject": "index.html",
  "Origins": {
    "Quantity": 1,
    "Items": [
      {
        "Id": "S3-$bucket_name",
        "DomainName": "$bucket_name.s3-website-$aws_region.amazonaws.com",
        "CustomOriginConfig": {
          "HTTPPort": 80,
          "HTTPSPort": 443,
          "OriginProtocolPolicy": "http-only"
        }
      }
    ]
  },
  "DefaultCacheBehavior": {
    "TargetOriginId": "S3-$bucket_name",
    "ViewerProtocolPolicy": "redirect-to-https",
    "AllowedMethods": {
      "Quantity": 2,
      "Items": ["GET", "HEAD"],
      "CachedMethods": {
        "Quantity": 2,
        "Items": ["GET", "HEAD"]
      }
    },
    "ForwardedValues": {
      "QueryString": false,
      "Cookies": {
        "Forward": "none"
      }
    },
    "MinTTL": 0,
    "DefaultTTL": 300,
    "MaxTTL": 86400,
    "Compress": true
  },
  "CustomErrorResponses": {
    "Quantity": 1,
    "Items": [
      {
        "ErrorCode": 404,
        "ResponsePagePath": "/index.html",
        "ResponseCode": "200",
        "ErrorCachingMinTTL": 300
      }
    ]
  }
}
EOF

    # Create distribution
    distribution_output=$(aws cloudfront create-distribution \
        --distribution-config file:///tmp/cf-config.json \
        --output json)
    
    distribution_id=$(echo "$distribution_output" | grep -o '"Id": "[^"]*"' | head -1 | cut -d'"' -f4)
    cloudfront_domain=$(echo "$distribution_output" | grep -o '"DomainName": "[^"]*"' | head -1 | cut -d'"' -f4)
    
    rm /tmp/cf-config.json
    
    echo "✅ CloudFront distribution created"
    echo "Distribution ID: $distribution_id"
    echo "CloudFront URL: https://$cloudfront_domain"
    echo ""
    echo "⏳ Distribution is deploying... This takes 10-15 minutes"
    echo "Check status with: aws cloudfront get-distribution --id $distribution_id"
    
    # Save distribution info
    cat > cloudfront-info.txt << EOF
CloudFront Distribution Information
====================================
Distribution ID: $distribution_id
CloudFront URL: https://$cloudfront_domain
S3 Bucket: $bucket_name
Created: $(date)

To invalidate cache:
aws cloudfront create-invalidation --distribution-id $distribution_id --paths "/*"

To update distribution:
aws cloudfront get-distribution-config --id $distribution_id > config.json
# Edit config.json
aws cloudfront update-distribution --id $distribution_id --distribution-config file://config.json
EOF
    
    echo "📝 Distribution info saved to cloudfront-info.txt"
fi

# Update API Gateway CORS
echo ""
echo "⚠️  Important: Update API Gateway CORS"
echo "======================================"
echo "Add these origins to your API Gateway CORS configuration:"
echo "  - $website_url"
if [ "$create_cloudfront" = "y" ]; then
    echo "  - https://$cloudfront_domain"
fi
echo ""

# Create deployment info file
cat > deployment-info.txt << EOF
Deployment Information
======================
Deployment Date: $(date)
S3 Bucket: $bucket_name
S3 Website URL: $website_url
AWS Region: $aws_region
API Gateway URL: $api_url
EOF

if [ "$create_cloudfront" = "y" ]; then
    cat >> deployment-info.txt << EOF
CloudFront Distribution ID: $distribution_id
CloudFront URL: https://$cloudfront_domain
EOF
fi

cat >> deployment-info.txt << EOF

Update Commands
===============
Upload new version:
  aws s3 cp index.html s3://$bucket_name/ --content-type "text/html"

EOF

if [ "$create_cloudfront" = "y" ]; then
    cat >> deployment-info.txt << EOF
Invalidate CloudFront cache:
  aws cloudfront create-invalidation --distribution-id $distribution_id --paths "/*"

EOF
fi

echo "📝 Deployment info saved to deployment-info.txt"

echo ""
echo "✅ Deployment Complete!"
echo ""
echo "🌐 Your application is accessible at:"
echo "   S3: $website_url"
if [ "$create_cloudfront" = "y" ]; then
    echo "   CloudFront: https://$cloudfront_domain (after deployment completes)"
fi
echo ""
echo "📋 Next Steps:"
echo "=============="
echo "1. Update API Gateway CORS (see above)"
echo "2. Test the application"
if [ "$create_cloudfront" = "y" ]; then
    echo "3. Wait for CloudFront deployment (10-15 minutes)"
    echo "4. Test CloudFront URL"
    echo "5. (Optional) Set up custom domain with Route 53"
fi
echo ""
