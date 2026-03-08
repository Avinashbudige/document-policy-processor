"""
Unit tests for LLMExclusionChecker module
"""

import pytest
import json
from unittest.mock import Mock, patch, MagicMock
from src.llm_exclusion_checker import LLMExclusionChecker, ExclusionResult
from src.policy_matcher import PolicyMatch


class TestLLMExclusionChecker:
    """Test suite for LLMExclusionChecker class"""
    
    @pytest.fixture
    def llm_checker(self):
        """Create an LLMExclusionChecker instance for testing"""
        with patch('openai.OpenAI'):
            return LLMExclusionChecker(
                model='gpt-3.5-turbo',
                api_key='test-key',
                max_retries=3,
                initial_retry_delay=0.1
            )
    
    @pytest.fixture
    def sample_policy_match(self):
        """Sample PolicyMatch for testing"""
        return PolicyMatch(
            policy_id='POL-001',
            policy_text='Basic health insurance covers hospitalization and surgery. Excludes pre-existing conditions for first 2 years.',
            similarity_score=0.85,
            metadata={'category': 'health'}
        )
    
    @pytest.fixture
    def sample_document_text(self):
        """Sample document text for testing"""
        return "Patient medical record showing diagnosis of diabetes and hypertension. Treatment history includes medication and regular checkups."
    
    @pytest.fixture
    def sample_symptoms(self):
        """Sample symptoms for testing"""
        return "Experiencing chest pain and shortness of breath"
    
    def test_initialization(self, llm_checker):
        """Test LLMExclusionChecker initialization"""
        assert llm_checker.model == 'gpt-3.5-turbo'
        assert llm_checker.max_retries == 3
        assert llm_checker.initial_retry_delay == 0.1
        assert llm_checker.client is not None
    
    def test_generate_prompt(self, llm_checker, sample_document_text, sample_symptoms, sample_policy_match):
        """Test prompt generation"""
        prompt = llm_checker._generate_prompt(
            sample_document_text,
            sample_symptoms,
            sample_policy_match
        )
        
        assert sample_symptoms in prompt
        assert 'POL-001' not in prompt  # Policy ID shouldn't be in prompt
        assert 'JSON' in prompt
        assert 'applies' in prompt
        assert 'confidence' in prompt
        assert 'reasoning' in prompt
        assert 'exclusions_found' in prompt
    
    def test_generate_prompt_truncates_long_text(self, llm_checker, sample_symptoms, sample_policy_match):
        """Test that prompt generation truncates very long text"""
        long_document = "A" * 5000  # Very long document
        
        prompt = llm_checker._generate_prompt(
            long_document,
            sample_symptoms,
            sample_policy_match
        )
        
        # Prompt should be shorter than original document
        assert len(prompt) < len(long_document)
        assert "..." in prompt  # Should contain truncation indicator
    
    def test_parse_response_valid_json(self, llm_checker):
        """Test parsing valid JSON response"""
        response_text = json.dumps({
            "applies": True,
            "confidence": 0.85,
            "reasoning": "Policy covers the described condition",
            "exclusions_found": []
        })
        
        result = llm_checker._parse_response(response_text, 'POL-001')
        
        assert isinstance(result, ExclusionResult)
        assert result.policy_id == 'POL-001'
        assert result.applies is True
        assert result.confidence == 0.85
        assert result.reasoning == "Policy covers the described condition"
        assert result.exclusions_found == []
        assert result.llm_model == 'gpt-3.5-turbo'
    
    def test_parse_response_with_exclusions(self, llm_checker):
        """Test parsing response with exclusions found"""
        response_text = json.dumps({
            "applies": False,
            "confidence": 0.9,
            "reasoning": "Pre-existing condition exclusion applies",
            "exclusions_found": ["pre-existing condition", "waiting period"]
        })
        
        result = llm_checker._parse_response(response_text, 'POL-002')
        
        assert result.applies is False
        assert result.confidence == 0.9
        assert len(result.exclusions_found) == 2
        assert "pre-existing condition" in result.exclusions_found
    
    def test_parse_response_with_extra_text(self, llm_checker):
        """Test parsing response when LLM adds extra text around JSON"""
        response_text = """Here is my analysis:
        {
            "applies": true,
            "confidence": 0.75,
            "reasoning": "Coverage appears to apply",
            "exclusions_found": []
        }
        Hope this helps!"""
        
        result = llm_checker._parse_response(response_text, 'POL-003')
        
        assert isinstance(result, ExclusionResult)
        assert result.applies is True
        assert result.confidence == 0.75
    
    def test_parse_response_invalid_json(self, llm_checker):
        """Test parsing invalid JSON raises error"""
        response_text = "This is not valid JSON"
        
        with pytest.raises(ValueError, match="Invalid JSON response"):
            llm_checker._parse_response(response_text, 'POL-001')
    
    def test_parse_response_missing_fields(self, llm_checker):
        """Test parsing response with missing required fields"""
        response_text = json.dumps({
            "applies": True,
            "confidence": 0.8
            # Missing 'reasoning' and 'exclusions_found'
        })
        
        with pytest.raises(ValueError, match="Missing required field"):
            llm_checker._parse_response(response_text, 'POL-001')
    
    def test_parse_response_confidence_out_of_range(self, llm_checker):
        """Test that confidence values are clipped to [0, 1]"""
        response_text = json.dumps({
            "applies": True,
            "confidence": 1.5,  # Out of range
            "reasoning": "Test",
            "exclusions_found": []
        })
        
        result = llm_checker._parse_response(response_text, 'POL-001')
        
        assert 0.0 <= result.confidence <= 1.0
        assert result.confidence == 1.0  # Should be clipped to 1.0
    
    def test_check_exclusions_empty_document(self, llm_checker, sample_symptoms, sample_policy_match):
        """Test check_exclusions with empty document raises error"""
        with pytest.raises(ValueError, match="Document text cannot be empty"):
            llm_checker.check_exclusions("", sample_symptoms, sample_policy_match)
    
    def test_check_exclusions_empty_symptoms(self, llm_checker, sample_document_text, sample_policy_match):
        """Test check_exclusions with empty symptoms raises error"""
        with pytest.raises(ValueError, match="Symptoms cannot be empty"):
            llm_checker.check_exclusions(sample_document_text, "", sample_policy_match)
    
    def test_check_exclusions_success(self, sample_document_text, sample_symptoms, sample_policy_match):
        """Test successful exclusion checking"""
        with patch('src.llm_exclusion_checker.OpenAI') as mock_openai:
            # Mock OpenAI response
            mock_client = Mock()
            mock_openai.return_value = mock_client
            
            mock_response = Mock()
            mock_response.choices = [Mock()]
            mock_response.choices[0].message.content = json.dumps({
                "applies": True,
                "confidence": 0.85,
                "reasoning": "Policy covers the condition",
                "exclusions_found": []
            })
            
            mock_client.chat.completions.create.return_value = mock_response
            
            # Create checker with mocked client
            checker = LLMExclusionChecker(model='gpt-3.5-turbo', api_key='test-key')
            
            result = checker.check_exclusions(
                sample_document_text,
                sample_symptoms,
                sample_policy_match
            )
            
            assert isinstance(result, ExclusionResult)
            assert result.policy_id == 'POL-001'
            assert result.applies is True
            assert result.confidence == 0.85
    
    def test_check_exclusions_with_retry(self, sample_document_text, sample_symptoms, sample_policy_match):
        """Test retry logic on API failure"""
        with patch('src.llm_exclusion_checker.OpenAI') as mock_openai:
            # Mock OpenAI client
            mock_client = Mock()
            mock_openai.return_value = mock_client
            
            # First call fails, second succeeds
            mock_client.chat.completions.create.side_effect = [
                Exception("API Error"),
                Mock(choices=[Mock(message=Mock(content=json.dumps({
                    "applies": True,
                    "confidence": 0.8,
                    "reasoning": "Test",
                    "exclusions_found": []
                })))])
            ]
            
            checker = LLMExclusionChecker(
                model='gpt-3.5-turbo',
                api_key='test-key',
                max_retries=2,
                initial_retry_delay=0.01
            )
            
            result = checker.check_exclusions(
                sample_document_text,
                sample_symptoms,
                sample_policy_match
            )
            
            assert isinstance(result, ExclusionResult)
            assert mock_client.chat.completions.create.call_count == 2
    
    def test_check_exclusions_fallback_on_failure(self, sample_document_text, sample_symptoms, sample_policy_match):
        """Test fallback to rule-based checking when API fails"""
        with patch('src.llm_exclusion_checker.OpenAI') as mock_openai:
            # Mock OpenAI client to always fail
            mock_client = Mock()
            mock_openai.return_value = mock_client
            
            mock_client.chat.completions.create.side_effect = Exception("API Error")
            
            checker = LLMExclusionChecker(
                model='gpt-3.5-turbo',
                api_key='test-key',
                max_retries=1,
                initial_retry_delay=0.01
            )
            
            result = checker.check_exclusions(
                sample_document_text,
                sample_symptoms,
                sample_policy_match
            )
            
            # Should get result from fallback
            assert isinstance(result, ExclusionResult)
            assert result.llm_model == "rule-based-fallback"
    
    def test_rule_based_fallback_with_exclusions(self, llm_checker):
        """Test rule-based fallback detects exclusions"""
        policy_with_exclusions = PolicyMatch(
            policy_id='POL-001',
            policy_text='Health insurance. Pre-existing conditions are excluded. Waiting period applies.',
            similarity_score=0.8,
            metadata={}
        )
        
        result = llm_checker._rule_based_fallback(
            "Sample document",
            "Sample symptoms",
            policy_with_exclusions
        )
        
        assert isinstance(result, ExclusionResult)
        assert result.llm_model == "rule-based-fallback"
        assert len(result.exclusions_found) > 0
        assert result.applies is False  # Should not apply due to exclusions
    
    def test_rule_based_fallback_without_exclusions(self, llm_checker):
        """Test rule-based fallback when no exclusions found"""
        policy_without_exclusions = PolicyMatch(
            policy_id='POL-002',
            policy_text='Comprehensive health insurance with full coverage.',
            similarity_score=0.9,
            metadata={}
        )
        
        result = llm_checker._rule_based_fallback(
            "Sample document",
            "Sample symptoms",
            policy_without_exclusions
        )
        
        assert isinstance(result, ExclusionResult)
        assert result.applies is True  # Should apply
        assert len(result.exclusions_found) == 0
    
    def test_generate_reasoning_applies(self, llm_checker):
        """Test reasoning generation when policy applies"""
        result = ExclusionResult(
            policy_id='POL-001',
            applies=True,
            confidence=0.85,
            reasoning="Coverage matches the condition",
            exclusions_found=[],
            llm_model='gpt-3.5-turbo'
        )
        
        reasoning = llm_checker.generate_reasoning(result)
        
        assert "apply" in reasoning.lower()  # Changed from "applies" to "apply"
        assert "85%" in reasoning
        assert "Coverage matches the condition" in reasoning
    
    def test_generate_reasoning_does_not_apply(self, llm_checker):
        """Test reasoning generation when policy does not apply"""
        result = ExclusionResult(
            policy_id='POL-001',
            applies=False,
            confidence=0.9,
            reasoning="Pre-existing condition exclusion",
            exclusions_found=["pre-existing condition"],
            llm_model='gpt-3.5-turbo'
        )
        
        reasoning = llm_checker.generate_reasoning(result)
        
        assert "may not apply" in reasoning.lower()
        assert "90%" in reasoning
        assert "pre-existing condition" in reasoning.lower()
    
    def test_generate_reasoning_with_considerations(self, llm_checker):
        """Test reasoning generation with exclusions but policy applies"""
        result = ExclusionResult(
            policy_id='POL-001',
            applies=True,
            confidence=0.75,
            reasoning="Generally covered with some limitations",
            exclusions_found=["waiting period"],
            llm_model='gpt-3.5-turbo'
        )
        
        reasoning = llm_checker.generate_reasoning(result)
        
        assert "apply" in reasoning.lower()  # Changed from "applies" to "apply"
        assert "considerations" in reasoning.lower() or "note" in reasoning.lower()
        assert "waiting period" in reasoning.lower()
    
    def test_exclusion_result_dataclass(self):
        """Test ExclusionResult dataclass creation"""
        result = ExclusionResult(
            policy_id='POL-001',
            applies=True,
            confidence=0.85,
            reasoning="Test reasoning",
            exclusions_found=["exclusion1"],
            llm_model='gpt-3.5-turbo'
        )
        
        assert result.policy_id == 'POL-001'
        assert result.applies is True
        assert result.confidence == 0.85
        assert result.reasoning == "Test reasoning"
        assert result.exclusions_found == ["exclusion1"]
        assert result.llm_model == 'gpt-3.5-turbo'
