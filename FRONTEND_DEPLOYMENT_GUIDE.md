# Frontend Deployment Guide

This guide provides comprehensive step-by-step instructions for deploying the Document Policy Processor frontend using multiple deployment options.

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Configuration](#configuration)
3. [Deployment Options](#deployment-options)
   - [Option 1: Streamlit Cloud (Recommended)](#option-1-streamlit-cloud-recommended)
   - [Option 2: AWS EC2](#option-2-aws-ec2)
   - [Option 3: Static HTML on S3 + CloudFront](#option-3-static-html-on-s3--cloudfront)
   - [Option 4: Docker Container](#option-4-docker-container)
4. [Testing Deployment](#testing-deployment)
5. [Custom Domain Setup](#custom-domain-setup)
6. [Troubleshooting](#troubleshooting)

---

## Prerequisites

Before deploying, ensure you have:

- ✅ Backend API deployed and accessible (API Gateway URL)
- ✅ API Gateway CORS configured for your frontend domain
- ✅ Python 3.9+ installed (for Streamlit options)
- ✅ AWS CLI configured (for AWS deployments)
- ✅ Git repository with frontend code

## Configuration

### Required Configuration

You need your **API Gateway URL** from the backend deployment. This should look like:
```
https://abc123xyz.execute-api.us-east-1.amazonaws.com/prod
```

Find this URL in:
- AWS Console → API Gateway → Your API → Stages → prod
- Or from your backend deployment output

---

## Deployment Options

## Option 1: Streamlit Cloud (Recommended)

**Best for:** Quick deployment, free hosting, automatic updates

**Pros:**
- ✅ Free hosting
- ✅ Automatic deployments from GitHub
- ✅ Built-in SSL/HTTPS
- ✅ Easy to update

**Cons:**
- ❌ Limited customization
- ❌ Streamlit branding
- ❌ Resource limits on free tier

### Step-by-Step Instructions

#### 1. Prepare Your Repository

Ensure your repository has these files:
```
frontend/
├── app.py
├── requirements.txt
└── .streamlit/
    └── secrets.toml.example
```

#### 2. Push to GitHub

```bash
# If not already in a Git repository
cd document-policy-processor
git init
git add .
git commit -m "Add frontend application"

# Create GitHub repository and push
git remote add origin https://github.com/YOUR_USERNAME/document-policy-processor.git
git branch -M main
git push -u origin main
```

#### 3. Deploy to Streamlit Cloud

1. Go to [share.streamlit.io](https://share.streamlit.io)
2. Click "New app"
3. Connect your GitHub account (if not already connected)
4. Select your repository: `YOUR_USERNAME/document-policy-processor`
5. Set the main file path: `frontend/app.py`
6. Click "Advanced settings"
7. Set Python version: `3.11`
8. Add secrets (see below)
9. Click "Deploy"

#### 4. Configure Secrets

In the Streamlit Cloud dashboard:

1. Go to your app settings
2. Click "Secrets"
3. Add this content:

```toml
API_BASE_URL = "https://YOUR-API-GATEWAY-URL.amazonaws.com/prod"
```

Replace `YOUR-API-GATEWAY-URL` with your actual API Gateway URL.

#### 5. Update CORS

Update your API Gateway CORS settings to allow your Streamlit Cloud URL:

```bash
# Your Streamlit Cloud URL will be:
# https://YOUR-USERNAME-document-policy-processor-frontend-app-HASH.streamlit.app

# Add this to API Gateway CORS allowed origins
```

#### 6. Test Your Deployment

1. Visit your Streamlit Cloud URL
2. Upload a test document
3. Enter test symptoms
4. Verify processing completes successfully

**Deployment Complete!** 🎉

Your app URL: `https://YOUR-USERNAME-document-policy-processor-frontend-app-HASH.streamlit.app`

---

## Option 2: AWS EC2

**Best for:** Full control, custom domain, production deployments

**Pros:**
- ✅ Full control over environment
- ✅ Can use custom domain
- ✅ Better performance
- ✅ No resource limits

**Cons:**
- ❌ Costs money (but t2.micro is free tier eligible)
- ❌ Requires server management
- ❌ Manual SSL setup

### Step-by-Step Instructions

#### 1. Launch EC2 Instance

```bash
# Using AWS CLI
aws ec2 run-instances \
  --image-id ami-0c55b159cbfafe1f0 \
  --instance-type t2.micro \
  --key-name YOUR_KEY_PAIR \
  --security-group-ids sg-YOUR_SECURITY_GROUP \
  --tag-specifications 'ResourceType=instance,Tags=[{Key=Name,Value=document-policy-processor-frontend}]'
```

Or use AWS Console:
1. Go to EC2 → Launch Instance
2. Choose Amazon Linux 2023 AMI
3. Select t2.micro (free tier eligible)
4. Configure security group (see below)
5. Launch with your key pair

#### 2. Configure Security Group

Allow these inbound rules:
- **SSH**: Port 22 from your IP
- **HTTP**: Port 80 from 0.0.0.0/0
- **HTTPS**: Port 443 from 0.0.0.0/0 (if using SSL)
- **Streamlit**: Port 8501 from 0.0.0.0/0 (for testing)

#### 3. Connect to Instance

```bash
ssh -i YOUR_KEY.pem ec2-user@YOUR_EC2_PUBLIC_IP
```

#### 4. Install Dependencies

```bash
# Update system
sudo yum update -y

# Install Python 3.11
sudo yum install python3.11 python3.11-pip -y

# Install Git
sudo yum install git -y

# Clone your repository
git clone https://github.com/YOUR_USERNAME/document-policy-processor.git
cd document-policy-processor/frontend
```

#### 5. Install Python Dependencies

```bash
# Create virtual environment
python3.11 -m venv venv
source venv/bin/activate

# Install requirements
pip install -r requirements.txt
```

#### 6. Configure Secrets

```bash
# Create secrets directory
mkdir -p .streamlit

# Create secrets file
cat > .streamlit/secrets.toml << EOF
API_BASE_URL = "https://YOUR-API-GATEWAY-URL.amazonaws.com/prod"
EOF
```

#### 7. Run Streamlit (Testing)

```bash
# Test run
streamlit run app.py --server.port 8501 --server.address 0.0.0.0

# Visit http://YOUR_EC2_PUBLIC_IP:8501 to test
```

#### 8. Set Up as System Service

Create a systemd service for automatic startup:

```bash
# Create service file
sudo tee /etc/systemd/system/streamlit.service > /dev/null << EOF
[Unit]
Description=Streamlit Document Policy Processor
After=network.target

[Service]
Type=simple
User=ec2-user
WorkingDirectory=/home/ec2-user/document-policy-processor/frontend
Environment="PATH=/home/ec2-user/document-policy-processor/frontend/venv/bin"
ExecStart=/home/ec2-user/document-policy-processor/frontend/venv/bin/streamlit run app.py --server.port 8501 --server.address 0.0.0.0
Restart=always

[Install]
WantedBy=multi-user.target
EOF

# Enable and start service
sudo systemctl daemon-reload
sudo systemctl enable streamlit
sudo systemctl start streamlit

# Check status
sudo systemctl status streamlit
```

#### 9. Set Up Nginx Reverse Proxy (Optional)

For production with SSL:

```bash
# Install Nginx
sudo yum install nginx -y

# Configure Nginx
sudo tee /etc/nginx/conf.d/streamlit.conf > /dev/null << EOF
server {
    listen 80;
    server_name YOUR_DOMAIN_OR_IP;

    location / {
        proxy_pass http://localhost:8501;
        proxy_http_version 1.1;
        proxy_set_header Upgrade \$http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }
}
EOF

# Start Nginx
sudo systemctl enable nginx
sudo systemctl start nginx
```

#### 10. Test Deployment

Visit `http://YOUR_EC2_PUBLIC_IP` and test the application.

**Deployment Complete!** 🎉

---

## Option 3: Static HTML on S3 + CloudFront

**Best for:** Simple static deployment, lowest cost, high scalability

**Pros:**
- ✅ Very low cost
- ✅ Highly scalable
- ✅ Built-in CDN with CloudFront
- ✅ Easy SSL with ACM

**Cons:**
- ❌ No server-side processing
- ❌ Limited to static HTML version
- ❌ Less interactive than Streamlit

### Step-by-Step Instructions

#### 1. Prepare Static HTML

The static HTML version is in `frontend/index.html`. Update the API URL:

```bash
cd document-policy-processor/frontend

# Edit index.html and update API_BASE_URL
# Find this line:
# const API_BASE_URL = 'https://your-api-gateway-url.amazonaws.com/prod';
# Replace with your actual API Gateway URL
```

#### 2. Create S3 Bucket

```bash
# Create bucket (must be globally unique name)
aws s3 mb s3://document-policy-processor-frontend-YOUR-UNIQUE-ID

# Enable static website hosting
aws s3 website s3://document-policy-processor-frontend-YOUR-UNIQUE-ID \
  --index-document index.html \
  --error-document index.html
```

#### 3. Configure Bucket Policy

```bash
# Create bucket policy file
cat > bucket-policy.json << EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "PublicReadGetObject",
      "Effect": "Allow",
      "Principal": "*",
      "Action": "s3:GetObject",
      "Resource": "arn:aws:s3:::document-policy-processor-frontend-YOUR-UNIQUE-ID/*"
    }
  ]
}
EOF

# Apply policy
aws s3api put-bucket-policy \
  --bucket document-policy-processor-frontend-YOUR-UNIQUE-ID \
  --policy file://bucket-policy.json
```

#### 4. Upload Files

```bash
# Upload index.html
aws s3 cp index.html s3://document-policy-processor-frontend-YOUR-UNIQUE-ID/ \
  --content-type "text/html"

# If you have other assets (CSS, JS, images)
# aws s3 sync ./assets s3://document-policy-processor-frontend-YOUR-UNIQUE-ID/assets/
```

#### 5. Test S3 Website

```bash
# Get website URL
echo "http://document-policy-processor-frontend-YOUR-UNIQUE-ID.s3-website-us-east-1.amazonaws.com"

# Visit this URL to test
```

#### 6. Create CloudFront Distribution (Optional but Recommended)

For HTTPS and better performance:

```bash
# Create CloudFront distribution
aws cloudfront create-distribution \
  --origin-domain-name document-policy-processor-frontend-YOUR-UNIQUE-ID.s3-website-us-east-1.amazonaws.com \
  --default-root-object index.html

# This will output a CloudFront domain like:
# d1234567890abc.cloudfront.net
```

Or use AWS Console:
1. Go to CloudFront → Create Distribution
2. Origin Domain: Your S3 website endpoint
3. Viewer Protocol Policy: Redirect HTTP to HTTPS
4. Default Root Object: index.html
5. Create Distribution

#### 7. Update CORS

Add CloudFront domain to API Gateway CORS:

```bash
# Add to allowed origins:
# https://d1234567890abc.cloudfront.net
```

#### 8. Test CloudFront Deployment

Visit your CloudFront URL and test the application.

**Deployment Complete!** 🎉

Your app URL: `https://d1234567890abc.cloudfront.net`

---

## Option 4: Docker Container

**Best for:** Consistent environments, container orchestration, local development

**Pros:**
- ✅ Consistent environment
- ✅ Easy to replicate
- ✅ Can deploy to ECS, Kubernetes, etc.
- ✅ Good for development

**Cons:**
- ❌ Requires Docker knowledge
- ❌ More complex setup
- ❌ Higher resource usage

### Step-by-Step Instructions

#### 1. Create Dockerfile

```bash
cd document-policy-processor/frontend

# Create Dockerfile
cat > Dockerfile << 'EOF'
FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY app.py .
COPY .streamlit .streamlit

# Expose port
EXPOSE 8501

# Health check
HEALTHCHECK CMD curl --fail http://localhost:8501/_stcore/health || exit 1

# Run application
CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]
EOF
```

#### 2. Create .dockerignore

```bash
cat > .dockerignore << EOF
__pycache__
*.pyc
*.pyo
*.pyd
.Python
venv/
.env
.git
.gitignore
*.md
EOF
```

#### 3. Build Docker Image

```bash
# Build image
docker build -t document-policy-processor-frontend:latest .

# Verify image
docker images | grep document-policy-processor-frontend
```

#### 4. Run Container Locally

```bash
# Run container
docker run -d \
  --name frontend \
  -p 8501:8501 \
  -e API_BASE_URL="https://YOUR-API-GATEWAY-URL.amazonaws.com/prod" \
  document-policy-processor-frontend:latest

# Check logs
docker logs frontend

# Test
curl http://localhost:8501
```

#### 5. Deploy to AWS ECS (Optional)

```bash
# Create ECR repository
aws ecr create-repository --repository-name document-policy-processor-frontend

# Get login command
aws ecr get-login-password --region us-east-1 | \
  docker login --username AWS --password-stdin YOUR_ACCOUNT_ID.dkr.ecr.us-east-1.amazonaws.com

# Tag image
docker tag document-policy-processor-frontend:latest \
  YOUR_ACCOUNT_ID.dkr.ecr.us-east-1.amazonaws.com/document-policy-processor-frontend:latest

# Push image
docker push YOUR_ACCOUNT_ID.dkr.ecr.us-east-1.amazonaws.com/document-policy-processor-frontend:latest

# Create ECS task definition and service (see AWS ECS documentation)
```

**Deployment Complete!** 🎉

---

## Testing Deployment

After deploying with any option, test your deployment:

### 1. Basic Connectivity Test

```bash
# Test if frontend is accessible
curl -I https://YOUR-FRONTEND-URL

# Should return HTTP 200
```

### 2. API Health Check Test

Visit your frontend and click "Check API Health" in the sidebar.

### 3. End-to-End Test

1. **Upload a test document**
   - Use a sample PDF or image
   - File should be under 10MB

2. **Enter test symptoms**
   ```
   I have been experiencing severe headaches and dizziness for the past two weeks.
   ```

3. **Submit and verify**
   - Processing should complete within 30-60 seconds
   - Results should display with recommendations
   - No errors should appear

### 4. Browser Console Check

Open browser developer tools (F12) and check for:
- ✅ No JavaScript errors
- ✅ Successful API calls (200 status)
- ✅ No CORS errors

### 5. Mobile Responsiveness Test

Test on mobile devices or use browser responsive mode:
- ✅ Layout adapts to screen size
- ✅ All buttons are clickable
- ✅ Text is readable

---

## Custom Domain Setup

### For Streamlit Cloud

Streamlit Cloud doesn't support custom domains on free tier. Consider:
- Upgrade to Streamlit Cloud Teams
- Use a URL shortener (bit.ly, tinyurl.com)
- Deploy to EC2 or S3+CloudFront instead

### For EC2 with Nginx

#### 1. Register Domain

Register a domain with Route 53 or any domain registrar.

#### 2. Create A Record

```bash
# Using Route 53
aws route53 change-resource-record-sets \
  --hosted-zone-id YOUR_ZONE_ID \
  --change-batch '{
    "Changes": [{
      "Action": "CREATE",
      "ResourceRecordSet": {
        "Name": "app.yourdomain.com",
        "Type": "A",
        "TTL": 300,
        "ResourceRecords": [{"Value": "YOUR_EC2_PUBLIC_IP"}]
      }
    }]
  }'
```

#### 3. Install SSL Certificate

```bash
# Install Certbot
sudo yum install certbot python3-certbot-nginx -y

# Get certificate
sudo certbot --nginx -d app.yourdomain.com

# Certbot will automatically configure Nginx for HTTPS
```

#### 4. Update Nginx Config

Certbot updates this automatically, but verify:

```bash
sudo cat /etc/nginx/conf.d/streamlit.conf
# Should now have SSL configuration
```

### For S3 + CloudFront

#### 1. Request SSL Certificate

```bash
# Request certificate in ACM (must be in us-east-1 for CloudFront)
aws acm request-certificate \
  --domain-name app.yourdomain.com \
  --validation-method DNS \
  --region us-east-1
```

#### 2. Validate Certificate

Follow the DNS validation instructions in ACM console.

#### 3. Update CloudFront Distribution

```bash
# Add alternate domain name and SSL certificate
aws cloudfront update-distribution \
  --id YOUR_DISTRIBUTION_ID \
  --aliases app.yourdomain.com \
  --viewer-certificate ACMCertificateArn=YOUR_CERT_ARN,SSLSupportMethod=sni-only
```

#### 4. Create Route 53 Alias

```bash
aws route53 change-resource-record-sets \
  --hosted-zone-id YOUR_ZONE_ID \
  --change-batch '{
    "Changes": [{
      "Action": "CREATE",
      "ResourceRecordSet": {
        "Name": "app.yourdomain.com",
        "Type": "A",
        "AliasTarget": {
          "HostedZoneId": "Z2FDTNDATAQYW2",
          "DNSName": "d1234567890abc.cloudfront.net",
          "EvaluateTargetHealth": false
        }
      }
    }]
  }'
```

---

## Troubleshooting

### Issue: Cannot connect to API

**Symptoms:**
- "Failed to get upload URL" error
- "Cannot reach API" message
- Network errors in console

**Solutions:**

1. **Verify API URL**
   ```bash
   # Test API directly
   curl https://YOUR-API-GATEWAY-URL.amazonaws.com/prod/api/health
   
   # Should return: {"status": "healthy"}
   ```

2. **Check CORS Configuration**
   - API Gateway must allow your frontend domain
   - Check API Gateway → Your API → CORS
   - Allowed origins should include your frontend URL

3. **Verify API Gateway Deployment**
   ```bash
   # Ensure API is deployed to 'prod' stage
   aws apigateway get-deployments --rest-api-id YOUR_API_ID
   ```

### Issue: File upload fails

**Symptoms:**
- "Failed to upload file to S3" error
- Upload hangs indefinitely
- 403 Forbidden errors

**Solutions:**

1. **Check S3 Bucket Permissions**
   ```bash
   # Verify bucket policy allows uploads
   aws s3api get-bucket-policy --bucket YOUR_BUCKET_NAME
   ```

2. **Verify Presigned URL**
   - Presigned URLs expire (usually 15 minutes)
   - Check Lambda function generates valid URLs
   - Test presigned URL directly with curl

3. **Check File Size**
   - Maximum file size is 10MB
   - API Gateway has 10MB payload limit
   - Consider increasing Lambda timeout for large files

### Issue: Processing timeout

**Symptoms:**
- "Processing timeout" message
- Job stuck in "processing" status
- No results after 5 minutes

**Solutions:**

1. **Check Lambda Logs**
   ```bash
   # View recent Lambda logs
   aws logs tail /aws/lambda/document-policy-processor --follow
   ```

2. **Verify Lambda Timeout**
   ```bash
   # Check Lambda timeout setting (should be 300 seconds)
   aws lambda get-function-configuration \
     --function-name document-policy-processor
   ```

3. **Check DynamoDB**
   ```bash
   # Verify job status in DynamoDB
   aws dynamodb get-item \
     --table-name ProcessingJobs \
     --key '{"job_id": {"S": "YOUR_JOB_ID"}}'
   ```

### Issue: Streamlit app won't start

**Symptoms:**
- "Address already in use" error
- Streamlit crashes on startup
- Import errors

**Solutions:**

1. **Check Port Availability**
   ```bash
   # Kill existing Streamlit process
   pkill -f streamlit
   
   # Or use different port
   streamlit run app.py --server.port 8502
   ```

2. **Verify Dependencies**
   ```bash
   # Reinstall requirements
   pip install --upgrade -r requirements.txt
   ```

3. **Check Python Version**
   ```bash
   # Ensure Python 3.9+
   python --version
   ```

### Issue: CORS errors in browser

**Symptoms:**
- "CORS policy" errors in console
- "Access-Control-Allow-Origin" errors
- API calls fail with CORS errors

**Solutions:**

1. **Update API Gateway CORS**
   - Add your frontend domain to allowed origins
   - Include both HTTP and HTTPS versions
   - Add wildcard for development: `*`

2. **Check Response Headers**
   ```bash
   # Verify CORS headers in response
   curl -H "Origin: https://your-frontend-url.com" \
     -H "Access-Control-Request-Method: POST" \
     -H "Access-Control-Request-Headers: Content-Type" \
     -X OPTIONS \
     https://YOUR-API-GATEWAY-URL.amazonaws.com/prod/api/process-document
   ```

### Issue: Static HTML not updating

**Symptoms:**
- Changes not reflected after deployment
- Old version still showing
- Cache issues

**Solutions:**

1. **Clear CloudFront Cache**
   ```bash
   # Create invalidation
   aws cloudfront create-invalidation \
     --distribution-id YOUR_DISTRIBUTION_ID \
     --paths "/*"
   ```

2. **Force Browser Refresh**
   - Press Ctrl+Shift+R (Windows/Linux)
   - Press Cmd+Shift+R (Mac)
   - Clear browser cache

3. **Verify S3 Upload**
   ```bash
   # Check file in S3
   aws s3 ls s3://YOUR_BUCKET_NAME/
   
   # Re-upload if needed
   aws s3 cp index.html s3://YOUR_BUCKET_NAME/ --content-type "text/html"
   ```

---

## Deployment Checklist

Before marking deployment as complete, verify:

- [ ] Frontend is accessible via public URL
- [ ] API health check passes
- [ ] Can upload test document successfully
- [ ] Processing completes and shows results
- [ ] No errors in browser console
- [ ] No CORS errors
- [ ] Mobile responsive (if applicable)
- [ ] HTTPS enabled (for production)
- [ ] Custom domain configured (optional)
- [ ] Monitoring/logging set up
- [ ] Documentation updated with URL

---

## Next Steps

After successful deployment:

1. **Update Documentation**
   - Add frontend URL to README.md
   - Update SUBMISSION.md with working prototype URL

2. **Test End-to-End**
   - Run complete workflow test
   - Test with different document types
   - Verify error handling

3. **Prepare Demo Video**
   - Use deployed frontend for demo recording
   - Show complete workflow
   - Highlight key features

4. **Monitor Performance**
   - Check CloudWatch logs
   - Monitor API Gateway metrics
   - Track user errors

---

## Support

For issues or questions:

1. Check CloudWatch logs for backend errors
2. Check browser console for frontend errors
3. Review API Gateway execution logs
4. Consult AWS documentation for service-specific issues

---

**Requirements Validation:**

This deployment guide satisfies:
- ✅ **Requirement 3.5**: Working prototype accessible via public URL
- ✅ **Task 10.3**: Deploy frontend with multiple options
- ✅ **Task 10.3**: Configure custom domain (optional)
- ✅ **Task 10.3**: Test frontend accessibility

**Deployment Options Summary:**

| Option | Cost | Complexity | Best For |
|--------|------|------------|----------|
| Streamlit Cloud | Free | ⭐ Easy | Quick demos, hackathons |
| AWS EC2 | ~$5/mo | ⭐⭐ Medium | Production, custom domains |
| S3 + CloudFront | ~$1/mo | ⭐⭐ Medium | Static sites, high scale |
| Docker | Varies | ⭐⭐⭐ Hard | Container orchestration |

Choose the option that best fits your needs and technical expertise!
