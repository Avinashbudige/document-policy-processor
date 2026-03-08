# DynamoDB Setup Guide

This guide explains how to set up the DynamoDB tables for the Document Policy Processor.

## Overview

The Document Policy Processor uses two DynamoDB tables:

1. **Policies Table**: Stores insurance policy information
   - Partition Key: `policy_id` (String)
   - Contains 10 sample policies covering various health insurance scenarios

2. **ProcessingJobs Table**: Tracks document processing jobs
   - Partition Key: `job_id` (String)
   - TTL enabled for automatic cleanup after 7 days

## Prerequisites

Before running the setup, ensure you have:

1. **AWS Account**: Active AWS account with appropriate permissions
2. **AWS CLI**: Installed and configured
   - Install: https://aws.amazon.com/cli/
   - Configure: Run `aws configure` and provide your credentials
3. **Python 3**: Python 3.7 or higher installed
4. **Boto3**: AWS SDK for Python (installed automatically by deployment script)

## Quick Start

### Option 1: Automated Deployment (Recommended)

**On Linux/Mac:**
```bash
cd document-policy-processor/infrastructure
chmod +x deploy-dynamodb.sh
./deploy-dynamodb.sh
```

**On Windows:**
```cmd
cd document-policy-processor\infrastructure
deploy-dynamodb.bat
```

The script will:
- Check prerequisites
- Install required Python packages
- Create CloudFormation stack with DynamoDB tables
- Populate the Policies table with 10 sample policies
- Display table names and next steps

### Option 2: Manual Deployment

If you prefer manual control:

```bash
# 1. Install dependencies
pip install boto3

# 2. Deploy CloudFormation stack
aws cloudformation create-stack \
  --stack-name DocumentPolicyProcessor-DynamoDB \
  --template-body file://dynamodb-tables.yaml \
  --region us-east-1

# 3. Wait for stack creation
aws cloudformation wait stack-create-complete \
  --stack-name DocumentPolicyProcessor-DynamoDB \
  --region us-east-1

# 4. Run Python script to populate sample data
python3 setup_dynamodb.py
```

## Table Schemas

### Policies Table

```json
{
  "policy_id": "POL-001",
  "policy_name": "Basic Health Insurance",
  "policy_text": "Full policy description...",
  "category": "health",
  "coverage_details": "{...}",
  "exclusions": "[...]",
  "created_at": "2026-01-24T00:00:00Z"
}
```

**Fields:**
- `policy_id` (String, Primary Key): Unique policy identifier
- `policy_name` (String): Human-readable policy name
- `policy_text` (String): Full policy description for semantic matching
- `category` (String): Policy category (health, accident, etc.)
- `coverage_details` (String): JSON string of coverage details
- `exclusions` (String): JSON array of exclusions
- `created_at` (String): ISO 8601 timestamp

### ProcessingJobs Table

```json
{
  "job_id": "uuid-string",
  "status": "processing",
  "document_url": "s3://bucket/key",
  "symptoms": "User-provided symptoms",
  "results": {...},
  "created_at": "2026-01-24T00:00:00Z",
  "ttl": 1234567890
}
```

**Fields:**
- `job_id` (String, Primary Key): Unique job identifier
- `status` (String): Job status (queued, processing, completed, failed)
- `document_url` (String): S3 URL of uploaded document
- `symptoms` (String): User-provided symptom description
- `results` (Map): Processing results and recommendations
- `created_at` (String): ISO 8601 timestamp
- `ttl` (Number): Unix timestamp for automatic deletion (7 days)

## Sample Policies

The setup script populates 10 sample policies:

1. **POL-001**: Basic Health Insurance - Hospitalization and emergency care
2. **POL-002**: Comprehensive Health Plus - Full coverage including outpatient
3. **POL-003**: Critical Illness Coverage - Lump sum for critical diagnoses
4. **POL-004**: Family Health Shield - Family floater policy
5. **POL-005**: Senior Citizen Health Plan - Age 60+ specialized coverage
6. **POL-006**: Accident and Emergency Cover - Accident-specific coverage
7. **POL-007**: Maternity and Newborn Care - Pregnancy and childbirth
8. **POL-008**: Dental and Vision Care - Specialized dental/vision coverage
9. **POL-009**: Mental Health and Wellness - Mental health services
10. **POL-010**: Preventive Care Plus - Preventive healthcare focus

## Verification

After deployment, verify the setup:

### Check Stack Status
```bash
aws cloudformation describe-stacks \
  --stack-name DocumentPolicyProcessor-DynamoDB \
  --region us-east-1
```

### List Tables
```bash
aws dynamodb list-tables --region us-east-1
```

### Scan Policies Table
```bash
aws dynamodb scan \
  --table-name DocumentPolicyProcessor-Policies \
  --region us-east-1
```

### Get Specific Policy
```bash
aws dynamodb get-item \
  --table-name DocumentPolicyProcessor-Policies \
  --key '{"policy_id": {"S": "POL-001"}}' \
  --region us-east-1
```

## Configuration for Lambda Functions

Use these environment variables in your Lambda functions:

```bash
POLICIES_TABLE=DocumentPolicyProcessor-Policies
JOBS_TABLE=DocumentPolicyProcessor-ProcessingJobs
AWS_REGION=us-east-1
```

## IAM Permissions

Your Lambda execution role needs these DynamoDB permissions:

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "dynamodb:GetItem",
        "dynamodb:PutItem",
        "dynamodb:UpdateItem",
        "dynamodb:Query",
        "dynamodb:Scan"
      ],
      "Resource": [
        "arn:aws:dynamodb:us-east-1:*:table/DocumentPolicyProcessor-Policies",
        "arn:aws:dynamodb:us-east-1:*:table/DocumentPolicyProcessor-ProcessingJobs"
      ]
    }
  ]
}
```

## Cost Considerations

- **Billing Mode**: PAY_PER_REQUEST (on-demand)
- **Cost**: Only pay for actual read/write requests
- **Estimated Cost**: ~$0.25 per million read requests, ~$1.25 per million write requests
- **Free Tier**: 25 GB storage, 25 read/write capacity units

For a hackathon/demo project, costs should be minimal (< $1/month).

## Cleanup

To delete the tables and avoid charges:

```bash
aws cloudformation delete-stack \
  --stack-name DocumentPolicyProcessor-DynamoDB \
  --region us-east-1
```

## Troubleshooting

### Error: "Stack already exists"
The stack is already deployed. Check its status:
```bash
aws cloudformation describe-stacks \
  --stack-name DocumentPolicyProcessor-DynamoDB
```

### Error: "Credentials not configured"
Run `aws configure` and provide:
- AWS Access Key ID
- AWS Secret Access Key
- Default region (us-east-1)
- Default output format (json)

### Error: "Access Denied"
Ensure your IAM user/role has permissions for:
- CloudFormation (CreateStack, DescribeStacks)
- DynamoDB (CreateTable, PutItem, DescribeTable)

### Tables created but no sample data
Run the population script manually:
```bash
python3 setup_dynamodb.py
```

## Next Steps

After setting up DynamoDB:

1. ✓ DynamoDB tables created
2. → Set up Lambda functions (Task 2.3)
3. → Configure API Gateway (Task 2.4)
4. → Implement document processing logic
5. → Test end-to-end workflow

## Additional Resources

- [DynamoDB Documentation](https://docs.aws.amazon.com/dynamodb/)
- [CloudFormation DynamoDB Reference](https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-dynamodb-table.html)
- [Boto3 DynamoDB Guide](https://boto3.amazonaws.com/v1/documentation/api/latest/guide/dynamodb.html)
