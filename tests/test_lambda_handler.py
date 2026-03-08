"""
Integration tests for Lambda handler

Tests the main lambda_handler function with various scenarios.
"""

import json
import os
import sys
from unittest.mock import Mock, patch, MagicMock
import pytest

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from lambda_handler import (
    lambda_handler,
    parse_event,
    create_response,
    format_recommendation
)
from recommendation_engine import Recommendation


class TestParseEvent:
    """Test event parsing functionality"""
    
    def test_parse_event_with_direct_body(self):
        """Test parsing event with direct body dictionary"""
        event = {
            'job_id': 'test-job-123',
            'document_url': 's3://bucket/document.pdf',
            'symptoms': 'fever and cough'
        }
        
        result = parse_event(event)
        
        assert result['job_id'] == 'test-job-123'
        assert result['document_url'] == 's3://bucket/document.pdf'
        assert result['symptoms'] == 'fever and cough'
    
    def test_parse_event_with_api_gateway_format(self):
        """Test parsing event with API Gateway format"""
        event = {
            'body': json.dumps({
                'job_id': 'test-job-456',
                'document_url': 's3://bucket/image.png',
                'symptoms': 'headache'
            })
        }
        
        result = parse_event(event)
        
        assert result['job_id'] == 'test-job-456'
        assert result['document_url'] == 's3://bucket/image.png'
        assert result['symptoms'] == 'headache'
    
    def test_parse_event_missing_job_id(self):
        """Test parsing event with missing job_id"""
        event = {
            'document_url': 's3://bucket/document.pdf',
            'symptoms': 'fever'
        }
        
        with pytest.raises(ValueError, match="Missing required field: job_id"):
            parse_event(event)
    
    def test_parse_event_missing_document_url(self):
        """Test parsing event with missing document_url"""
        event = {
            'job_id': 'test-job-123',
            'symptoms': 'fever'
        }
        
        with pytest.raises(ValueError, match="Missing required field: document_url"):
            parse_event(event)
    
    def test_parse_event_missing_symptoms(self):
        """Test parsing event with missing symptoms"""
        event = {
            'job_id': 'test-job-123',
            'document_url': 's3://bucket/document.pdf'
        }
        
        with pytest.raises(ValueError, match="Missing required field: symptoms"):
            parse_event(event)
    
    def test_parse_event_empty_job_id(self):
        """Test parsing event with empty job_id"""
        event = {
            'job_id': '   ',
            'document_url': 's3://bucket/document.pdf',
            'symptoms': 'fever'
        }
        
        with pytest.raises(ValueError, match="job_id cannot be empty"):
            parse_event(event)
    
    def test_parse_event_invalid_s3_url(self):
        """Test parsing event with invalid S3 URL"""
        event = {
            'job_id': 'test-job-123',
            'document_url': 'http://example.com/document.pdf',
            'symptoms': 'fever'
        }
        
        with pytest.raises(ValueError, match="document_url must be an S3 URL"):
            parse_event(event)


class TestCreateResponse:
    """Test response creation functionality"""
    
    def test_create_response_success(self):
        """Test creating successful response"""
        body = {
            'job_id': 'test-job-123',
            'status': 'completed',
            'recommendations': []
        }
        
        response = create_response(200, body)
        
        assert response['statusCode'] == 200
        assert 'headers' in response
        assert response['headers']['Content-Type'] == 'application/json'
        assert 'Access-Control-Allow-Origin' in response['headers']
        
        response_body = json.loads(response['body'])
        assert response_body['job_id'] == 'test-job-123'
        assert response_body['status'] == 'completed'
    
    def test_create_response_error(self):
        """Test creating error response"""
        body = {
            'job_id': 'test-job-123',
            'status': 'failed',
            'error': 'VALIDATION_ERROR',
            'error_message': 'Invalid input'
        }
        
        response = create_response(400, body)
        
        assert response['statusCode'] == 400
        response_body = json.loads(response['body'])
        assert response_body['status'] == 'failed'
        assert response_body['error'] == 'VALIDATION_ERROR'


class TestFormatRecommendation:
    """Test recommendation formatting"""
    
    def test_format_recommendation(self):
        """Test formatting a recommendation object"""
        recommendation = Recommendation(
            policy_id='POL-001',
            policy_name='Health Insurance Basic',
            action='claim',
            confidence=0.85,
            reasoning='Policy matches your situation',
            next_steps=['Step 1', 'Step 2'],
            priority=1
        )
        
        formatted = format_recommendation(recommendation)
        
        assert formatted['policy_id'] == 'POL-001'
        assert formatted['policy_name'] == 'Health Insurance Basic'
        assert formatted['action'] == 'claim'
        assert formatted['confidence'] == 0.85
        assert formatted['reasoning'] == 'Policy matches your situation'
        assert formatted['next_steps'] == ['Step 1', 'Step 2']
        assert formatted['priority'] == 1


class TestLambdaHandlerIntegration:
    """Integration tests for lambda_handler"""
    
    @patch('lambda_handler.s3_client')
    @patch('lambda_handler.jobs_table')
    @patch('lambda_handler.text_extractor')
    @patch('lambda_handler.policy_matcher')
    @patch('lambda_handler.llm_checker')
    @patch('lambda_handler.recommendation_engine')
    def test_lambda_handler_validation_error(
        self,
        mock_rec_engine,
        mock_llm,
        mock_matcher,
        mock_extractor,
        mock_table,
        mock_s3
    ):
        """Test lambda_handler with validation error"""
        event = {
            'job_id': 'test-job-123',
            # Missing document_url
            'symptoms': 'fever'
        }
        
        response = lambda_handler(event, None)
        
        assert response['statusCode'] == 400
        body = json.loads(response['body'])
        assert body['status'] == 'failed'
        assert body['error'] == 'VALIDATION_ERROR'
        assert 'document_url' in body['error_message']
    
    @patch('lambda_handler.s3_client')
    @patch('lambda_handler.jobs_table')
    def test_lambda_handler_invalid_s3_url(self, mock_table, mock_s3):
        """Test lambda_handler with invalid S3 URL"""
        event = {
            'job_id': 'test-job-123',
            'document_url': 'http://example.com/doc.pdf',
            'symptoms': 'fever'
        }
        
        response = lambda_handler(event, None)
        
        assert response['statusCode'] == 400
        body = json.loads(response['body'])
        assert body['status'] == 'failed'
        assert 'S3 URL' in body['error_message']


def test_lambda_handler_module_imports():
    """Test that all required modules can be imported"""
    import lambda_handler
    
    # Verify key functions exist
    assert hasattr(lambda_handler, 'lambda_handler')
    assert hasattr(lambda_handler, 'parse_event')
    assert hasattr(lambda_handler, 'initialize_modules')
    assert hasattr(lambda_handler, 'download_document_from_s3')
    assert hasattr(lambda_handler, 'extract_text')
    assert hasattr(lambda_handler, 'match_policies')
    assert hasattr(lambda_handler, 'check_exclusions')
    assert hasattr(lambda_handler, 'generate_recommendations')
    assert hasattr(lambda_handler, 'store_result')
    assert hasattr(lambda_handler, 'create_response')
