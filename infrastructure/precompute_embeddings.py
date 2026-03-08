#!/usr/bin/env python3
"""
Pre-compute Policy Embeddings Script

This script generates embeddings for all sample policies in the DynamoDB table
and stores them in S3 for fast retrieval during document processing.

Usage:
    python precompute_embeddings.py [--region REGION] [--bucket BUCKET] [--table TABLE]
"""

import boto3
import json
import numpy as np
import argparse
import sys
from typing import Dict, List, Tuple
from sentence_transformers import SentenceTransformer
from botocore.exceptions import ClientError

# Default configuration
DEFAULT_REGION = "us-east-1"
DEFAULT_BUCKET = "document-policy-processor-uploads"
DEFAULT_TABLE = "DocumentPolicyProcessor-Policies"
DEFAULT_MODEL = "all-MiniLM-L6-v2"
EMBEDDINGS_KEY = "embeddings/policy_embeddings.json"
METADATA_KEY = "embeddings/policy_metadata.json"


class EmbeddingGenerator:
    """Handles generation and storage of policy embeddings"""
    
    def __init__(self, model_name: str = DEFAULT_MODEL):
        """
        Initialize the embedding generator.
        
        Args:
            model_name: Name of the sentence-transformers model to use
        """
        print(f"Loading embedding model: {model_name}...")
        self.model = SentenceTransformer(model_name)
        self.model_name = model_name
        print(f"✓ Model loaded successfully")
    
    def generate_embedding(self, text: str) -> np.ndarray:
        """
        Generate embedding vector for input text.
        
        Args:
            text: Input text to generate embedding for
            
        Returns:
            numpy array containing the embedding vector
        """
        if not text or not text.strip():
            raise ValueError("Input text cannot be empty")
        
        embedding = self.model.encode(text, convert_to_numpy=True)
        return embedding


def fetch_policies_from_dynamodb(
    dynamodb_client, 
    table_name: str
) -> List[Dict]:
    """
    Fetch all policies from DynamoDB table.
    
    Args:
        dynamodb_client: Boto3 DynamoDB client
        table_name: Name of the DynamoDB table
        
    Returns:
        List of policy dictionaries
    """
    print(f"\nFetching policies from DynamoDB table: {table_name}...")
    
    try:
        policies = []
        
        # Scan the table to get all policies
        response = dynamodb_client.scan(TableName=table_name)
        
        # Process items
        for item in response.get('Items', []):
            policy = {
                'policy_id': item['policy_id']['S'],
                'policy_name': item['policy_name']['S'],
                'policy_text': item['policy_text']['S'],
                'category': item['category']['S'],
                'coverage_details': json.loads(item['coverage_details']['S']),
                'exclusions': json.loads(item['exclusions']['S']),
                'created_at': item['created_at']['S']
            }
            policies.append(policy)
        
        # Handle pagination if there are more items
        while 'LastEvaluatedKey' in response:
            response = dynamodb_client.scan(
                TableName=table_name,
                ExclusiveStartKey=response['LastEvaluatedKey']
            )
            for item in response.get('Items', []):
                policy = {
                    'policy_id': item['policy_id']['S'],
                    'policy_name': item['policy_name']['S'],
                    'policy_text': item['policy_text']['S'],
                    'category': item['category']['S'],
                    'coverage_details': json.loads(item['coverage_details']['S']),
                    'exclusions': json.loads(item['exclusions']['S']),
                    'created_at': item['created_at']['S']
                }
                policies.append(policy)
        
        print(f"✓ Fetched {len(policies)} policies from DynamoDB")
        return policies
        
    except ClientError as e:
        print(f"✗ Error fetching policies from DynamoDB: {e}")
        raise


def generate_policy_embeddings(
    generator: EmbeddingGenerator,
    policies: List[Dict]
) -> Tuple[Dict[str, List[float]], Dict[str, Dict]]:
    """
    Generate embeddings for all policies.
    
    Args:
        generator: EmbeddingGenerator instance
        policies: List of policy dictionaries
        
    Returns:
        Tuple of (embeddings_dict, metadata_dict)
        - embeddings_dict: Maps policy_id to embedding vector (as list)
        - metadata_dict: Maps policy_id to policy metadata
    """
    print(f"\nGenerating embeddings for {len(policies)} policies...")
    
    embeddings = {}
    metadata = {}
    
    for i, policy in enumerate(policies, 1):
        policy_id = policy['policy_id']
        policy_text = policy['policy_text']
        
        try:
            # Generate embedding
            embedding = generator.generate_embedding(policy_text)
            
            # Convert numpy array to list for JSON serialization
            embeddings[policy_id] = embedding.tolist()
            
            # Store metadata
            metadata[policy_id] = {
                'policy_id': policy_id,
                'policy_name': policy['policy_name'],
                'policy_text': policy_text,
                'category': policy['category'],
                'coverage_details': policy['coverage_details'],
                'exclusions': policy['exclusions'],
                'created_at': policy['created_at']
            }
            
            print(f"  [{i}/{len(policies)}] ✓ {policy_id}: {policy['policy_name']}")
            
        except Exception as e:
            print(f"  [{i}/{len(policies)}] ✗ Error processing {policy_id}: {e}")
            continue
    
    print(f"\n✓ Generated {len(embeddings)} embeddings successfully")
    return embeddings, metadata


def upload_to_s3(
    s3_client,
    bucket_name: str,
    embeddings: Dict[str, List[float]],
    metadata: Dict[str, Dict],
    model_name: str
) -> bool:
    """
    Upload embeddings and metadata to S3.
    
    Args:
        s3_client: Boto3 S3 client
        bucket_name: Name of the S3 bucket
        embeddings: Dictionary mapping policy_id to embedding vector
        metadata: Dictionary mapping policy_id to policy metadata
        model_name: Name of the embedding model used
        
    Returns:
        True if upload successful, False otherwise
    """
    print(f"\nUploading embeddings to S3 bucket: {bucket_name}...")
    
    try:
        # Add model information to metadata
        embeddings_data = {
            'model_name': model_name,
            'embedding_dimension': len(next(iter(embeddings.values()))),
            'num_policies': len(embeddings),
            'embeddings': embeddings
        }
        
        # Upload embeddings
        embeddings_json = json.dumps(embeddings)
        s3_client.put_object(
            Bucket=bucket_name,
            Key=EMBEDDINGS_KEY,
            Body=embeddings_json.encode('utf-8'),
            ContentType='application/json'
        )
        print(f"  ✓ Uploaded embeddings to s3://{bucket_name}/{EMBEDDINGS_KEY}")
        
        # Upload metadata
        metadata_json = json.dumps(metadata, indent=2)
        s3_client.put_object(
            Bucket=bucket_name,
            Key=METADATA_KEY,
            Body=metadata_json.encode('utf-8'),
            ContentType='application/json'
        )
        print(f"  ✓ Uploaded metadata to s3://{bucket_name}/{METADATA_KEY}")
        
        # Upload embeddings info file
        info_data = {
            'model_name': model_name,
            'embedding_dimension': len(next(iter(embeddings.values()))),
            'num_policies': len(embeddings),
            'policy_ids': list(embeddings.keys()),
            'generated_at': metadata[list(metadata.keys())[0]]['created_at']
        }
        info_json = json.dumps(info_data, indent=2)
        s3_client.put_object(
            Bucket=bucket_name,
            Key='embeddings/embeddings_info.json',
            Body=info_json.encode('utf-8'),
            ContentType='application/json'
        )
        print(f"  ✓ Uploaded info to s3://{bucket_name}/embeddings/embeddings_info.json")
        
        return True
        
    except ClientError as e:
        print(f"✗ Error uploading to S3: {e}")
        return False


def verify_embeddings(
    s3_client,
    bucket_name: str
) -> bool:
    """
    Verify that embeddings were uploaded correctly.
    
    Args:
        s3_client: Boto3 S3 client
        bucket_name: Name of the S3 bucket
        
    Returns:
        True if verification successful, False otherwise
    """
    print(f"\nVerifying embeddings in S3...")
    
    try:
        # Check embeddings file
        embeddings_obj = s3_client.get_object(
            Bucket=bucket_name,
            Key=EMBEDDINGS_KEY
        )
        embeddings_data = json.loads(embeddings_obj['Body'].read().decode('utf-8'))
        print(f"  ✓ Embeddings file exists: {len(embeddings_data)} policies")
        
        # Check metadata file
        metadata_obj = s3_client.get_object(
            Bucket=bucket_name,
            Key=METADATA_KEY
        )
        metadata_data = json.loads(metadata_obj['Body'].read().decode('utf-8'))
        print(f"  ✓ Metadata file exists: {len(metadata_data)} policies")
        
        # Verify consistency
        if len(embeddings_data) == len(metadata_data):
            print(f"  ✓ Embeddings and metadata are consistent")
            return True
        else:
            print(f"  ✗ Mismatch: {len(embeddings_data)} embeddings vs {len(metadata_data)} metadata entries")
            return False
        
    except ClientError as e:
        print(f"✗ Verification failed: {e}")
        return False


def main():
    """Main function"""
    parser = argparse.ArgumentParser(
        description='Pre-compute policy embeddings and upload to S3'
    )
    parser.add_argument(
        '--region',
        default=DEFAULT_REGION,
        help=f'AWS region (default: {DEFAULT_REGION})'
    )
    parser.add_argument(
        '--bucket',
        default=DEFAULT_BUCKET,
        help=f'S3 bucket name (default: {DEFAULT_BUCKET})'
    )
    parser.add_argument(
        '--table',
        default=DEFAULT_TABLE,
        help=f'DynamoDB table name (default: {DEFAULT_TABLE})'
    )
    parser.add_argument(
        '--model',
        default=DEFAULT_MODEL,
        help=f'Embedding model name (default: {DEFAULT_MODEL})'
    )
    
    args = parser.parse_args()
    
    print("=" * 70)
    print("Pre-compute Policy Embeddings")
    print("=" * 70)
    print(f"\nConfiguration:")
    print(f"  Region:        {args.region}")
    print(f"  S3 Bucket:     {args.bucket}")
    print(f"  DynamoDB Table: {args.table}")
    print(f"  Model:         {args.model}")
    print()
    
    try:
        # Initialize AWS clients
        print("Initializing AWS clients...")
        dynamodb_client = boto3.client('dynamodb', region_name=args.region)
        s3_client = boto3.client('s3', region_name=args.region)
        print("✓ AWS clients initialized")
        
        # Initialize embedding generator
        generator = EmbeddingGenerator(model_name=args.model)
        
        # Fetch policies from DynamoDB
        policies = fetch_policies_from_dynamodb(dynamodb_client, args.table)
        
        if not policies:
            print("\n✗ No policies found in DynamoDB table")
            print("Please run setup_dynamodb.py first to populate sample policies")
            return 1
        
        # Generate embeddings
        embeddings, metadata = generate_policy_embeddings(generator, policies)
        
        if not embeddings:
            print("\n✗ No embeddings generated")
            return 1
        
        # Upload to S3
        if not upload_to_s3(s3_client, args.bucket, embeddings, metadata, args.model):
            print("\n✗ Failed to upload embeddings to S3")
            return 1
        
        # Verify upload
        if not verify_embeddings(s3_client, args.bucket):
            print("\n⚠ Warning: Verification failed, but files may still be usable")
        
        # Print summary
        print("\n" + "=" * 70)
        print("✓ Pre-computation Complete!")
        print("=" * 70)
        print(f"\nSummary:")
        print(f"  • Policies processed: {len(policies)}")
        print(f"  • Embeddings generated: {len(embeddings)}")
        print(f"  • Embedding dimension: {len(next(iter(embeddings.values())))}")
        print(f"  • Model used: {args.model}")
        print(f"\nFiles created in S3:")
        print(f"  • s3://{args.bucket}/{EMBEDDINGS_KEY}")
        print(f"  • s3://{args.bucket}/{METADATA_KEY}")
        print(f"  • s3://{args.bucket}/embeddings/embeddings_info.json")
        print(f"\nNext steps:")
        print(f"  1. Use PolicyMatcher.load_policy_embeddings() in your Lambda function")
        print(f"  2. Pass bucket_name='{args.bucket}' to load the embeddings")
        print(f"  3. The embeddings will be cached in Lambda memory for fast access")
        print()
        
        return 0
        
    except KeyboardInterrupt:
        print("\n\n✗ Operation cancelled by user")
        return 1
    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
