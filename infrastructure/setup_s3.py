#!/usr/bin/env python3
"""
S3 Bucket Setup Script for Document Policy Processor
Creates S3 bucket with CORS configuration and folder structure
"""

import boto3
import json
from botocore.exceptions import ClientError

# Configuration
BUCKET_NAME = "document-policy-processor-uploads"
REGION = "us-east-1"  # Change as needed
FOLDERS = ["documents/", "embeddings/", "results/"]

def create_s3_bucket():
    """Create S3 bucket with appropriate configuration"""
    s3_client = boto3.client('s3', region_name=REGION)
    
    try:
        # Create bucket
        if REGION == 'us-east-1':
            s3_client.create_bucket(Bucket=BUCKET_NAME)
        else:
            s3_client.create_bucket(
                Bucket=BUCKET_NAME,
                CreateBucketConfiguration={'LocationConstraint': REGION}
            )
        print(f"✓ Created S3 bucket: {BUCKET_NAME}")
        
    except ClientError as e:
        if e.response['Error']['Code'] == 'BucketAlreadyOwnedByYou':
            print(f"✓ Bucket {BUCKET_NAME} already exists and is owned by you")
        elif e.response['Error']['Code'] == 'BucketAlreadyExists':
            print(f"✗ Bucket {BUCKET_NAME} already exists (owned by someone else)")
            raise
        else:
            print(f"✗ Error creating bucket: {e}")
            raise

def configure_cors():
    """Configure CORS for frontend access"""
    s3_client = boto3.client('s3', region_name=REGION)
    
    cors_configuration = {
        'CORSRules': [
            {
                'AllowedHeaders': ['*'],
                'AllowedMethods': ['GET', 'PUT', 'POST', 'DELETE', 'HEAD'],
                'AllowedOrigins': ['*'],  # Restrict to specific domain in production
                'ExposeHeaders': ['ETag'],
                'MaxAgeSeconds': 3000
            }
        ]
    }
    
    try:
        s3_client.put_bucket_cors(
            Bucket=BUCKET_NAME,
            CORSConfiguration=cors_configuration
        )
        print(f"✓ Configured CORS for bucket: {BUCKET_NAME}")
    except ClientError as e:
        print(f"✗ Error configuring CORS: {e}")
        raise

def create_folders():
    """Create folder structure in S3 bucket"""
    s3_client = boto3.client('s3', region_name=REGION)
    
    for folder in FOLDERS:
        try:
            # S3 doesn't have real folders, but we create empty objects with trailing /
            s3_client.put_object(
                Bucket=BUCKET_NAME,
                Key=folder,
                Body=b''
            )
            print(f"✓ Created folder: {folder}")
        except ClientError as e:
            print(f"✗ Error creating folder {folder}: {e}")
            raise

def enable_versioning():
    """Enable versioning for the bucket (optional but recommended)"""
    s3_client = boto3.client('s3', region_name=REGION)
    
    try:
        s3_client.put_bucket_versioning(
            Bucket=BUCKET_NAME,
            VersioningConfiguration={'Status': 'Enabled'}
        )
        print(f"✓ Enabled versioning for bucket: {BUCKET_NAME}")
    except ClientError as e:
        print(f"✗ Error enabling versioning: {e}")
        raise

def configure_lifecycle():
    """Configure lifecycle policy to auto-delete old files"""
    s3_client = boto3.client('s3', region_name=REGION)
    
    lifecycle_configuration = {
        'Rules': [
            {
                'ID': 'DeleteOldDocuments',
                'Status': 'Enabled',
                'Prefix': 'documents/',
                'Expiration': {'Days': 30}
            },
            {
                'ID': 'DeleteOldResults',
                'Status': 'Enabled',
                'Prefix': 'results/',
                'Expiration': {'Days': 30}
            }
        ]
    }
    
    try:
        s3_client.put_bucket_lifecycle_configuration(
            Bucket=BUCKET_NAME,
            LifecycleConfiguration=lifecycle_configuration
        )
        print(f"✓ Configured lifecycle policy for bucket: {BUCKET_NAME}")
    except ClientError as e:
        print(f"✗ Error configuring lifecycle: {e}")
        raise

def verify_setup():
    """Verify bucket setup is complete"""
    s3_client = boto3.client('s3', region_name=REGION)
    
    try:
        # Check bucket exists
        s3_client.head_bucket(Bucket=BUCKET_NAME)
        print(f"\n✓ Bucket verification successful: {BUCKET_NAME}")
        
        # List folders
        response = s3_client.list_objects_v2(Bucket=BUCKET_NAME, Delimiter='/')
        if 'CommonPrefixes' in response:
            print(f"✓ Folders created: {[p['Prefix'] for p in response['CommonPrefixes']]}")
        
        # Check CORS
        cors = s3_client.get_bucket_cors(Bucket=BUCKET_NAME)
        print(f"✓ CORS configured: {len(cors['CORSRules'])} rule(s)")
        
        return True
    except ClientError as e:
        print(f"✗ Verification failed: {e}")
        return False

def main():
    """Main setup function"""
    print("=" * 60)
    print("Document Policy Processor - S3 Bucket Setup")
    print("=" * 60)
    print(f"\nBucket Name: {BUCKET_NAME}")
    print(f"Region: {REGION}")
    print(f"Folders: {', '.join(FOLDERS)}")
    print("\nStarting setup...\n")
    
    try:
        # Step 1: Create bucket
        create_s3_bucket()
        
        # Step 2: Configure CORS
        configure_cors()
        
        # Step 3: Create folder structure
        create_folders()
        
        # Step 4: Enable versioning (optional)
        enable_versioning()
        
        # Step 5: Configure lifecycle policy (optional)
        configure_lifecycle()
        
        # Step 6: Verify setup
        if verify_setup():
            print("\n" + "=" * 60)
            print("✓ S3 bucket setup completed successfully!")
            print("=" * 60)
            print(f"\nBucket URL: https://{BUCKET_NAME}.s3.{REGION}.amazonaws.com")
            print(f"Console URL: https://s3.console.aws.amazon.com/s3/buckets/{BUCKET_NAME}")
        else:
            print("\n✗ Setup completed with errors. Please check the logs above.")
            
    except Exception as e:
        print(f"\n✗ Setup failed: {e}")
        print("\nPlease ensure:")
        print("1. AWS credentials are configured (aws configure)")
        print("2. You have permissions to create S3 buckets")
        print("3. The bucket name is globally unique")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())
