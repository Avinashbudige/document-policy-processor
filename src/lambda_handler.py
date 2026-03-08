"""
Main Lambda Handler for Document Policy Processor

This module orchestrates the complete document processing pipeline:
1. Parse API Gateway event
2. Download document from S3
3. Extract text from document
4. Generate embeddings and match policies
5. Check exclusions with LLM
6. Generate recommendations
7. Store results in DynamoDB
8. Return response

Requirements: 2.2, 2.8
"""

import json
import logging
import os
import time
import uuid
from typing import Dict, Any, Optional
from pathlib import Path
import tempfile
from decimal import Decimal

import boto3
from botocore.exceptions import ClientError

# Set cache directories to /tmp (Lambda writable directory)
os.environ['TRANSFORMERS_CACHE'] = '/tmp/transformers_cache'
os.environ['HF_HOME'] = '/tmp/huggingface'
os.environ['TORCH_HOME'] = '/tmp/torch'
os.environ['SENTENCE_TRANSFORMERS_HOME'] = '/tmp/sentence_transformers'

try:
    # Try relative imports first (for package usage)
    from .text_extractor import TextExtractor
    from .policy_matcher import PolicyMatcher
    from .llm_exclusion_checker import LLMExclusionChecker
    from .recommendation_engine import RecommendationEngine
except ImportError:
    # Fall back to absolute imports (for direct execution)
    from text_extractor import TextExtractor
    from policy_matcher import PolicyMatcher
    from llm_exclusion_checker import LLMExclusionChecker
    from recommendation_engine import RecommendationEngine

# Configure logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Environment variables
S3_BUCKET_NAME = os.environ.get('S3_BUCKET_NAME', 'document-policy-processor-uploads')
DYNAMODB_TABLE_JOBS = os.environ.get('DYNAMODB_TABLE_JOBS', 'ProcessingJobs')
OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY')
MISTRAL_API_KEY = os.environ.get('MISTRAL_API_KEY')
EMBEDDING_MODEL = os.environ.get('EMBEDDING_MODEL', 'all-MiniLM-L6-v2')
LLM_MODEL = os.environ.get('LLM_MODEL', 'gpt-3.5-turbo')

# AWS clients
s3_client = boto3.client('s3')
dynamodb = boto3.resource('dynamodb')
jobs_table = dynamodb.Table(DYNAMODB_TABLE_JOBS)

# Initialize processing modules (reused across warm Lambda invocations)
text_extractor = None
policy_matcher = None
llm_checker = None
recommendation_engine = None


def lambda_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    Main Lambda handler function for document processing.
    
    Routes requests to appropriate handlers based on API Gateway path and method.
    
    Supported endpoints:
    - POST /api/upload-url: Generate presigned URL for document upload
    - POST /api/process-document: Process a document
    - GET /api/status/{jobId}: Get job status
    - GET /api/results/{jobId}: Get job results
    - GET /api/health: Health check
    
    Returns:
    {
        "statusCode": 200,
        "body": {...}
    }
    """
    try:
        # Extract HTTP method and path
        http_method = event.get('httpMethod', 'POST')
        path = event.get('path', '/api/process-document')
        
        logger.info(f"Received {http_method} request to {path}")
        
        # Route to appropriate handler
        if path == '/api/health' and http_method == 'GET':
            return handle_health_check(event, context)
        
        elif path == '/api/upload-url' and http_method == 'POST':
            return handle_generate_upload_url(event, context)
        
        elif path == '/api/process-document' and http_method == 'POST':
            return handle_process_document(event, context)
        
        elif path.startswith('/api/status/') and http_method == 'GET':
            return handle_get_status(event, context)
        
        elif path.startswith('/api/results/') and http_method == 'GET':
            return handle_get_results(event, context)
        
        else:
            return create_response(404, {
                'error': 'NOT_FOUND',
                'message': f'Endpoint not found: {http_method} {path}'
            })
    
    except Exception as e:
        logger.exception(f"Unexpected error in router: {str(e)}")
        return create_response(500, {
            'error': 'INTERNAL_ERROR',
            'message': f'An unexpected error occurred: {str(e)}'
        })


def handle_health_check(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    Handle health check endpoint.
    
    Returns:
        Health status response
    """
    return create_response(200, {
        'status': 'healthy',
        'service': 'Document Policy Processor',
        'version': '1.0.0',
        'timestamp': int(time.time())
    })


def handle_generate_upload_url(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    Handle presigned URL generation endpoint.
    
    Generates an S3 presigned URL for direct document upload from frontend.
    
    Expected request body:
    {
        "filename": "document.pdf",
        "file_type": "application/pdf"
    }
    
    Returns:
    {
        "upload_url": "https://s3.amazonaws.com/...",
        "document_url": "s3://bucket/documents/uuid/filename",
        "job_id": "generated-uuid",
        "expires_in": 3600
    }
    """
    try:
        # Parse request body
        if 'body' in event:
            if isinstance(event['body'], str):
                body = json.loads(event['body'])
            else:
                body = event['body']
        else:
            body = event
        
        # Validate required fields
        if 'filename' not in body:
            return create_response(400, {
                'error': 'MISSING_PARAMETER',
                'message': 'Missing required field: filename'
            })
        
        filename = body['filename'].strip()
        file_type = body.get('file_type', 'application/octet-stream')
        
        if not filename:
            return create_response(400, {
                'error': 'INVALID_PARAMETER',
                'message': 'filename cannot be empty'
            })
        
        # Validate file extension
        file_extension = Path(filename).suffix.lower()
        allowed_extensions = ['.pdf', '.png', '.jpg', '.jpeg', '.txt']
        
        if file_extension not in allowed_extensions:
            return create_response(400, {
                'error': 'INVALID_FILE_TYPE',
                'message': f'Unsupported file type: {file_extension}. Allowed: {", ".join(allowed_extensions)}',
                'allowed_extensions': allowed_extensions
            })
        
        # Generate unique job ID and S3 key
        import uuid
        job_id = str(uuid.uuid4())
        s3_key = f"documents/{job_id}/{filename}"
        
        # Generate presigned URL for upload (PUT)
        try:
            presigned_url = s3_client.generate_presigned_url(
                'put_object',
                Params={
                    'Bucket': S3_BUCKET_NAME,
                    'Key': s3_key,
                    'ContentType': file_type
                },
                ExpiresIn=3600  # URL expires in 1 hour
            )
            
            # Construct S3 URL for later processing
            document_url = f"s3://{S3_BUCKET_NAME}/{s3_key}"
            
            logger.info(f"Generated presigned URL for job {job_id}: {s3_key}")
            
            return create_response(200, {
                'upload_url': presigned_url,
                'document_url': document_url,
                'job_id': job_id,
                'expires_in': 3600,
                'upload_method': 'PUT'
            })
            
        except ClientError as e:
            logger.error(f"Failed to generate presigned URL: {str(e)}")
            return create_response(500, {
                'error': 'PRESIGNED_URL_ERROR',
                'message': 'Failed to generate upload URL. Please try again.'
            })
    
    except json.JSONDecodeError as e:
        return create_response(400, {
            'error': 'INVALID_JSON',
            'message': 'Request body must be valid JSON'
        })
    
    except Exception as e:
        logger.exception(f"Error in handle_generate_upload_url: {str(e)}")
        return create_response(500, {
            'error': 'INTERNAL_ERROR',
            'message': str(e)
        })


def handle_get_status(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    Handle get job status endpoint.
    
    Args:
        event: API Gateway event with jobId in path parameters
        
    Returns:
        Job status response
    """
    try:
        # Extract job ID from path parameters
        path_parameters = event.get('pathParameters', {})
        job_id = path_parameters.get('jobId')
        
        if not job_id:
            return create_response(400, {
                'error': 'MISSING_PARAMETER',
                'message': 'Missing required parameter: jobId'
            })
        
        # Query DynamoDB for job status
        try:
            response = jobs_table.get_item(Key={'job_id': job_id})
            
            if 'Item' not in response:
                return create_response(404, {
                    'error': 'JOB_NOT_FOUND',
                    'message': f'Job not found: {job_id}'
                })
            
            item = response['Item']
            
            return create_response(200, {
                'job_id': job_id,
                'status': item.get('status', 'unknown'),
                'updated_at': item.get('updated_at')
            })
            
        except ClientError as e:
            logger.error(f"DynamoDB error: {str(e)}")
            return create_response(500, {
                'error': 'DATABASE_ERROR',
                'message': 'Failed to retrieve job status'
            })
    
    except Exception as e:
        logger.exception(f"Error in handle_get_status: {str(e)}")
        return create_response(500, {
            'error': 'INTERNAL_ERROR',
            'message': str(e)
        })


def handle_get_results(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    Handle get job results endpoint.
    
    Args:
        event: API Gateway event with jobId in path parameters
        
    Returns:
        Job results response
    """
    try:
        # Extract job ID from path parameters
        path_parameters = event.get('pathParameters', {})
        job_id = path_parameters.get('jobId')
        
        if not job_id:
            return create_response(400, {
                'error': 'MISSING_PARAMETER',
                'message': 'Missing required parameter: jobId'
            })
        
        # Query DynamoDB for job results
        try:
            response = jobs_table.get_item(Key={'job_id': job_id})
            
            if 'Item' not in response:
                return create_response(404, {
                    'error': 'JOB_NOT_FOUND',
                    'message': f'Job not found: {job_id}'
                })
            
            item = response['Item']
            status = item.get('status', 'unknown')
            
            # Check if job is completed
            if status == 'processing':
                return create_response(202, {
                    'job_id': job_id,
                    'status': 'processing',
                    'message': 'Job is still processing. Please check back later.'
                })
            
            # Return results
            if 'result' in item:
                result = json.loads(item['result'])
                return create_response(200, result)
            else:
                return create_response(200, {
                    'job_id': job_id,
                    'status': status,
                    'message': 'No results available yet.'
                })
            
        except ClientError as e:
            logger.error(f"DynamoDB error: {str(e)}")
            return create_response(500, {
                'error': 'DATABASE_ERROR',
                'message': 'Failed to retrieve job results'
            })
    
    except Exception as e:
        logger.exception(f"Error in handle_get_results: {str(e)}")
        return create_response(500, {
            'error': 'INTERNAL_ERROR',
            'message': str(e)
        })


def handle_process_document(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    Handle document processing endpoint.
    
    Expected event format (API Gateway):
    {
        "body": {
            "document_url": "s3://bucket/key",
            "symptoms": "user symptom description",
            "job_id": "unique-job-id"
        }
    }
    
    Returns:
    {
        "statusCode": 200,
        "body": {
            "job_id": "unique-job-id",
            "status": "completed" | "failed",
            "recommendations": [...],
            "processing_time": 12.34,
            "error_message": "..." (if failed)
        }
    }
    """
    start_time = time.time()
    job_id = None
    
    try:
        # Parse event
        logger.info("Parsing event")
        parsed_event = parse_event(event)
        job_id = parsed_event['job_id']
        document_url = parsed_event['document_url']
        symptoms = parsed_event['symptoms']
        
        logger.info(f"Processing job {job_id} for document {document_url}")
        
        # Update job status to processing
        update_job_status(job_id, 'processing', {
            'document_url': document_url,
            'symptoms': symptoms
        })
        
        # Initialize modules (lazy initialization for cold starts)
        initialize_modules()
        
        # Download document from S3
        logger.info("Downloading document from S3")
        local_file_path = download_document_from_s3(document_url)
        
        try:
            # Extract text from document
            logger.info("Extracting text from document")
            extracted_text = extract_text(local_file_path)
            
            # Combine document text with symptoms for better matching
            combined_text = f"{extracted_text}\n\nSymptoms: {symptoms}"
            
            # Generate embedding and match policies
            logger.info("Matching policies")
            policy_matches = match_policies(combined_text)
            
            if not policy_matches:
                logger.warning("No policy matches found")
                result = {
                    'job_id': job_id,
                    'status': 'completed',
                    'recommendations': [],
                    'processing_time': time.time() - start_time,
                    'message': 'No relevant policies found for the provided document and symptoms.'
                }
                
                # Store result in DynamoDB
                store_result(job_id, result)
                
                return create_response(200, result)
            
            # Check exclusions with LLM
            logger.info(f"Checking exclusions for {len(policy_matches)} policies")
            exclusion_results = check_exclusions(extracted_text, symptoms, policy_matches)
            
            # Generate recommendations
            logger.info("Generating recommendations")
            recommendations = generate_recommendations(policy_matches, exclusion_results)
            
            # Prepare result
            processing_time = time.time() - start_time
            result = {
                'job_id': job_id,
                'status': 'completed',
                'recommendations': [format_recommendation(rec) for rec in recommendations],
                'processing_time': processing_time,
                'document_summary': extracted_text[:500] + '...' if len(extracted_text) > 500 else extracted_text
            }
            
            logger.info(
                f"Processing completed successfully in {processing_time:.2f}s "
                f"with {len(recommendations)} recommendations"
            )
            
            # Store result in DynamoDB
            store_result(job_id, result)
            
            return create_response(200, result)
            
        finally:
            # Clean up temporary file
            cleanup_temp_file(local_file_path)
    
    except ValueError as e:
        # Input validation errors
        logger.error(f"Validation error: {str(e)}")
        error_result = {
            'job_id': job_id,
            'status': 'failed',
            'error': 'VALIDATION_ERROR',
            'error_message': str(e),
            'processing_time': time.time() - start_time
        }
        
        if job_id:
            update_job_status(job_id, 'failed', error_result)
        
        return create_response(400, error_result)
    
    except FileNotFoundError as e:
        # Document not found
        logger.error(f"Document not found: {str(e)}")
        error_result = {
            'job_id': job_id,
            'status': 'failed',
            'error': 'DOCUMENT_NOT_FOUND',
            'error_message': str(e),
            'processing_time': time.time() - start_time
        }
        
        if job_id:
            update_job_status(job_id, 'failed', error_result)
        
        return create_response(404, error_result)
    
    except RuntimeError as e:
        # Processing errors (OCR, LLM, etc.)
        logger.error(f"Processing error: {str(e)}")
        error_result = {
            'job_id': job_id,
            'status': 'failed',
            'error': 'PROCESSING_ERROR',
            'error_message': str(e),
            'processing_time': time.time() - start_time
        }
        
        if job_id:
            update_job_status(job_id, 'failed', error_result)
        
        return create_response(500, error_result)
    
    except Exception as e:
        # Unexpected errors
        logger.exception(f"Unexpected error: {str(e)}")
        error_result = {
            'job_id': job_id,
            'status': 'failed',
            'error': 'INTERNAL_ERROR',
            'error_message': f"An unexpected error occurred: {str(e)}",
            'processing_time': time.time() - start_time
        }
        
        if job_id:
            update_job_status(job_id, 'failed', error_result)
        
        return create_response(500, error_result)


def parse_event(event: Dict[str, Any]) -> Dict[str, str]:
    """
    Parse API Gateway event to extract required parameters.
    
    Args:
        event: API Gateway event
        
    Returns:
        Dictionary with job_id, document_url, and symptoms
        
    Raises:
        ValueError: If required parameters are missing or invalid
    """
    # Handle both direct invocation and API Gateway format
    if 'body' in event:
        if isinstance(event['body'], str):
            body = json.loads(event['body'])
        else:
            body = event['body']
    else:
        body = event
    
    # Validate required fields
    if 'job_id' not in body:
        raise ValueError("Missing required field: job_id")
    
    if 'document_url' not in body:
        raise ValueError("Missing required field: document_url")
    
    if 'symptoms' not in body:
        raise ValueError("Missing required field: symptoms")
    
    job_id = body['job_id'].strip()
    document_url = body['document_url'].strip()
    symptoms = body['symptoms'].strip()
    
    # Validate non-empty
    if not job_id:
        raise ValueError("job_id cannot be empty")
    
    if not document_url:
        raise ValueError("document_url cannot be empty")
    
    if not symptoms:
        raise ValueError("symptoms cannot be empty")
    
    # Validate document URL format (S3 URL)
    if not document_url.startswith('s3://'):
        raise ValueError("document_url must be an S3 URL (s3://bucket/key)")
    
    return {
        'job_id': job_id,
        'document_url': document_url,
        'symptoms': symptoms
    }


def initialize_modules() -> None:
    """
    Initialize processing modules (lazy initialization).
    
    Modules are initialized once and reused across warm Lambda invocations
    to improve performance.
    """
    global text_extractor, policy_matcher, llm_checker, recommendation_engine
    
    if text_extractor is None:
        logger.info("Initializing TextExtractor")
        text_extractor = TextExtractor()
    
    if policy_matcher is None:
        logger.info("Initializing PolicyMatcher")
        policy_matcher = PolicyMatcher(embedding_model=EMBEDDING_MODEL)
        
        # Load policy embeddings from S3
        logger.info("Loading policy embeddings from S3")
        policy_matcher.load_policy_embeddings(S3_BUCKET_NAME)
    
    if llm_checker is None:
        logger.info("Initializing LLMExclusionChecker")
        # Use Mistral API key if available, otherwise fall back to OpenAI
        api_key = MISTRAL_API_KEY or OPENAI_API_KEY
        llm_checker = LLMExclusionChecker(
            model=LLM_MODEL,
            api_key=api_key
        )
    
    if recommendation_engine is None:
        logger.info("Initializing RecommendationEngine")
        recommendation_engine = RecommendationEngine()


def download_document_from_s3(s3_url: str) -> str:
    """
    Download document from S3 to temporary local file.
    
    Args:
        s3_url: S3 URL in format s3://bucket/key
        
    Returns:
        Path to downloaded local file
        
    Raises:
        ValueError: If S3 URL is invalid
        FileNotFoundError: If document doesn't exist in S3
        RuntimeError: If download fails
    """
    # Parse S3 URL
    if not s3_url.startswith('s3://'):
        raise ValueError(f"Invalid S3 URL: {s3_url}")
    
    parts = s3_url[5:].split('/', 1)
    if len(parts) != 2:
        raise ValueError(f"Invalid S3 URL format: {s3_url}")
    
    bucket_name = parts[0]
    key = parts[1]
    
    # Determine file extension
    file_extension = Path(key).suffix or '.tmp'
    
    # Create temporary file
    temp_file = tempfile.NamedTemporaryFile(
        delete=False,
        suffix=file_extension
    )
    temp_file_path = temp_file.name
    temp_file.close()
    
    try:
        # Download from S3
        logger.info(f"Downloading s3://{bucket_name}/{key} to {temp_file_path}")
        s3_client.download_file(bucket_name, key, temp_file_path)
        
        return temp_file_path
        
    except ClientError as e:
        error_code = e.response['Error']['Code']
        
        if error_code == '404' or error_code == 'NoSuchKey':
            raise FileNotFoundError(
                f"Document not found in S3: {s3_url}"
            )
        else:
            raise RuntimeError(
                f"Failed to download document from S3: {e.response['Error']['Message']}"
            )
    
    except Exception as e:
        raise RuntimeError(f"Failed to download document: {str(e)}")


def extract_text(file_path: str) -> str:
    """
    Extract text from document based on file type.
    
    Args:
        file_path: Path to local document file
        
    Returns:
        Extracted and normalized text
        
    Raises:
        ValueError: If file type is not supported
        RuntimeError: If extraction fails
    """
    file_extension = Path(file_path).suffix.lower()
    
    try:
        if file_extension == '.pdf':
            raw_text = text_extractor.extract_from_pdf(file_path)
        elif file_extension in ['.png', '.jpg', '.jpeg']:
            raw_text = text_extractor.extract_from_image(file_path)
        elif file_extension == '.txt':
            raw_text = text_extractor.extract_from_text(file_path)
        else:
            raise ValueError(
                f"Unsupported file format: {file_extension}. "
                f"Supported formats: .pdf, .png, .jpg, .jpeg, .txt"
            )
        
        # Normalize text
        normalized_text = text_extractor.normalize_text(raw_text)
        
        if not normalized_text:
            raise RuntimeError("No text could be extracted from the document")
        
        logger.info(f"Extracted {len(normalized_text)} characters of text")
        
        return normalized_text
        
    except (ValueError, RuntimeError):
        raise
    except Exception as e:
        raise RuntimeError(f"Text extraction failed: {str(e)}")


def match_policies(text: str) -> list:
    """
    Generate embedding and match against policies.
    
    Args:
        text: Combined document text and symptoms
        
    Returns:
        List of PolicyMatch objects
        
    Raises:
        RuntimeError: If matching fails
    """
    try:
        # Generate embedding
        embedding = policy_matcher.generate_embedding(text)
        
        # Get threshold from environment variable (default 0.3 for better matching)
        threshold = float(os.environ.get('SIMILARITY_THRESHOLD', '0.3'))
        
        # Find similar policies
        matches = policy_matcher.find_similar_policies(
            embedding,
            top_k=5,
            threshold=threshold
        )
        
        logger.info(f"Found {len(matches)} policy matches (threshold: {threshold})")
        
        return matches
        
    except Exception as e:
        raise RuntimeError(f"Policy matching failed: {str(e)}")


def check_exclusions(document_text: str, symptoms: str, policy_matches: list) -> list:
    """
    Check exclusions for matched policies using LLM.
    
    Args:
        document_text: Extracted document text
        symptoms: User symptoms
        policy_matches: List of PolicyMatch objects
        
    Returns:
        List of ExclusionResult objects
        
    Raises:
        RuntimeError: If exclusion checking fails
    """
    exclusion_results = []
    
    for policy in policy_matches:
        try:
            result = llm_checker.check_exclusions(
                document_text,
                symptoms,
                policy
            )
            exclusion_results.append(result)
            
        except Exception as e:
            logger.error(
                f"Exclusion check failed for policy {policy.policy_id}: {str(e)}"
            )
            # Continue with other policies even if one fails
            continue
    
    if not exclusion_results:
        raise RuntimeError("All exclusion checks failed")
    
    return exclusion_results


def generate_recommendations(policy_matches: list, exclusion_results: list) -> list:
    """
    Generate recommendations from policy matches and exclusion results.
    
    Args:
        policy_matches: List of PolicyMatch objects
        exclusion_results: List of ExclusionResult objects
        
    Returns:
        List of Recommendation objects
        
    Raises:
        RuntimeError: If recommendation generation fails
    """
    try:
        recommendations = recommendation_engine.generate_recommendations(
            policy_matches,
            exclusion_results
        )
        
        return recommendations
        
    except Exception as e:
        raise RuntimeError(f"Recommendation generation failed: {str(e)}")


def format_recommendation(recommendation) -> Dict[str, Any]:
    """
    Format Recommendation object for JSON serialization.
    
    Args:
        recommendation: Recommendation object
        
    Returns:
        Dictionary representation
    """
    return {
        'policy_id': recommendation.policy_id,
        'policy_name': recommendation.policy_name,
        'action': recommendation.action,
        'confidence': round(recommendation.confidence, 3),
        'reasoning': recommendation.reasoning,
        'next_steps': recommendation.next_steps,
        'priority': recommendation.priority
    }


def store_result(job_id: str, result: Dict[str, Any]) -> None:
    """
    Store processing result in DynamoDB.
    
    Args:
        job_id: Job identifier
        result: Processing result dictionary
    """
    try:
        # Add TTL (7 days from now)
        ttl = int(time.time()) + (7 * 24 * 60 * 60)
        
        item = {
            'job_id': job_id,
            'status': result['status'],
            'result': json.dumps(result),
            'updated_at': int(time.time()),
            'ttl': ttl
        }
        
        jobs_table.put_item(Item=item)
        
        logger.info(f"Stored result for job {job_id} in DynamoDB")
        
    except Exception as e:
        logger.error(f"Failed to store result in DynamoDB: {str(e)}")
        # Don't raise - this is not critical for the response


def update_job_status(job_id: str, status: str, data: Optional[Dict[str, Any]] = None) -> None:
    """
    Update job status in DynamoDB.
    
    Args:
        job_id: Job identifier
        status: Job status ('processing', 'completed', 'failed')
        data: Optional additional data to store
    """
    try:
        item = {
            'job_id': job_id,
            'status': status,
            'updated_at': int(time.time())
        }
        
        if data:
            item['data'] = json.dumps(data)
        
        jobs_table.put_item(Item=item)
        
        logger.info(f"Updated job {job_id} status to {status}")
        
    except Exception as e:
        logger.error(f"Failed to update job status in DynamoDB: {str(e)}")
        # Don't raise - this is not critical


def cleanup_temp_file(file_path: Optional[str]) -> None:
    """
    Clean up temporary file.
    
    Args:
        file_path: Path to temporary file
    """
    if file_path and os.path.exists(file_path):
        try:
            os.remove(file_path)
            logger.debug(f"Cleaned up temporary file: {file_path}")
        except Exception as e:
            logger.warning(f"Failed to clean up temporary file: {str(e)}")


def convert_decimal(obj):
    """
    Convert DynamoDB Decimal types to JSON-serializable types.
    
    Args:
        obj: Object that may contain Decimal types
        
    Returns:
        Object with Decimals converted to int or float
    """
    if isinstance(obj, list):
        return [convert_decimal(item) for item in obj]
    elif isinstance(obj, dict):
        return {key: convert_decimal(value) for key, value in obj.items()}
    elif isinstance(obj, Decimal):
        # Convert to int if it's a whole number, otherwise float
        if obj % 1 == 0:
            return int(obj)
        else:
            return float(obj)
    else:
        return obj


def create_response(status_code: int, body: Dict[str, Any]) -> Dict[str, Any]:
    """
    Create API Gateway response.
    
    Args:
        status_code: HTTP status code
        body: Response body dictionary
        
    Returns:
        API Gateway response format
    """
    # Convert any Decimal types to JSON-serializable types
    body = convert_decimal(body)
    
    return {
        'statusCode': status_code,
        'headers': {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Headers': 'Content-Type,X-Amz-Date,Authorization,X-Api-Key',
            'Access-Control-Allow-Methods': 'POST,GET,OPTIONS'
        },
        'body': json.dumps(body)
    }
