# IAM Roles Setup Guide

This guide explains how to set up IAM roles and permissions for the Document Policy Processor.

## Overview

The Document Policy Processor requires two IAM roles:

1. **Lambda Execution Role**: Grants Lambda functions access to S3, DynamoDB, Textract, and CloudWatch
2. **API Gateway Role**: Allows API Gateway to invoke Lambda functions and write logs

## Prerequisites

- AWS CLI installed and configured (`aws configure`)
- Python 3.7+ (for Python script method)
- boto3 library (will be installed automatically if missing)
- Appropriate IAM permissions to create roles and policies

## Quick Start

### On Linux/Mac

```bash
cd infrastructure
chmod +x deploy-iam.sh
./deploy-iam.sh
```

### On Windows

```cmd
cd infrastructure
deploy-iam.bat
```

The script will prompt you to choose between CloudFormation or Python deployment.

## Deployment Methods

### Method 1: CloudFormation (Recommended for Production)

CloudFormation provides infrastructure-as-code with version control and reproducibility.

**Deploy the stack:**

```bash
aws cloudformation create-stack \
  --stack-name document-policy-processor-iam \
  --template-body file://iam-roles.yaml \
  --parameters \
      ParameterKey=Environment,ParameterValue=dev \
      ParameterKey=S3BucketName,ParameterValue=document-policy-processor-uploads \
  --capabilities CAPABILITY_NAMED_IAM
```

**Check stack status:**

```bash
aws cloudformation describe-stacks \
  --stack-name document-policy-processor-iam \
  --query 'Stacks[0].StackStatus'
```

**Get role ARNs:**

```bash
aws cloudformation describe-stacks \
  --stack-name document-policy-processor-iam \
  --query 'Stacks[0].Outputs[*].[OutputKey,OutputValue]' \
  --output table
```

**Update the stack:**

```bash
aws cloudformation update-stack \
  --stack-name document-policy-processor-iam \
  --template-body file://iam-roles.yaml \
  --parameters \
      ParameterKey=Environment,ParameterValue=dev \
      ParameterKey=S3BucketName,ParameterValue=document-policy-processor-uploads \
  --capabilities CAPABILITY_NAMED_IAM
```

**Delete the stack:**

```bash
aws cloudformation delete-stack \
  --stack-name document-policy-processor-iam
```

### Method 2: Python Script (Faster, More Flexible)

The Python script provides immediate feedback and is easier to customize.

**Install dependencies:**

```bash
pip install boto3
```

**Run the script:**

```bash
python setup_iam.py
```

The script will:
1. Create the Lambda execution role
2. Attach AWS managed policies
3. Create inline policies for S3, DynamoDB, Textract, and CloudWatch
4. Create the API Gateway role
5. Create inline policies for Lambda invocation and CloudWatch
6. Verify all roles and policies

## IAM Roles Details

### Lambda Execution Role

**Role Name:** `DocumentPolicyProcessor-Lambda-dev`

**Trust Policy:**
- Allows Lambda service to assume this role

**Managed Policies:**
- `AWSLambdaBasicExecutionRole` - Basic Lambda execution permissions

**Inline Policies:**

1. **S3Access** - Access to document storage bucket
   - `s3:GetObject` - Download documents
   - `s3:PutObject` - Upload results
   - `s3:DeleteObject` - Clean up temporary files
   - `s3:ListBucket` - List bucket contents

2. **DynamoDBAccess** - Access to policy and job tables
   - `dynamodb:GetItem` - Read single items
   - `dynamodb:PutItem` - Write items
   - `dynamodb:UpdateItem` - Update items
   - `dynamodb:Query` - Query tables
   - `dynamodb:Scan` - Scan tables
   - `dynamodb:BatchGetItem` - Batch reads
   - `dynamodb:BatchWriteItem` - Batch writes

3. **TextractAccess** - OCR capabilities
   - `textract:DetectDocumentText` - Synchronous text detection
   - `textract:AnalyzeDocument` - Document analysis
   - `textract:StartDocumentTextDetection` - Async text detection
   - `textract:GetDocumentTextDetection` - Get async results

4. **CloudWatchLogs** - Logging
   - `logs:CreateLogGroup` - Create log groups
   - `logs:CreateLogStream` - Create log streams
   - `logs:PutLogEvents` - Write log events

### API Gateway Role

**Role Name:** `DocumentPolicyProcessor-ApiGateway-dev`

**Trust Policy:**
- Allows API Gateway service to assume this role

**Inline Policies:**

1. **InvokeLambda** - Lambda invocation
   - `lambda:InvokeFunction` - Invoke Lambda functions

2. **CloudWatchLogs** - API Gateway logging
   - `logs:CreateLogGroup` - Create log groups
   - `logs:CreateLogStream` - Create log streams
   - `logs:PutLogEvents` - Write log events

## Verification

After deployment, verify the roles were created:

```bash
# List roles
aws iam list-roles --query 'Roles[?contains(RoleName, `DocumentPolicyProcessor`)].RoleName'

# Get Lambda role details
aws iam get-role --role-name DocumentPolicyProcessor-Lambda-dev

# List Lambda role policies
aws iam list-role-policies --role-name DocumentPolicyProcessor-Lambda-dev

# Get API Gateway role details
aws iam get-role --role-name DocumentPolicyProcessor-ApiGateway-dev

# List API Gateway role policies
aws iam list-role-policies --role-name DocumentPolicyProcessor-ApiGateway-dev
```

## Using the Roles

### In Lambda Functions

When creating a Lambda function, specify the Lambda execution role ARN:

```bash
aws lambda create-function \
  --function-name DocumentPolicyProcessor-Main \
  --runtime python3.11 \
  --role arn:aws:iam::ACCOUNT_ID:role/DocumentPolicyProcessor-Lambda-dev \
  --handler lambda_function.lambda_handler \
  --zip-file fileb://function.zip
```

### In API Gateway

When configuring API Gateway integration:

1. Go to API Gateway console
2. Select your API
3. Go to Settings
4. Set CloudWatch log role ARN to the API Gateway role ARN
5. Enable CloudWatch Logs

Or via CLI:

```bash
aws apigateway update-account \
  --patch-operations op=replace,path=/cloudwatchRoleArn,value=arn:aws:iam::ACCOUNT_ID:role/DocumentPolicyProcessor-ApiGateway-dev
```

## Security Best Practices

### Least Privilege

The roles follow the principle of least privilege:
- Only necessary permissions are granted
- Resources are scoped to specific tables and buckets
- Wildcards are used only where necessary (e.g., Textract)

### Resource Scoping

Permissions are scoped to specific resources:
- S3: Only the document-policy-processor-uploads bucket
- DynamoDB: Only the Policies and ProcessingJobs tables
- Lambda: Only functions with DocumentPolicyProcessor prefix
- CloudWatch: Only log groups with specific prefixes

### Environment Separation

Use different role names for different environments:
- Development: `DocumentPolicyProcessor-Lambda-dev`
- Production: `DocumentPolicyProcessor-Lambda-prod`

Update the `ENVIRONMENT` variable in the scripts or CloudFormation parameters.

### Monitoring

Enable CloudTrail to monitor IAM role usage:

```bash
aws cloudtrail lookup-events \
  --lookup-attributes AttributeKey=ResourceName,AttributeValue=DocumentPolicyProcessor-Lambda-dev \
  --max-results 10
```

## Troubleshooting

### Role Already Exists

If you see "EntityAlreadyExists" error:
- The role was created previously
- Use CloudFormation update-stack instead of create-stack
- Or delete the existing role first (if safe to do so)

### Permission Denied

If you get permission denied errors:
- Ensure your AWS credentials have IAM permissions
- Required permissions: `iam:CreateRole`, `iam:PutRolePolicy`, `iam:AttachRolePolicy`
- Check your IAM user/role has these permissions

### IAM Changes Not Taking Effect

IAM changes can take a few seconds to propagate:
- Wait 10-30 seconds after creating roles
- If Lambda still can't access resources, check:
  - Role ARN is correct
  - Policies are attached
  - Resource names match (bucket name, table names)

### Textract Access Denied

If Textract operations fail:
- Verify Textract is available in your region
- Check the Lambda role has TextractAccess policy
- Ensure the document is in a supported format

### DynamoDB Access Denied

If DynamoDB operations fail:
- Verify table names match exactly
- Check the region matches
- Ensure tables exist before testing

## Cost Considerations

IAM roles themselves are free, but the services they grant access to have costs:

- **Textract**: $1.50 per 1,000 pages (DetectDocumentText)
- **Lambda**: Free tier includes 1M requests/month
- **DynamoDB**: Free tier includes 25 GB storage
- **S3**: Free tier includes 5 GB storage
- **CloudWatch Logs**: $0.50 per GB ingested

For the hackathon MVP with limited testing, costs should be minimal (under $5).

## Next Steps

After setting up IAM roles:

1. ✅ IAM roles created
2. → Create Lambda function (task 2.4)
3. → Set up API Gateway (task 2.5)
4. → Test end-to-end permissions
5. → Deploy document processing logic

## Resources

- [AWS IAM Roles Documentation](https://docs.aws.amazon.com/IAM/latest/UserGuide/id_roles.html)
- [Lambda Execution Role](https://docs.aws.amazon.com/lambda/latest/dg/lambda-intro-execution-role.html)
- [API Gateway Permissions](https://docs.aws.amazon.com/apigateway/latest/developerguide/permissions.html)
- [IAM Best Practices](https://docs.aws.amazon.com/IAM/latest/UserGuide/best-practices.html)
- [AWS Textract Permissions](https://docs.aws.amazon.com/textract/latest/dg/security-iam.html)

## Support

If you encounter issues:
1. Check the troubleshooting section above
2. Review CloudWatch logs for error messages
3. Verify AWS credentials and permissions
4. Check AWS service quotas and limits
