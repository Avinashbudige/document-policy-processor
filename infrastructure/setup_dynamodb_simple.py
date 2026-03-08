#!/usr/bin/env python3
"""
Simple DynamoDB Setup Script (No CloudFormation)
Creates DynamoDB tables directly and populates sample policy data
"""

import boto3
import json
from datetime import datetime, timezone
from botocore.exceptions import ClientError

# Configuration
REGION = "us-east-1"

# Sample policy data
SAMPLE_POLICIES = [
    {
        "policy_id": "POL-001",
        "policy_name": "Basic Health Insurance",
        "policy_text": "Covers hospitalization, surgery, and emergency care. Excludes pre-existing conditions for first 2 years.",
        "category": "health",
        "coverage_details": json.dumps({
            "hospitalization": True,
            "surgery": True,
            "emergency_care": True
        }),
        "exclusions": json.dumps([
            "Pre-existing conditions (first 2 years)",
            "Cosmetic procedures"
        ]),
        "created_at": datetime.now(timezone.utc).isoformat()
    },
    {
        "policy_id": "POL-002",
        "policy_name": "Comprehensive Health Plus",
        "policy_text": "Covers all medical expenses including outpatient care, dental, and vision. No exclusions after 6 months.",
        "category": "health",
        "coverage_details": json.dumps({
            "hospitalization": True,
            "surgery": True,
            "outpatient": True,
            "dental": True
        }),
        "exclusions": json.dumps([]),
        "created_at": datetime.now(timezone.utc).isoformat()
    },
    {
        "policy_id": "POL-003",
        "policy_name": "Diabetes Care Plan",
        "policy_text": "Specialized coverage for diabetes management including insulin, monitoring supplies, and specialist visits.",
        "category": "health",
        "coverage_details": json.dumps({
            "diabetes_supplies": True,
            "insulin": True,
            "specialist_visits": True
        }),
        "exclusions": json.dumps([]),
        "created_at": datetime.now(timezone.utc).isoformat()
    }
]

def create_policies_table(dynamodb):
    """Create Policies table"""
    try:
        table = dynamodb.create_table(
            TableName='Policies',
            KeySchema=[
                {'AttributeName': 'policy_id', 'KeyType': 'HASH'}
            ],
            AttributeDefinitions=[
                {'AttributeName': 'policy_id', 'AttributeType': 'S'},
                {'AttributeName': 'category', 'AttributeType': 'S'}
            ],
            GlobalSecondaryIndexes=[
                {
                    'IndexName': 'CategoryIndex',
                    'KeySchema': [
                        {'AttributeName': 'category', 'KeyType': 'HASH'}
                    ],
                    'Projection': {'ProjectionType': 'ALL'},
                    'ProvisionedThroughput': {
                        'ReadCapacityUnits': 5,
                        'WriteCapacityUnits': 5
                    }
                }
            ],
            BillingMode='PROVISIONED',
            ProvisionedThroughput={
                'ReadCapacityUnits': 5,
                'WriteCapacityUnits': 5
            },
            Tags=[
                {'Key': 'Project', 'Value': 'DocumentPolicyProcessor'},
                {'Key': 'Environment', 'Value': 'dev'}
            ]
        )
        
        # Wait for table to be created
        table.meta.client.get_waiter('table_exists').wait(TableName='Policies')
        print("✓ Created Policies table")
        return True
        
    except ClientError as e:
        if e.response['Error']['Code'] == 'ResourceInUseException':
            print("✓ Policies table already exists")
            return True
        else:
            print(f"✗ Error creating Policies table: {e}")
            return False

def create_processing_jobs_table(dynamodb):
    """Create ProcessingJobs table"""
    try:
        table = dynamodb.create_table(
            TableName='ProcessingJobs',
            KeySchema=[
                {'AttributeName': 'job_id', 'KeyType': 'HASH'}
            ],
            AttributeDefinitions=[
                {'AttributeName': 'job_id', 'AttributeType': 'S'}
            ],
            BillingMode='PROVISIONED',
            ProvisionedThroughput={
                'ReadCapacityUnits': 5,
                'WriteCapacityUnits': 5
            },
            Tags=[
                {'Key': 'Project', 'Value': 'DocumentPolicyProcessor'},
                {'Key': 'Environment', 'Value': 'dev'}
            ]
        )
        
        # Wait for table to be created
        table.meta.client.get_waiter('table_exists').wait(TableName='ProcessingJobs')
        
        # Enable TTL
        dynamodb.meta.client.update_time_to_live(
            TableName='ProcessingJobs',
            TimeToLiveSpecification={
                'Enabled': True,
                'AttributeName': 'ttl'
            }
        )
        
        print("✓ Created ProcessingJobs table with TTL")
        return True
        
    except ClientError as e:
        if e.response['Error']['Code'] == 'ResourceInUseException':
            print("✓ ProcessingJobs table already exists")
            return True
        else:
            print(f"✗ Error creating ProcessingJobs table: {e}")
            return False

def populate_sample_data(dynamodb):
    """Populate Policies table with sample data"""
    table = dynamodb.Table('Policies')
    
    print("\nPopulating sample policy data...")
    for policy in SAMPLE_POLICIES:
        try:
            table.put_item(Item=policy)
            print(f"✓ Added policy: {policy['policy_name']}")
        except ClientError as e:
            print(f"✗ Error adding policy {policy['policy_id']}: {e}")
            return False
    
    return True

def verify_setup(dynamodb):
    """Verify tables are created and accessible"""
    try:
        # Check Policies table
        policies_table = dynamodb.Table('Policies')
        policies_table.load()
        print(f"\n✓ Policies table status: {policies_table.table_status}")
        
        # Check ProcessingJobs table
        jobs_table = dynamodb.Table('ProcessingJobs')
        jobs_table.load()
        print(f"✓ ProcessingJobs table status: {jobs_table.table_status}")
        
        # Count policies
        response = policies_table.scan(Select='COUNT')
        print(f"✓ Total policies in database: {response['Count']}")
        
        return True
    except ClientError as e:
        print(f"✗ Verification failed: {e}")
        return False

def main():
    """Main setup function"""
    print("=" * 60)
    print("Document Policy Processor - DynamoDB Setup (Simple)")
    print("=" * 60)
    print(f"\nRegion: {REGION}")
    print("\nStarting setup...\n")
    
    try:
        # Initialize DynamoDB resource
        dynamodb = boto3.resource('dynamodb', region_name=REGION)
        
        # Step 1: Create Policies table
        if not create_policies_table(dynamodb):
            return 1
        
        # Step 2: Create ProcessingJobs table
        if not create_processing_jobs_table(dynamodb):
            return 1
        
        # Step 3: Populate sample data
        if not populate_sample_data(dynamodb):
            return 1
        
        # Step 4: Verify setup
        if verify_setup(dynamodb):
            print("\n" + "=" * 60)
            print("✓ DynamoDB setup completed successfully!")
            print("=" * 60)
            print(f"\nTables created:")
            print("  - Policies (with CategoryIndex)")
            print("  - ProcessingJobs (with TTL enabled)")
            print(f"\nConsole URL: https://console.aws.amazon.com/dynamodbv2/home?region={REGION}#tables")
        else:
            print("\n✗ Setup completed with errors")
            return 1
            
    except Exception as e:
        print(f"\n✗ Setup failed: {e}")
        print("\nPlease ensure:")
        print("1. AWS credentials are configured (aws configure)")
        print("2. You have permissions to create DynamoDB tables")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())
