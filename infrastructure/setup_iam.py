#!/usr/bin/env python3
"""
IAM Roles Setup Script for Document Policy Processor

This script creates IAM roles for Lambda and API Gateway using boto3.
It provides the same functionality as the CloudFormation template but
with more flexibility and immediate feedback.
"""

import boto3
import json
import sys
from botocore.exceptions import ClientError

# Configuration
ENVIRONMENT = 'dev'
S3_BUCKET_NAME = 'document-policy-processor-uploads'
LAMBDA_ROLE_NAME = f'DocumentPolicyProcessor-Lambda-{ENVIRONMENT}'
API_GATEWAY_ROLE_NAME = f'DocumentPolicyProcessor-ApiGateway-{ENVIRONMENT}'

# Initialize boto3 clients
iam_client = boto3.client('iam')
sts_client = boto3.client('sts')

def get_account_id():
    """Get AWS account ID"""
    try:
        return sts_client.get_caller_identity()['Account']
    except ClientError as e:
        print(f"❌ Error getting account ID: {e}")
        sys.exit(1)

def get_region():
    """Get AWS region"""
    session = boto3.session.Session()
    return session.region_name or 'us-east-1'

def create_lambda_execution_role(account_id, region):
    """Create Lambda execution role with necessary permissions"""
    print(f"\n📋 Creating Lambda execution role: {LAMBDA_ROLE_NAME}")
    
    # Trust policy for Lambda
    trust_policy = {
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
    
    # Create role
    try:
        response = iam_client.create_role(
            RoleName=LAMBDA_ROLE_NAME,
            AssumeRolePolicyDocument=json.dumps(trust_policy),
            Description='Execution role for Document Policy Processor Lambda functions',
            Tags=[
                {'Key': 'Project', 'Value': 'DocumentPolicyProcessor'},
                {'Key': 'Environment', 'Value': ENVIRONMENT}
            ]
        )
        print(f"✅ Created role: {response['Role']['Arn']}")
    except ClientError as e:
        if e.response['Error']['Code'] == 'EntityAlreadyExists':
            print(f"⚠️  Role already exists: {LAMBDA_ROLE_NAME}")
            response = iam_client.get_role(RoleName=LAMBDA_ROLE_NAME)
        else:
            print(f"❌ Error creating role: {e}")
            sys.exit(1)
    
    # Attach AWS managed policy for basic Lambda execution
    print("📎 Attaching AWSLambdaBasicExecutionRole managed policy...")
    try:
        iam_client.attach_role_policy(
            RoleName=LAMBDA_ROLE_NAME,
            PolicyArn='arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole'
        )
        print("✅ Attached AWSLambdaBasicExecutionRole")
    except ClientError as e:
        if e.response['Error']['Code'] == 'EntityAlreadyExists':
            print("⚠️  Policy already attached")
        else:
            print(f"❌ Error attaching policy: {e}")
    
    # S3 Access Policy
    s3_policy = {
        "Version": "2012-10-17",
        "Statement": [
            {
                "Effect": "Allow",
                "Action": [
                    "s3:GetObject",
                    "s3:PutObject",
                    "s3:DeleteObject",
                    "s3:ListBucket"
                ],
                "Resource": [
                    f"arn:aws:s3:::{S3_BUCKET_NAME}",
                    f"arn:aws:s3:::{S3_BUCKET_NAME}/*"
                ]
            }
        ]
    }
    
    print("📎 Creating S3 access policy...")
    try:
        iam_client.put_role_policy(
            RoleName=LAMBDA_ROLE_NAME,
            PolicyName='S3Access',
            PolicyDocument=json.dumps(s3_policy)
        )
        print("✅ Created S3 access policy")
    except ClientError as e:
        print(f"❌ Error creating S3 policy: {e}")
    
    # DynamoDB Access Policy
    dynamodb_policy = {
        "Version": "2012-10-17",
        "Statement": [
            {
                "Effect": "Allow",
                "Action": [
                    "dynamodb:GetItem",
                    "dynamodb:PutItem",
                    "dynamodb:UpdateItem",
                    "dynamodb:Query",
                    "dynamodb:Scan",
                    "dynamodb:BatchGetItem",
                    "dynamodb:BatchWriteItem"
                ],
                "Resource": [
                    f"arn:aws:dynamodb:{region}:{account_id}:table/DocumentPolicyProcessor-Policies",
                    f"arn:aws:dynamodb:{region}:{account_id}:table/DocumentPolicyProcessor-ProcessingJobs"
                ]
            }
        ]
    }
    
    print("📎 Creating DynamoDB access policy...")
    try:
        iam_client.put_role_policy(
            RoleName=LAMBDA_ROLE_NAME,
            PolicyName='DynamoDBAccess',
            PolicyDocument=json.dumps(dynamodb_policy)
        )
        print("✅ Created DynamoDB access policy")
    except ClientError as e:
        print(f"❌ Error creating DynamoDB policy: {e}")
    
    # Textract Access Policy
    textract_policy = {
        "Version": "2012-10-17",
        "Statement": [
            {
                "Effect": "Allow",
                "Action": [
                    "textract:DetectDocumentText",
                    "textract:AnalyzeDocument",
                    "textract:StartDocumentTextDetection",
                    "textract:GetDocumentTextDetection"
                ],
                "Resource": "*"
            }
        ]
    }
    
    print("📎 Creating Textract access policy...")
    try:
        iam_client.put_role_policy(
            RoleName=LAMBDA_ROLE_NAME,
            PolicyName='TextractAccess',
            PolicyDocument=json.dumps(textract_policy)
        )
        print("✅ Created Textract access policy")
    except ClientError as e:
        print(f"❌ Error creating Textract policy: {e}")
    
    # CloudWatch Logs Policy
    cloudwatch_policy = {
        "Version": "2012-10-17",
        "Statement": [
            {
                "Effect": "Allow",
                "Action": [
                    "logs:CreateLogGroup",
                    "logs:CreateLogStream",
                    "logs:PutLogEvents"
                ],
                "Resource": f"arn:aws:logs:{region}:{account_id}:log-group:/aws/lambda/DocumentPolicyProcessor-*"
            }
        ]
    }
    
    print("📎 Creating CloudWatch Logs policy...")
    try:
        iam_client.put_role_policy(
            RoleName=LAMBDA_ROLE_NAME,
            PolicyName='CloudWatchLogs',
            PolicyDocument=json.dumps(cloudwatch_policy)
        )
        print("✅ Created CloudWatch Logs policy")
    except ClientError as e:
        print(f"❌ Error creating CloudWatch policy: {e}")
    
    return response['Role']['Arn']

def create_api_gateway_role(account_id, region):
    """Create API Gateway role with Lambda invocation permissions"""
    print(f"\n📋 Creating API Gateway role: {API_GATEWAY_ROLE_NAME}")
    
    # Trust policy for API Gateway
    trust_policy = {
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
    
    # Create role
    try:
        response = iam_client.create_role(
            RoleName=API_GATEWAY_ROLE_NAME,
            AssumeRolePolicyDocument=json.dumps(trust_policy),
            Description='Role for API Gateway to invoke Lambda functions',
            Tags=[
                {'Key': 'Project', 'Value': 'DocumentPolicyProcessor'},
                {'Key': 'Environment', 'Value': ENVIRONMENT}
            ]
        )
        print(f"✅ Created role: {response['Role']['Arn']}")
    except ClientError as e:
        if e.response['Error']['Code'] == 'EntityAlreadyExists':
            print(f"⚠️  Role already exists: {API_GATEWAY_ROLE_NAME}")
            response = iam_client.get_role(RoleName=API_GATEWAY_ROLE_NAME)
        else:
            print(f"❌ Error creating role: {e}")
            sys.exit(1)
    
    # Lambda Invocation Policy
    lambda_policy = {
        "Version": "2012-10-17",
        "Statement": [
            {
                "Effect": "Allow",
                "Action": "lambda:InvokeFunction",
                "Resource": f"arn:aws:lambda:{region}:{account_id}:function:DocumentPolicyProcessor-*"
            }
        ]
    }
    
    print("📎 Creating Lambda invocation policy...")
    try:
        iam_client.put_role_policy(
            RoleName=API_GATEWAY_ROLE_NAME,
            PolicyName='InvokeLambda',
            PolicyDocument=json.dumps(lambda_policy)
        )
        print("✅ Created Lambda invocation policy")
    except ClientError as e:
        print(f"❌ Error creating Lambda policy: {e}")
    
    # CloudWatch Logs Policy
    cloudwatch_policy = {
        "Version": "2012-10-17",
        "Statement": [
            {
                "Effect": "Allow",
                "Action": [
                    "logs:CreateLogGroup",
                    "logs:CreateLogStream",
                    "logs:PutLogEvents"
                ],
                "Resource": f"arn:aws:logs:{region}:{account_id}:log-group:/aws/apigateway/DocumentPolicyProcessor-*"
            }
        ]
    }
    
    print("📎 Creating CloudWatch Logs policy...")
    try:
        iam_client.put_role_policy(
            RoleName=API_GATEWAY_ROLE_NAME,
            PolicyName='CloudWatchLogs',
            PolicyDocument=json.dumps(cloudwatch_policy)
        )
        print("✅ Created CloudWatch Logs policy")
    except ClientError as e:
        print(f"❌ Error creating CloudWatch policy: {e}")
    
    return response['Role']['Arn']

def verify_roles():
    """Verify that roles were created successfully"""
    print("\n🔍 Verifying IAM roles...")
    
    try:
        # Check Lambda role
        lambda_role = iam_client.get_role(RoleName=LAMBDA_ROLE_NAME)
        print(f"✅ Lambda role exists: {lambda_role['Role']['Arn']}")
        
        # List attached policies
        policies = iam_client.list_attached_role_policies(RoleName=LAMBDA_ROLE_NAME)
        print(f"   Managed policies: {len(policies['AttachedPolicies'])}")
        
        inline_policies = iam_client.list_role_policies(RoleName=LAMBDA_ROLE_NAME)
        print(f"   Inline policies: {len(inline_policies['PolicyNames'])}")
        
        # Check API Gateway role
        api_role = iam_client.get_role(RoleName=API_GATEWAY_ROLE_NAME)
        print(f"✅ API Gateway role exists: {api_role['Role']['Arn']}")
        
        inline_policies = iam_client.list_role_policies(RoleName=API_GATEWAY_ROLE_NAME)
        print(f"   Inline policies: {len(inline_policies['PolicyNames'])}")
        
        return True
    except ClientError as e:
        print(f"❌ Error verifying roles: {e}")
        return False

def main():
    """Main execution function"""
    print("=" * 60)
    print("Document Policy Processor - IAM Roles Setup")
    print("=" * 60)
    
    # Get AWS account info
    account_id = get_account_id()
    region = get_region()
    print(f"\n📍 AWS Account: {account_id}")
    print(f"📍 Region: {region}")
    print(f"📍 Environment: {ENVIRONMENT}")
    
    # Create roles
    lambda_role_arn = create_lambda_execution_role(account_id, region)
    api_gateway_role_arn = create_api_gateway_role(account_id, region)
    
    # Verify setup
    if verify_roles():
        print("\n" + "=" * 60)
        print("✅ IAM Roles Setup Complete!")
        print("=" * 60)
        print(f"\nLambda Execution Role ARN:")
        print(f"  {lambda_role_arn}")
        print(f"\nAPI Gateway Role ARN:")
        print(f"  {api_gateway_role_arn}")
        print("\n💡 Next Steps:")
        print("  1. Use these role ARNs when creating Lambda functions")
        print("  2. Configure API Gateway to use the API Gateway role")
        print("  3. Test Lambda function with S3, DynamoDB, and Textract access")
        print("\n⚠️  Note: IAM changes may take a few seconds to propagate")
    else:
        print("\n❌ Setup verification failed. Please check the errors above.")
        sys.exit(1)

if __name__ == '__main__':
    main()
