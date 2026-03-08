#!/usr/bin/env python3
"""
DynamoDB Setup Script for Document Policy Processor
Creates DynamoDB tables and populates sample policy data
"""

import boto3
import json
import sys
from datetime import datetime
from botocore.exceptions import ClientError

# Configuration
STACK_NAME = "DocumentPolicyProcessor-DynamoDB"
TEMPLATE_FILE = "dynamodb-tables.yaml"
REGION = "us-east-1"

# Sample policy data
SAMPLE_POLICIES = [
    {
        "policy_id": "POL-001",
        "policy_name": "Basic Health Insurance",
        "policy_text": "Covers hospitalization, surgery, and emergency care. Includes coverage for diagnostic tests, specialist consultations, and prescription medications during hospital stay. Excludes pre-existing conditions for first 2 years, cosmetic procedures, and alternative medicine treatments.",
        "category": "health",
        "coverage_details": {
            "hospitalization": True,
            "surgery": True,
            "emergency_care": True,
            "outpatient": False,
            "dental": False,
            "vision": False
        },
        "exclusions": [
            "Pre-existing conditions (first 2 years)",
            "Cosmetic procedures",
            "Alternative medicine"
        ],
        "created_at": datetime.utcnow().isoformat()
    },
    {
        "policy_id": "POL-002",
        "policy_name": "Comprehensive Health Plus",
        "policy_text": "Covers all medical expenses including outpatient care, dental, and vision. Includes preventive care, annual health checkups, mental health services, and maternity coverage. No exclusions after 6 months waiting period. Covers pre-existing conditions after initial waiting period.",
        "category": "health",
        "coverage_details": {
            "hospitalization": True,
            "surgery": True,
            "emergency_care": True,
            "outpatient": True,
            "dental": True,
            "vision": True,
            "mental_health": True,
            "maternity": True
        },
        "exclusions": [
            "Waiting period: 6 months for pre-existing conditions"
        ],
        "created_at": datetime.utcnow().isoformat()
    },
    {
        "policy_id": "POL-003",
        "policy_name": "Critical Illness Coverage",
        "policy_text": "Provides lump sum payment upon diagnosis of critical illnesses including cancer, heart attack, stroke, kidney failure, and major organ transplant. Coverage amount: up to $100,000. Excludes illnesses diagnosed within first year of policy.",
        "category": "health",
        "coverage_details": {
            "cancer": True,
            "heart_attack": True,
            "stroke": True,
            "kidney_failure": True,
            "organ_transplant": True,
            "max_coverage": 100000
        },
        "exclusions": [
            "Illnesses diagnosed in first year",
            "Self-inflicted injuries",
            "Pre-existing critical conditions"
        ],
        "created_at": datetime.utcnow().isoformat()
    },
    {
        "policy_id": "POL-004",
        "policy_name": "Family Health Shield",
        "policy_text": "Family floater policy covering spouse and up to 3 children. Includes hospitalization, daycare procedures, ambulance charges, and home healthcare. Covers newborn from day one. Annual health checkups included for all family members.",
        "category": "health",
        "coverage_details": {
            "family_members": 5,
            "hospitalization": True,
            "daycare_procedures": True,
            "ambulance": True,
            "home_healthcare": True,
            "newborn_coverage": True,
            "annual_checkup": True
        },
        "exclusions": [
            "Adventure sports injuries",
            "War and nuclear risks"
        ],
        "created_at": datetime.utcnow().isoformat()
    },
    {
        "policy_id": "POL-005",
        "policy_name": "Senior Citizen Health Plan",
        "policy_text": "Specialized coverage for individuals aged 60 and above. Covers age-related illnesses, chronic disease management, domiciliary hospitalization, and AYUSH treatments. No medical examination required up to age 65. Includes coverage for diabetes, hypertension, and arthritis.",
        "category": "health",
        "coverage_details": {
            "age_range": "60+",
            "chronic_disease": True,
            "domiciliary_hospitalization": True,
            "ayush_treatment": True,
            "diabetes": True,
            "hypertension": True,
            "arthritis": True
        },
        "exclusions": [
            "Alzheimer's and dementia (first 3 years)",
            "Parkinson's disease (first 2 years)"
        ],
        "created_at": datetime.utcnow().isoformat()
    },
    {
        "policy_id": "POL-006",
        "policy_name": "Accident and Emergency Cover",
        "policy_text": "Covers medical expenses arising from accidents including road accidents, burns, fractures, and poisoning. Includes ambulance charges, emergency room treatment, and follow-up care. 24/7 coverage worldwide. No waiting period.",
        "category": "accident",
        "coverage_details": {
            "road_accidents": True,
            "burns": True,
            "fractures": True,
            "poisoning": True,
            "ambulance": True,
            "emergency_room": True,
            "worldwide": True
        },
        "exclusions": [
            "Intentional self-injury",
            "Injuries under influence of alcohol/drugs",
            "Adventure sports (unless rider added)"
        ],
        "created_at": datetime.utcnow().isoformat()
    },
    {
        "policy_id": "POL-007",
        "policy_name": "Maternity and Newborn Care",
        "policy_text": "Comprehensive maternity coverage including prenatal care, delivery (normal and cesarean), postnatal care, and newborn coverage for first 90 days. Includes complications during pregnancy, vaccinations, and lactation support. Waiting period: 9 months.",
        "category": "health",
        "coverage_details": {
            "prenatal_care": True,
            "normal_delivery": True,
            "cesarean_delivery": True,
            "postnatal_care": True,
            "newborn_90days": True,
            "vaccinations": True,
            "complications": True
        },
        "exclusions": [
            "Waiting period: 9 months",
            "Surrogacy",
            "Fertility treatments"
        ],
        "created_at": datetime.utcnow().isoformat()
    },
    {
        "policy_id": "POL-008",
        "policy_name": "Dental and Vision Care",
        "policy_text": "Specialized coverage for dental and vision care. Includes routine checkups, fillings, root canals, extractions, eye examinations, prescription glasses, and contact lenses. Covers cataract surgery and laser eye surgery (LASIK) with sub-limits.",
        "category": "health",
        "coverage_details": {
            "dental_checkup": True,
            "dental_procedures": True,
            "eye_examination": True,
            "prescription_glasses": True,
            "contact_lenses": True,
            "cataract_surgery": True,
            "lasik": True
        },
        "exclusions": [
            "Cosmetic dentistry",
            "Teeth whitening",
            "Cosmetic eye procedures"
        ],
        "created_at": datetime.utcnow().isoformat()
    },
    {
        "policy_id": "POL-009",
        "policy_name": "Mental Health and Wellness",
        "policy_text": "Coverage for mental health services including therapy sessions, psychiatric consultations, counseling, and hospitalization for mental health conditions. Includes coverage for depression, anxiety, PTSD, and substance abuse treatment. Telemedicine consultations included.",
        "category": "health",
        "coverage_details": {
            "therapy_sessions": True,
            "psychiatric_consultation": True,
            "counseling": True,
            "hospitalization": True,
            "depression": True,
            "anxiety": True,
            "ptsd": True,
            "substance_abuse": True,
            "telemedicine": True
        },
        "exclusions": [
            "Waiting period: 30 days",
            "Self-inflicted injuries"
        ],
        "created_at": datetime.utcnow().isoformat()
    },
    {
        "policy_id": "POL-010",
        "policy_name": "Preventive Care Plus",
        "policy_text": "Focus on preventive healthcare including annual health checkups, vaccinations, health screenings (cancer, diabetes, heart disease), nutritional counseling, and fitness program reimbursements. Includes health coaching and wellness app access.",
        "category": "health",
        "coverage_details": {
            "annual_checkup": True,
            "vaccinations": True,
            "cancer_screening": True,
            "diabetes_screening": True,
            "heart_screening": True,
            "nutritional_counseling": True,
            "fitness_reimbursement": True,
            "health_coaching": True,
            "wellness_app": True
        },
        "exclusions": [
            "Experimental treatments",
            "Non-approved supplements"
        ],
        "created_at": datetime.utcnow().isoformat()
    }
]


def create_cloudformation_stack(cf_client):
    """Create CloudFormation stack for DynamoDB tables"""
    print(f"Creating CloudFormation stack: {STACK_NAME}")
    
    try:
        # Read template file
        with open(TEMPLATE_FILE, 'r') as f:
            template_body = f.read()
        
        # Create stack
        response = cf_client.create_stack(
            StackName=STACK_NAME,
            TemplateBody=template_body,
            Capabilities=['CAPABILITY_IAM'],
            Tags=[
                {'Key': 'Project', 'Value': 'DocumentPolicyProcessor'},
                {'Key': 'Environment', 'Value': 'Development'}
            ]
        )
        
        print(f"Stack creation initiated. Stack ID: {response['StackId']}")
        
        # Wait for stack creation to complete
        print("Waiting for stack creation to complete...")
        waiter = cf_client.get_waiter('stack_create_complete')
        waiter.wait(StackName=STACK_NAME)
        
        print("✓ Stack created successfully")
        return True
        
    except ClientError as e:
        if e.response['Error']['Code'] == 'AlreadyExistsException':
            print(f"Stack {STACK_NAME} already exists. Checking status...")
            return check_stack_status(cf_client)
        else:
            print(f"✗ Error creating stack: {e}")
            return False


def check_stack_status(cf_client):
    """Check if existing stack is in a usable state"""
    try:
        response = cf_client.describe_stacks(StackName=STACK_NAME)
        stack = response['Stacks'][0]
        status = stack['StackStatus']
        
        if status in ['CREATE_COMPLETE', 'UPDATE_COMPLETE']:
            print(f"✓ Stack exists and is ready (Status: {status})")
            return True
        elif status in ['CREATE_IN_PROGRESS', 'UPDATE_IN_PROGRESS']:
            print(f"Stack is being created/updated (Status: {status}). Waiting...")
            waiter = cf_client.get_waiter('stack_create_complete')
            waiter.wait(StackName=STACK_NAME)
            print("✓ Stack is now ready")
            return True
        else:
            print(f"✗ Stack is in unusable state: {status}")
            return False
            
    except ClientError as e:
        print(f"✗ Error checking stack status: {e}")
        return False


def populate_sample_policies(dynamodb_client, table_name):
    """Populate the Policies table with sample data"""
    print(f"\nPopulating sample policies into {table_name}...")
    
    success_count = 0
    error_count = 0
    
    for policy in SAMPLE_POLICIES:
        try:
            # Convert nested dicts to JSON strings for DynamoDB
            item = {
                'policy_id': {'S': policy['policy_id']},
                'policy_name': {'S': policy['policy_name']},
                'policy_text': {'S': policy['policy_text']},
                'category': {'S': policy['category']},
                'coverage_details': {'S': json.dumps(policy['coverage_details'])},
                'exclusions': {'S': json.dumps(policy['exclusions'])},
                'created_at': {'S': policy['created_at']}
            }
            
            dynamodb_client.put_item(
                TableName=table_name,
                Item=item
            )
            
            print(f"  ✓ Added policy: {policy['policy_id']} - {policy['policy_name']}")
            success_count += 1
            
        except ClientError as e:
            print(f"  ✗ Error adding policy {policy['policy_id']}: {e}")
            error_count += 1
    
    print(f"\nSummary: {success_count} policies added successfully, {error_count} errors")
    return success_count > 0


def get_stack_outputs(cf_client):
    """Get outputs from CloudFormation stack"""
    try:
        response = cf_client.describe_stacks(StackName=STACK_NAME)
        stack = response['Stacks'][0]
        outputs = {output['OutputKey']: output['OutputValue'] 
                  for output in stack.get('Outputs', [])}
        return outputs
    except ClientError as e:
        print(f"Error getting stack outputs: {e}")
        return {}


def main():
    """Main setup function"""
    print("=" * 60)
    print("Document Policy Processor - DynamoDB Setup")
    print("=" * 60)
    print()
    
    # Initialize AWS clients
    try:
        cf_client = boto3.client('cloudformation', region_name=REGION)
        dynamodb_client = boto3.client('dynamodb', region_name=REGION)
        print(f"✓ Connected to AWS region: {REGION}")
    except Exception as e:
        print(f"✗ Error connecting to AWS: {e}")
        print("\nPlease ensure:")
        print("  1. AWS CLI is configured (run 'aws configure')")
        print("  2. You have valid AWS credentials")
        print("  3. You have necessary permissions for DynamoDB and CloudFormation")
        sys.exit(1)
    
    # Create CloudFormation stack
    if not create_cloudformation_stack(cf_client):
        print("\n✗ Failed to create/verify CloudFormation stack")
        sys.exit(1)
    
    # Get stack outputs
    outputs = get_stack_outputs(cf_client)
    policies_table = outputs.get('PoliciesTableName', 'DocumentPolicyProcessor-Policies')
    jobs_table = outputs.get('ProcessingJobsTableName', 'DocumentPolicyProcessor-ProcessingJobs')
    
    print(f"\nCreated tables:")
    print(f"  • Policies table: {policies_table}")
    print(f"  • Processing Jobs table: {jobs_table}")
    
    # Populate sample policies
    if not populate_sample_policies(dynamodb_client, policies_table):
        print("\n⚠ Warning: Failed to populate sample policies")
    
    # Print summary
    print("\n" + "=" * 60)
    print("Setup Complete!")
    print("=" * 60)
    print("\nNext steps:")
    print("  1. Use these table names in your Lambda functions:")
    print(f"     - POLICIES_TABLE={policies_table}")
    print(f"     - JOBS_TABLE={jobs_table}")
    print("  2. Ensure Lambda execution role has DynamoDB permissions")
    print("  3. Test the tables using AWS Console or CLI")
    print("\nTo verify the setup:")
    print(f"  aws dynamodb scan --table-name {policies_table} --region {REGION}")
    print()


if __name__ == "__main__":
    main()
