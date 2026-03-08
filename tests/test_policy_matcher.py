"""
Unit tests for PolicyMatcher module
"""

import pytest
import numpy as np
import json
from unittest.mock import Mock, patch, MagicMock
from src.policy_matcher import PolicyMatcher, PolicyMatch


class TestPolicyMatcher:
    """Test suite for PolicyMatcher class"""
    
    @pytest.fixture
    def policy_matcher(self):
        """Create a PolicyMatcher instance for testing"""
        return PolicyMatcher(embedding_model='all-MiniLM-L6-v2')
    
    @pytest.fixture
    def sample_embeddings(self):
        """Sample policy embeddings for testing"""
        return {
            'POL-001': np.random.rand(384),
            'POL-002': np.random.rand(384),
            'POL-003': np.random.rand(384)
        }
    
    @pytest.fixture
    def sample_metadata(self):
        """Sample policy metadata for testing"""
        return {
            'POL-001': {
                'policy_text': 'Basic health insurance coverage',
                'category': 'health'
            },
            'POL-002': {
                'policy_text': 'Comprehensive health plus coverage',
                'category': 'health'
            },
            'POL-003': {
                'policy_text': 'Dental insurance coverage',
                'category': 'dental'
            }
        }
    
    def test_initialization(self, policy_matcher):
        """Test PolicyMatcher initialization"""
        assert policy_matcher.model_name == 'all-MiniLM-L6-v2'
        assert policy_matcher.model is not None
        assert policy_matcher.policy_embeddings is None
        assert policy_matcher.policy_metadata is None
    
    def test_generate_embedding_valid_text(self, policy_matcher):
        """Test embedding generation with valid text"""
        text = "This is a sample health insurance policy"
        embedding = policy_matcher.generate_embedding(text)
        
        assert embedding is not None
        assert isinstance(embedding, np.ndarray)
        assert len(embedding) == 384  # MiniLM model dimension
    
    def test_generate_embedding_empty_text(self, policy_matcher):
        """Test embedding generation with empty text raises error"""
        with pytest.raises(ValueError, match="Input text cannot be empty"):
            policy_matcher.generate_embedding("")
    
    def test_generate_embedding_whitespace_only(self, policy_matcher):
        """Test embedding generation with whitespace-only text raises error"""
        with pytest.raises(ValueError, match="Input text cannot be empty"):
            policy_matcher.generate_embedding("   ")
    
    def test_cosine_similarity(self, policy_matcher):
        """Test cosine similarity calculation"""
        vec1 = np.array([1.0, 0.0, 0.0])
        vec2 = np.array([1.0, 0.0, 0.0])
        
        similarity = policy_matcher._cosine_similarity(vec1, vec2)
        
        assert 0.99 <= similarity <= 1.0  # Should be very close to 1.0
    
    def test_cosine_similarity_orthogonal(self, policy_matcher):
        """Test cosine similarity with orthogonal vectors"""
        vec1 = np.array([1.0, 0.0, 0.0])
        vec2 = np.array([0.0, 1.0, 0.0])
        
        similarity = policy_matcher._cosine_similarity(vec1, vec2)
        
        assert similarity < 0.1  # Should be close to 0
    
    def test_find_similar_policies_not_loaded(self, policy_matcher):
        """Test find_similar_policies raises error when embeddings not loaded"""
        query_embedding = np.random.rand(384)
        
        with pytest.raises(RuntimeError, match="Policy embeddings not loaded"):
            policy_matcher.find_similar_policies(query_embedding)
    
    def test_find_similar_policies_empty_embedding(self, policy_matcher, sample_embeddings, sample_metadata):
        """Test find_similar_policies with empty embedding raises error"""
        policy_matcher.policy_embeddings = sample_embeddings
        policy_matcher.policy_metadata = sample_metadata
        
        with pytest.raises(ValueError, match="Query embedding cannot be empty"):
            policy_matcher.find_similar_policies(np.array([]))
    
    def test_find_similar_policies_success(self, policy_matcher, sample_embeddings, sample_metadata):
        """Test successful policy matching"""
        policy_matcher.policy_embeddings = sample_embeddings
        policy_matcher.policy_metadata = sample_metadata
        
        # Create a query embedding similar to POL-001
        query_embedding = sample_embeddings['POL-001'] + np.random.rand(384) * 0.1
        
        matches = policy_matcher.find_similar_policies(query_embedding, top_k=2)
        
        assert len(matches) <= 2
        assert all(isinstance(match, PolicyMatch) for match in matches)
        
        # Check that matches are sorted by similarity score
        if len(matches) > 1:
            assert matches[0].similarity_score >= matches[1].similarity_score
    
    def test_find_similar_policies_with_threshold(self, policy_matcher, sample_embeddings, sample_metadata):
        """Test policy matching with similarity threshold"""
        policy_matcher.policy_embeddings = sample_embeddings
        policy_matcher.policy_metadata = sample_metadata
        
        query_embedding = np.random.rand(384)
        
        matches = policy_matcher.find_similar_policies(
            query_embedding, 
            top_k=5, 
            threshold=0.9  # High threshold
        )
        
        # All matches should have similarity >= threshold
        assert all(match.similarity_score >= 0.9 for match in matches)
    
    def test_find_similar_policies_returns_policy_match_objects(self, policy_matcher, sample_embeddings, sample_metadata):
        """Test that find_similar_policies returns proper PolicyMatch objects"""
        policy_matcher.policy_embeddings = sample_embeddings
        policy_matcher.policy_metadata = sample_metadata
        
        query_embedding = sample_embeddings['POL-001']
        
        matches = policy_matcher.find_similar_policies(query_embedding, top_k=1, threshold=0.0)
        
        assert len(matches) > 0
        match = matches[0]
        assert hasattr(match, 'policy_id')
        assert hasattr(match, 'policy_text')
        assert hasattr(match, 'similarity_score')
        assert hasattr(match, 'metadata')
    
    @patch('boto3.client')
    def test_load_policy_embeddings_success(self, mock_boto_client, policy_matcher, sample_embeddings, sample_metadata):
        """Test successful loading of policy embeddings from S3"""
        # Mock S3 client
        mock_s3 = Mock()
        mock_boto_client.return_value = mock_s3
        policy_matcher.s3_client = mock_s3
        
        # Mock S3 responses
        embeddings_json = json.dumps({
            k: v.tolist() for k, v in sample_embeddings.items()
        })
        metadata_json = json.dumps(sample_metadata)
        
        mock_s3.get_object.side_effect = [
            {'Body': Mock(read=Mock(return_value=embeddings_json.encode('utf-8')))},
            {'Body': Mock(read=Mock(return_value=metadata_json.encode('utf-8')))}
        ]
        
        # Load embeddings
        policy_matcher.load_policy_embeddings('test-bucket')
        
        # Verify embeddings were loaded
        assert policy_matcher.policy_embeddings is not None
        assert policy_matcher.policy_metadata is not None
        assert len(policy_matcher.policy_embeddings) == 3
        assert 'POL-001' in policy_matcher.policy_embeddings
    
    @patch('boto3.client')
    def test_load_policy_embeddings_caching(self, mock_boto_client, policy_matcher, sample_embeddings, sample_metadata):
        """Test that embeddings are cached and not reloaded"""
        # Pre-load embeddings
        policy_matcher.policy_embeddings = sample_embeddings
        policy_matcher.policy_metadata = sample_metadata
        
        # Mock S3 client
        mock_s3 = Mock()
        mock_boto_client.return_value = mock_s3
        policy_matcher.s3_client = mock_s3
        
        # Try to load again
        policy_matcher.load_policy_embeddings('test-bucket')
        
        # S3 should not be called due to caching
        mock_s3.get_object.assert_not_called()
    
    @patch('boto3.client')
    def test_load_policy_embeddings_file_not_found(self, mock_boto_client, policy_matcher):
        """Test error handling when embeddings file not found in S3"""
        # Mock S3 client
        mock_s3 = Mock()
        mock_boto_client.return_value = mock_s3
        policy_matcher.s3_client = mock_s3
        
        # Mock NoSuchKey exception
        from botocore.exceptions import ClientError
        mock_s3.exceptions.NoSuchKey = type('NoSuchKey', (Exception,), {})
        mock_s3.get_object.side_effect = mock_s3.exceptions.NoSuchKey("File not found")
        
        # Should raise FileNotFoundError
        with pytest.raises(FileNotFoundError, match="Embeddings or metadata file not found in S3"):
            policy_matcher.load_policy_embeddings('test-bucket')
    
    def test_policy_match_dataclass(self):
        """Test PolicyMatch dataclass creation"""
        match = PolicyMatch(
            policy_id='POL-001',
            policy_text='Sample policy text',
            similarity_score=0.95,
            metadata={'category': 'health'}
        )
        
        assert match.policy_id == 'POL-001'
        assert match.policy_text == 'Sample policy text'
        assert match.similarity_score == 0.95
        assert match.metadata['category'] == 'health'
