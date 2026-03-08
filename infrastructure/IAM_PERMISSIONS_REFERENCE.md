# IAM Permissions Reference

Quick reference for IAM roles and permissions used by Document Policy Processor.

## Lambda Execution Role

**Role Name:** `DocumentPolicyProcessor-Lambda-dev`

**ARN Format:** `arn:aws:iam::ACCOUNT_ID:role/DocumentPolicyProcessor-Lambda-dev`

### Permissions Summary

| Service | Actions | Resources | Purpose |
|---------|---------|-----------|---------|
| **S3** | GetObject, PutObject, DeleteObject, ListBucket | `document-policy-processor-uploads` bucket | Store and retrieve documents, embeddings, and results |
| **DynamoDB** | GetItem, PutItem, UpdateItem, Query, Scan, BatchGetItem, BatchWriteItem | `DocumentPolicyProcessor-Policies`, `DocumentPolicyProcessor-ProcessingJobs` tables | Read policies and manage processing jobs |
| **Textract** | DetectDocumentText, AnalyzeDocument, StartDocumentTextDetection, GetDocumentTextDetection | All resources (*) | Extract text from documents (OCR) |
| **CloudWatch Logs** | CreateLogGroup, CreateLogStream, PutLogEvents | `/aws/lambda/DocumentPolicyProcessor-*` log groups | Write Lambda execution logs |

### Trust Relationship

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": {
        "Service": "lambda.amazonaws.com"
      },
      "Action": "sts:AssumeRole"
    }
  ]
}
```

## API Gateway Role

**Role Name:** `DocumentPolicyProcessor-ApiGateway-dev`

**ARN Format:** `arn:aws:iam::ACCOUNT_ID:role/DocumentPolicyProcessor-ApiGateway-dev`

### Permissions Summary

| Service | Actions | Resources | Purpose |
|---------|---------|-----------|---------|
| **Lambda** | InvokeFunction | `DocumentPolicyProcessor-*` functions | Invoke Lambda functions from API Gateway |
| **CloudWatch Logs** | CreateLogGroup, CreateLogStream, PutLogEvents | `/aws/apigateway/DocumentPolicyProcessor-*` log groups | Write API Gateway logs |

### Trust Relationship

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": {
        "Service": "apigateway.amazonaws.com"
      },
      "Action": "sts:AssumeRole"
    }
  ]
}
```

## Permission Scoping

### Why These Permissions?

**S3 Permissions:**
- `GetObject` - Download uploaded documents for processing
- `PutObject` - Store processing results and embeddings
- `DeleteObject` - Clean up temporary files
- `ListBucket` - List documents in folders

**DynamoDB Permissions:**
- `GetItem` - Retrieve individual policies
- `PutItem` - Create new processing jobs
- `UpdateItem` - Update job status
- `Query` - Find policies by category
- `Scan` - Load all policies for embedding
- `BatchGetItem/BatchWriteItem` - Efficient bulk operations

**Textract Permissions:**
- `DetectDocumentText` - Synchronous OCR for small documents
- `AnalyzeDocument` - Extract structured data (forms, tables)
- `StartDocumentTextDetection` - Async OCR for large documents
- `GetDocumentTextDetection` - Retrieve async OCR results

**CloudWatch Logs:**
- Required for debugging and monitoring
- Separate log groups for Lambda and API Gateway

## Security Considerations

### Least Privilege

✅ **Good:**
- Permissions scoped to specific buckets and tables
- Function names use consistent prefix for filtering
- Separate roles for Lambda and API Gateway

❌ **Avoid:**
- Using `*` for S3 bucket resources
- Granting `dynamodb:*` on all tables
- Using admin policies for convenience

### Resource Naming Convention

All resources use the `DocumentPolicyProcessor-` prefix:
- Lambda functions: `DocumentPolicyProcessor-Main`, `DocumentPolicyProcessor-TextExtractor`
- DynamoDB tables: `DocumentPolicyProcessor-Policies`, `DocumentPolicyProcessor-ProcessingJobs`
- S3 bucket: `document-policy-processor-uploads`
- Log groups: `/aws/lambda/DocumentPolicyProcessor-*`, `/aws/apigateway/DocumentPolicyProcessor-*`

This allows IAM policies to use wildcards safely.

### Environment Separation

For production, create separate roles:
- Dev: `DocumentPolicyProcessor-Lambda-dev`
- Prod: `DocumentPolicyProcessor-Lambda-prod`

Use different S3 buckets and DynamoDB tables per environment.

## Common Use Cases

### Lambda Function Accessing S3

```python
import boto3

s3 = boto3.client('s3')

# Download document
response = s3.get_object(
    Bucket='document-policy-processor-uploads',
    Key='documents/user-doc.pdf'
)
document_content = response['Body'].read()

# Upload result
s3.put_object(
    Bucket='document-policy-processor-uploads',
    Key='results/job-123.json',
    Body=json.dumps(result)
)
```

### Lambda Function Accessing DynamoDB

```python
import boto3

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('DocumentPolicyProcessor-Policies')

# Get policy
response = table.get_item(Key={'policy_id': 'POL-001'})
policy = response['Item']

# Query by category
response = table.query(
    IndexName='CategoryIndex',
    KeyConditionExpression='category = :cat',
    ExpressionAttributeValues={':cat': 'health'}
)
policies = response['Items']
```

### Lambda Function Using Textract

```python
import boto3

textract = boto3.client('textract')

# Synchronous text detection
response = textract.detect_document_text(
    Document={
        'S3Object': {
            'Bucket': 'document-policy-processor-uploads',
            'Name': 'documents/user-doc.pdf'
        }
    }
)

# Extract text
text = ' '.join([
    block['Text'] 
    for block in response['Blocks'] 
    if block['BlockType'] == 'LINE'
])
```

### API Gateway Invoking Lambda

API Gateway automatically uses the configured role to invoke Lambda functions. No code changes needed.

## Troubleshooting

### Access Denied Errors

**Error:** `AccessDenied: User: arn:aws:sts::ACCOUNT_ID:assumed-role/DocumentPolicyProcessor-Lambda-dev/function-name is not authorized to perform: s3:GetObject`

**Solution:**
1. Verify the S3 bucket name matches the policy
2. Check the object key exists
3. Ensure the role has the S3Access policy attached

**Error:** `AccessDeniedException: User is not authorized to perform: textract:DetectDocumentText`

**Solution:**
1. Verify the TextractAccess policy is attached
2. Check Textract is available in your region
3. Ensure the document format is supported

### Role Not Found

**Error:** `The role defined for the function cannot be assumed by Lambda`

**Solution:**
1. Wait 10-30 seconds for IAM propagation
2. Verify the role exists: `aws iam get-role --role-name DocumentPolicyProcessor-Lambda-dev`
3. Check the trust policy allows Lambda to assume the role

### Policy Not Attached

**Error:** Lambda function has no permissions

**Solution:**
```bash
# List attached policies
aws iam list-role-policies --role-name DocumentPolicyProcessor-Lambda-dev

# If empty, re-run setup script
python setup_iam.py
```

## Monitoring

### View Role Usage

```bash
# Get role details
aws iam get-role --role-name DocumentPolicyProcessor-Lambda-dev

# List all policies
aws iam list-role-policies --role-name DocumentPolicyProcessor-Lambda-dev

# Get specific policy
aws iam get-role-policy \
  --role-name DocumentPolicyProcessor-Lambda-dev \
  --policy-name S3Access
```

### CloudTrail Events

Monitor IAM role usage with CloudTrail:

```bash
aws cloudtrail lookup-events \
  --lookup-attributes AttributeKey=ResourceName,AttributeValue=DocumentPolicyProcessor-Lambda-dev \
  --max-results 20
```

### CloudWatch Logs

View Lambda execution logs:

```bash
aws logs tail /aws/lambda/DocumentPolicyProcessor-Main --follow
```

## Cost Impact

IAM roles are **free**. You only pay for the services they access:

- **Textract**: ~$1.50 per 1,000 pages
- **Lambda**: Free tier includes 1M requests/month
- **DynamoDB**: Free tier includes 25 GB storage
- **S3**: Free tier includes 5 GB storage
- **CloudWatch**: $0.50 per GB logs ingested

For hackathon MVP with limited testing: **< $5 total**

## Quick Commands

```bash
# Get Lambda role ARN
aws iam get-role \
  --role-name DocumentPolicyProcessor-Lambda-dev \
  --query 'Role.Arn' \
  --output text

# Get API Gateway role ARN
aws iam get-role \
  --role-name DocumentPolicyProcessor-ApiGateway-dev \
  --query 'Role.Arn' \
  --output text

# Test role can be assumed
aws sts assume-role \
  --role-arn arn:aws:iam::ACCOUNT_ID:role/DocumentPolicyProcessor-Lambda-dev \
  --role-session-name test-session

# Delete roles (cleanup)
aws iam delete-role-policy --role-name DocumentPolicyProcessor-Lambda-dev --policy-name S3Access
aws iam delete-role-policy --role-name DocumentPolicyProcessor-Lambda-dev --policy-name DynamoDBAccess
aws iam delete-role-policy --role-name DocumentPolicyProcessor-Lambda-dev --policy-name TextractAccess
aws iam delete-role-policy --role-name DocumentPolicyProcessor-Lambda-dev --policy-name CloudWatchLogs
aws iam detach-role-policy --role-name DocumentPolicyProcessor-Lambda-dev --policy-arn arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole
aws iam delete-role --role-name DocumentPolicyProcessor-Lambda-dev

aws iam delete-role-policy --role-name DocumentPolicyProcessor-ApiGateway-dev --policy-name InvokeLambda
aws iam delete-role-policy --role-name DocumentPolicyProcessor-ApiGateway-dev --policy-name CloudWatchLogs
aws iam delete-role --role-name DocumentPolicyProcessor-ApiGateway-dev
```

## References

- [AWS IAM Roles](https://docs.aws.amazon.com/IAM/latest/UserGuide/id_roles.html)
- [Lambda Execution Role](https://docs.aws.amazon.com/lambda/latest/dg/lambda-intro-execution-role.html)
- [Textract Permissions](https://docs.aws.amazon.com/textract/latest/dg/security-iam.html)
- [DynamoDB Permissions](https://docs.aws.amazon.com/amazondynamodb/latest/developerguide/security-iam.html)
- [S3 Permissions](https://docs.aws.amazon.com/AmazonS3/latest/userguide/s3-access-control.html)
