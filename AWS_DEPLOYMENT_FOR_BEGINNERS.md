# AWS Deployment for Beginners

**Complete step-by-step guide to deploy your Document Policy Processor to AWS**

This guide assumes you have ZERO AWS experience. We'll walk through everything from creating an AWS account to deploying your application.

---

## 📋 Table of Contents

1. [Prerequisites](#prerequisites)
2. [AWS Account Setup](#aws-account-setup)
3. [Install AWS CLI](#install-aws-cli)
4. [Configure AWS Credentials](#configure-aws-credentials)
5. [Deploy Infrastructure](#deploy-infrastructure)
6. [Deploy Lambda Function](#deploy-lambda-function)
7. [Deploy API Gateway](#deploy-api-gateway)
8. [Setup CloudWatch](#setup-cloudwatch)
9. [Test Your Deployment](#test-your-deployment)
10. [Troubleshooting](#troubleshooting)

---

## Prerequisites

Before starting, make sure you have:

- ✅ Windows computer
- ✅ Internet connection
- ✅ Credit/debit card (for AWS account - free tier available)
- ✅ Email address
- ✅ Phone number (for verification)
- ✅ This project code (already have it!)

**Time Required**: 1-2 hours for first-time setup

---

## AWS Account Setup

### Step 1: Create AWS Account

1. **Go to AWS website**
   - Open browser: https://aws.amazon.com/
   - Click "Create an AWS Account" (orange button, top right)

2. **Enter account information**
   ```
   Email address: your-email@example.com
   Password: [create strong password]
   AWS account name: document-policy-processor
   ```
   - Click "Continue"

3. **Contact Information**
   ```
   Account type: Personal
   Full name: [Your name]
   Phone number: [Your phone]
   Country: [Your country]
   Address: [Your address]
   ```
   - Check "I have read and agree to the terms"
   - Click "Create Account and Continue"

4. **Payment Information**
   - Enter credit/debit card details
   - Don't worry - we'll use FREE TIER services
   - AWS won't charge unless you exceed free tier limits
   - Click "Verify and Add"

5. **Identity Verification**
   - Choose "Text message (SMS)" or "Voice call"
   - Enter verification code
   - Click "Continue"

6. **Select Support Plan**
   - Choose "Basic support - Free"
   - Click "Complete sign up"

7. **Wait for confirmation**
   - You'll receive email: "Welcome to Amazon Web Services"
   - This may take a few minutes

### Step 2: Sign in to AWS Console

1. **Go to AWS Console**
   - Open: https://console.aws.amazon.com/
   - Click "Sign in to the Console"

2. **Enter credentials**
   ```
   Email: [your email]
   Password: [your password]
   ```
   - Click "Sign in"

3. **You're in!**
   - You should see the AWS Management Console
   - This is your AWS dashboard

---

## Install AWS CLI

The AWS CLI (Command Line Interface) lets you control AWS from your computer's command prompt.

### Step 1: Download AWS CLI

1. **Download installer**
   - Go to: https://aws.amazon.com/cli/
   - Click "Download for Windows"
   - Or direct link: https://awscli.amazonaws.com/AWSCLIV2.msi

2. **Run installer**
   - Double-click the downloaded file
   - Click "Next" through the wizard
   - Accept defaults
   - Click "Install"
   - Click "Finish"

### Step 2: Verify Installation

1. **Open Command Prompt**
   - Press `Win + R`
   - Type: `cmd`
   - Press Enter

2. **Check AWS CLI version**
   ```cmd
   aws --version
   ```
   
   **Expected output**:
   ```
   aws-cli/2.x.x Python/3.x.x Windows/10 exe/AMD64
   ```

3. **If you see an error**:
   - Close and reopen Command Prompt
   - Try again
   - If still fails, restart your computer

---

## Configure AWS Credentials

AWS needs to know who you are. We'll create access keys and configure them.

### Step 1: Create Access Keys

1. **Open AWS Console**
   - Go to: https://console.aws.amazon.com/

2. **Navigate to IAM**
   - In the search bar at top, type: `IAM`
   - Click "IAM" (Identity and Access Management)

3. **Create User** (if you don't have one)
   - Click "Users" in left sidebar
   - Click "Create user" (orange button)
   - User name: `document-policy-processor-user`
   - Click "Next"

4. **Set Permissions**
   - Select "Attach policies directly"
   - Search for and check these policies:
     - ✅ `AWSLambda_FullAccess`
     - ✅ `AmazonS3FullAccess`
     - ✅ `AmazonDynamoDBFullAccess`
     - ✅ `AmazonAPIGatewayAdministrator`
     - ✅ `CloudWatchFullAccess`
     - ✅ `IAMFullAccess`
   - Click "Next"
   - Click "Create user"

5. **Create Access Key**
   - Click on the user you just created
   - Click "Security credentials" tab
   - Scroll to "Access keys"
   - Click "Create access key"
   - Select "Command Line Interface (CLI)"
   - Check "I understand..."
   - Click "Next"
   - Description: `Local development`
   - Click "Create access key"

6. **IMPORTANT: Save Your Keys**
   - You'll see:
     ```
     Access key ID: AKIAIOSFODNN7EXAMPLE
     Secret access key: wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY
     ```
   - Click "Download .csv file"
   - Save it somewhere safe!
   - **WARNING**: Never share these keys or commit them to GitHub!

### Step 2: Configure AWS CLI

1. **Open Command Prompt**
   ```cmd
   cd document-policy-processor
   ```

2. **Run AWS configure**
   ```cmd
   aws configure
   ```

3. **Enter your credentials**
   ```
   AWS Access Key ID [None]: [paste your Access Key ID]
   AWS Secret Access Key [None]: [paste your Secret Access Key]
   Default region name [None]: us-east-1
   Default output format [None]: json
   ```

4. **Verify configuration**
   ```cmd
   aws sts get-caller-identity
   ```
   
   **Expected output**:
   ```json
   {
       "UserId": "AIDAI...",
       "Account": "123456789012",
       "Arn": "arn:aws:iam::123456789012:user/..."
   }
   ```

5. **If you see an error**:
   - Double-check your access keys
   - Make sure you copied them correctly
   - Try running `aws configure` again

---

## Deploy Infrastructure

Now we'll create the AWS resources (S3 buckets, DynamoDB tables, IAM roles).

### Step 1: Create S3 Buckets

1. **Open Command Prompt**
   ```cmd
   cd document-policy-processor\infrastructure
   ```

2. **Run S3 setup script**
   ```cmd
   deploy-s3.bat
   ```

3. **What this does**:
   - Creates S3 bucket for document uploads
   - Creates folders: documents/, embeddings/, results/
   - Configures CORS for frontend access

4. **Expected output**:
   ```
   Creating S3 bucket: document-policy-processor-uploads-[random]
   Bucket created successfully!
   Configuring CORS...
   CORS configured successfully!
   ```

5. **Save the bucket name**:
   - You'll see: `Bucket name: document-policy-processor-uploads-abc123`
   - Write this down! You'll need it later.

### Step 2: Create DynamoDB Tables

1. **Run DynamoDB setup script**
   ```cmd
   deploy-dynamodb.bat
   ```

2. **What this does**:
   - Creates "Policies" table for storing insurance policies
   - Creates "ProcessingJobs" table for tracking document processing
   - Adds sample policy data

3. **Expected output**:
   ```
   Creating DynamoDB table: Policies
   Table created successfully!
   Creating DynamoDB table: ProcessingJobs
   Table created successfully!
   Adding sample policies...
   Sample data added!
   ```

### Step 3: Create IAM Roles

1. **Run IAM setup script**
   ```cmd
   deploy-iam.bat
   ```

2. **What this does**:
   - Creates Lambda execution role
   - Grants permissions to access S3, DynamoDB, Textract, CloudWatch

3. **Expected output**:
   ```
   Creating IAM role: DocumentPolicyProcessorLambdaRole
   Role created successfully!
   Attaching policies...
   Policies attached!
   ```

4. **Save the role ARN**:
   - You'll see: `Role ARN: arn:aws:iam::123456789012:role/...`
   - Write this down!

### Step 4: Pre-compute Policy Embeddings

1. **Run embeddings script**
   ```cmd
   deploy-embeddings.bat
   ```

2. **What this does**:
   - Generates embeddings for all sample policies
   - Uploads embeddings to S3

3. **Expected output**:
   ```
   Generating embeddings for 10 policies...
   Uploading to S3...
   Embeddings uploaded successfully!
   ```

---

## Deploy Lambda Function

Now we'll deploy the main processing function.

### Step 1: Set Environment Variables

1. **Open Notepad**
   - Create a file called `env-vars.txt`
   - Add these lines (replace with your values):
   ```
   S3_BUCKET_NAME=document-policy-processor-uploads-abc123
   DYNAMODB_TABLE_POLICIES=Policies
   DYNAMODB_TABLE_JOBS=ProcessingJobs
   EMBEDDING_MODEL=all-MiniLM-L6-v2
   LLM_MODEL=gpt-3.5-turbo
   OPENAI_API_KEY=sk-your-openai-key-here
   AWS_REGION=us-east-1
   ```

2. **Get OpenAI API Key** (if you don't have one):
   - Go to: https://platform.openai.com/
   - Sign up or log in
   - Click "API keys" in left sidebar
   - Click "Create new secret key"
   - Copy the key and paste in `env-vars.txt`

### Step 2: Package Lambda Function

1. **Go back to main directory**
   ```cmd
   cd ..
   ```

2. **Run packaging script**
   ```cmd
   python package-lambda.py
   ```
   
   **If this script doesn't exist, create it**:
   ```python
   # package-lambda.py
   import os
   import shutil
   import zipfile
   
   print("Packaging Lambda function...")
   
   # Create package directory
   if os.path.exists("lambda-package"):
       shutil.rmtree("lambda-package")
   os.makedirs("lambda-package")
   
   # Copy source files
   for file in os.listdir("src"):
       if file.endswith(".py"):
           shutil.copy(f"src/{file}", f"lambda-package/{file}")
   
   # Install dependencies
   os.system("pip install -r src/requirements.txt -t lambda-package/")
   
   # Create ZIP file
   with zipfile.ZipFile("lambda-function.zip", "w", zipfile.ZIP_DEFLATED) as zipf:
       for root, dirs, files in os.walk("lambda-package"):
           for file in files:
               file_path = os.path.join(root, file)
               arcname = os.path.relpath(file_path, "lambda-package")
               zipf.write(file_path, arcname)
   
   print("Package created: lambda-function.zip")
   print(f"Size: {os.path.getsize('lambda-function.zip') / 1024 / 1024:.2f} MB")
   ```

3. **Run it**:
   ```cmd
   py package-lambda.py
   ```

### Step 3: Deploy Lambda Function

1. **Run deployment script**
   ```cmd
   deploy-lambda.bat
   ```

2. **When prompted, enter**:
   - Function name: `DocumentPolicyProcessor`
   - Role ARN: [paste the role ARN you saved earlier]
   - Environment variables: [paste from env-vars.txt]

3. **Expected output**:
   ```
   Uploading Lambda function...
   Function created successfully!
   Function ARN: arn:aws:lambda:us-east-1:123456789012:function:DocumentPolicyProcessor
   ```

4. **Save the function ARN**!

### Step 4: Test Lambda Function

1. **Run test script**
   ```cmd
   verify-lambda-deployment.bat
   ```

2. **Expected output**:
   ```
   Testing Lambda function...
   Response: {
       "statusCode": 200,
       "body": "..."
   }
   Test successful!
   ```

---

## Deploy API Gateway

Now we'll create the REST API that the frontend will call.

### Step 1: Create API

1. **Run API Gateway deployment**
   ```cmd
   deploy-api-gateway.bat
   ```

2. **When prompted, enter**:
   - API name: `DocumentPolicyProcessorAPI`
   - Lambda function ARN: [paste the Lambda ARN]

3. **Expected output**:
   ```
   Creating API Gateway...
   API created successfully!
   API ID: abc123xyz
   API URL: https://abc123xyz.execute-api.us-east-1.amazonaws.com/prod
   ```

4. **IMPORTANT: Save the API URL**!
   - You'll need this for the frontend

### Step 2: Create API Key

1. **The script will ask**: "Create API key? (y/n)"
   - Type: `y`
   - Press Enter

2. **Save the API key**:
   ```
   API Key: AbCdEf123456789
   ```

### Step 3: Test API

1. **Run API test**
   ```cmd
   test-api-gateway.bat --api-url https://your-api-url.com/prod --api-key your-api-key
   ```

2. **Expected output**:
   ```
   Testing health endpoint...
   Response: {"status": "healthy"}
   
   Testing status endpoint...
   Response: {"error": "Job not found"}
   
   All tests passed!
   ```

---

## Setup CloudWatch

CloudWatch monitors your application and logs errors.

### Step 1: Configure CloudWatch

1. **Run CloudWatch setup**
   ```cmd
   setup-cloudwatch-monitoring.bat
   ```

2. **Expected output**:
   ```
   Creating log group...
   Log group created!
   Creating dashboard...
   Dashboard created!
   Setting up alarms...
   Alarms configured!
   ```

### Step 2: View Logs

1. **Open AWS Console**
   - Go to: https://console.aws.amazon.com/cloudwatch/

2. **Click "Logs" in left sidebar**
   - You'll see: `/aws/lambda/DocumentPolicyProcessor`
   - Click on it to view logs

3. **Click "Dashboards"**
   - You'll see: `DocumentPolicyProcessor-Dashboard`
   - Click to view metrics

---

## Test Your Deployment

Let's test the complete system end-to-end!

### Step 1: Test Document Upload

1. **Create test file**
   - Create `test-document.txt` with:
   ```
   Patient Name: John Doe
   Diagnosis: Type 2 Diabetes
   Treatment: Insulin therapy required
   ```

2. **Upload to S3**
   ```cmd
   aws s3 cp test-document.txt s3://your-bucket-name/documents/test-document.txt
   ```

### Step 2: Test Processing

1. **Create test request**
   - Create `test-request.json`:
   ```json
   {
     "job_id": "test-123",
     "document_url": "s3://your-bucket-name/documents/test-document.txt",
     "symptoms": "Diagnosed with Type 2 diabetes, requiring insulin therapy"
   }
   ```

2. **Invoke Lambda**
   ```cmd
   aws lambda invoke --function-name DocumentPolicyProcessor --payload file://test-request.json response.json
   ```

3. **Check response**
   ```cmd
   type response.json
   ```

4. **Expected output**:
   ```json
   {
     "statusCode": 200,
     "body": {
       "job_id": "test-123",
       "status": "completed",
       "recommendations": [...]
     }
   }
   ```

### Step 3: Test via API

1. **Use curl to test**
   ```cmd
   curl -X POST https://your-api-url.com/prod/api/process-document ^
     -H "X-Api-Key: your-api-key" ^
     -H "Content-Type: application/json" ^
     -d @test-request.json
   ```

2. **Check response**
   - Should see recommendations!

---

## Troubleshooting

### Common Issues

#### Issue 1: "Access Denied" Error

**Problem**: AWS CLI can't access your account

**Solution**:
```cmd
aws configure
```
- Re-enter your access keys
- Make sure you copied them correctly

#### Issue 2: "Bucket already exists"

**Problem**: S3 bucket name is taken

**Solution**:
- S3 bucket names must be globally unique
- The script adds random characters to avoid this
- If it still fails, edit the script and change the bucket name

#### Issue 3: "Lambda function too large"

**Problem**: Lambda package exceeds size limit

**Solution**:
- Use Lambda layers for large dependencies
- Or use Docker container image instead
- See: `LAMBDA_DEPLOYMENT_GUIDE.md`

#### Issue 4: "OpenAI API Error"

**Problem**: Invalid or missing OpenAI API key

**Solution**:
1. Get API key from https://platform.openai.com/
2. Update environment variable:
   ```cmd
   aws lambda update-function-configuration ^
     --function-name DocumentPolicyProcessor ^
     --environment Variables={OPENAI_API_KEY=sk-your-new-key}
   ```

#### Issue 5: "Timeout Error"

**Problem**: Lambda function times out

**Solution**:
```cmd
aws lambda update-function-configuration ^
  --function-name DocumentPolicyProcessor ^
  --timeout 300 ^
  --memory-size 2048
```

### Getting Help

**Check CloudWatch Logs**:
```cmd
aws logs tail /aws/lambda/DocumentPolicyProcessor --follow
```

**Check Lambda Configuration**:
```cmd
aws lambda get-function-configuration --function-name DocumentPolicyProcessor
```

**Test Lambda Directly**:
```cmd
aws lambda invoke --function-name DocumentPolicyProcessor --payload file://test-event.json output.json
type output.json
```

---

## Next Steps

### ✅ Deployment Complete!

You now have:
- ✅ Lambda function deployed
- ✅ API Gateway configured
- ✅ CloudWatch monitoring active
- ✅ S3 buckets created
- ✅ DynamoDB tables ready

### Configure Frontend

1. **Update frontend configuration**
   - Open `frontend/app.py`
   - Update API URL:
   ```python
   API_BASE_URL = "https://your-api-url.com/prod"
   API_KEY = "your-api-key"
   ```

2. **Run frontend locally**
   ```cmd
   cd frontend
   streamlit run app.py
   ```

3. **Test complete flow**
   - Upload document
   - Enter symptoms
   - View recommendations

### Record Demo Video

Now that everything is deployed and working:
1. Follow `demo/VIDEO_CREATION_WALKTHROUGH.md`
2. Use `demo/COMPLETE_3MIN_SCRIPT.md` for narration
3. Record your working application!

### Submit to Hackathon

1. Update README.md with:
   - API URL
   - Demo video link
   - Screenshots

2. Make GitHub repository public

3. Submit all deliverables!

---

## Cost Estimate

### AWS Free Tier (First 12 Months)

- **Lambda**: 1 million requests/month FREE
- **API Gateway**: 1 million requests/month FREE
- **S3**: 5 GB storage FREE
- **DynamoDB**: 25 GB storage FREE
- **CloudWatch**: 10 custom metrics FREE

### After Free Tier

For this hackathon project with moderate usage:
- **Estimated cost**: $5-10/month
- **To minimize costs**: Delete resources after hackathon

### Delete Resources After Hackathon

```cmd
REM Delete Lambda function
aws lambda delete-function --function-name DocumentPolicyProcessor

REM Delete API Gateway
aws apigateway delete-rest-api --rest-api-id your-api-id

REM Delete S3 bucket (empty it first)
aws s3 rm s3://your-bucket-name --recursive
aws s3 rb s3://your-bucket-name

REM Delete DynamoDB tables
aws dynamodb delete-table --table-name Policies
aws dynamodb delete-table --table-name ProcessingJobs
```

---

## Summary

You've successfully deployed your Document Policy Processor to AWS! 🎉

**What you accomplished**:
1. ✅ Created AWS account
2. ✅ Installed and configured AWS CLI
3. ✅ Deployed infrastructure (S3, DynamoDB, IAM)
4. ✅ Deployed Lambda function
5. ✅ Deployed API Gateway
6. ✅ Setup CloudWatch monitoring
7. ✅ Tested end-to-end flow

**Your application is now**:
- 🌐 Accessible via public API
- 📊 Monitored with CloudWatch
- 🔒 Secured with API keys
- ⚡ Scalable and serverless
- 💰 Running on AWS Free Tier

**Ready for**:
- 🎥 Demo video recording
- 📝 Hackathon submission
- 🏆 Winning the competition!

---

**Need more help?**
- AWS Documentation: https://docs.aws.amazon.com/
- AWS Support: https://console.aws.amazon.com/support/
- Project Documentation: See other .md files in this directory

**Good luck with your hackathon! 🚀**
