"""
Unit tests for RecommendationEngine module
"""

import pytest
from src.recommendation_engine import RecommendationEngine, Recommendation
from src.policy_matcher import PolicyMatch
from src.llm_exclusion_checker import ExclusionResult


class TestRecommendationEngine:
    """Test suite for RecommendationEngine class"""
    
    @pytest.fixture
    def recommendation_engine(self):
        """Create a RecommendationEngine instance for testing"""
        return RecommendationEngine(similarity_weight=0.4, llm_confidence_weight=0.6)
    
    @pytest.fixture
    def sample_policy_matches(self):
        """Sample policy matches for testing"""
        return [
            PolicyMatch(
                policy_id='POL-001',
                policy_text='Basic health insurance coverage',
                similarity_score=0.85,
                metadata={'policy_name': 'Basic Health Insurance', 'category': 'health'}
            ),
            PolicyMatch(
                policy_id='POL-002',
                policy_text='Comprehensive health plus coverage',
                similarity_score=0.72,
                metadata={'policy_name': 'Comprehensive Health Plus', 'category': 'health'}
            ),
            PolicyMatch(
                policy_id='POL-003',
                policy_text='Dental insurance coverage',
                similarity_score=0.65,
                metadata={'policy_name': 'Dental Insurance', 'category': 'dental'}
            )
        ]
    
    @pytest.fixture
    def sample_exclusion_results(self):
        """Sample exclusion results for testing"""
        return [
            ExclusionResult(
                policy_id='POL-001',
                applies=True,
                confidence=0.9,
                reasoning='Policy covers the documented condition with no exclusions',
                exclusions_found=[],
                llm_model='gpt-3.5-turbo'
            ),
            ExclusionResult(
                policy_id='POL-002',
                applies=True,
                confidence=0.75,
                reasoning='Policy likely applies but requires agent review',
                exclusions_found=[],
                llm_model='gpt-3.5-turbo'
            ),
            ExclusionResult(
                policy_id='POL-003',
                applies=False,
                confidence=0.8,
                reasoning='Policy does not cover the documented condition',
                exclusions_found=['pre-existing condition'],
                llm_model='gpt-3.5-turbo'
            )
        ]
    
    def test_initialization(self):
        """Test RecommendationEngine initialization"""
        engine = RecommendationEngine(similarity_weight=0.4, llm_confidence_weight=0.6)
        
        # Weights should be normalized
        assert abs(engine.similarity_weight + engine.llm_confidence_weight - 1.0) < 1e-6
        assert 0.0 <= engine.similarity_weight <= 1.0
        assert 0.0 <= engine.llm_confidence_weight <= 1.0
    
    def test_initialization_invalid_weights(self):
        """Test initialization with invalid weights"""
        with pytest.raises(ValueError):
            RecommendationEngine(similarity_weight=-0.1, llm_confidence_weight=0.6)
        
        with pytest.raises(ValueError):
            RecommendationEngine(similarity_weight=0.4, llm_confidence_weight=1.5)
    
    def test_calculate_confidence(self, recommendation_engine):
        """Test confidence calculation using weighted average"""
        confidence = recommendation_engine.calculate_confidence(
            similarity_score=0.8,
            llm_confidence=0.9
        )
        
        # Expected: 0.4 * 0.8 + 0.6 * 0.9 = 0.32 + 0.54 = 0.86
        expected = 0.4 * 0.8 + 0.6 * 0.9
        assert abs(confidence - expected) < 1e-6
        assert 0.0 <= confidence <= 1.0
    
    def test_calculate_confidence_edge_cases(self, recommendation_engine):
        """Test confidence calculation with edge case values"""
        # Both scores at 0
        confidence = recommendation_engine.calculate_confidence(0.0, 0.0)
        assert confidence == 0.0
        
        # Both scores at 1
        confidence = recommendation_engine.calculate_confidence(1.0, 1.0)
        assert confidence == 1.0
        
        # Mixed values
        confidence = recommendation_engine.calculate_confidence(0.5, 0.5)
        assert 0.0 <= confidence <= 1.0
    
    def test_calculate_confidence_invalid_scores(self, recommendation_engine):
        """Test confidence calculation with invalid scores"""
        with pytest.raises(ValueError):
            recommendation_engine.calculate_confidence(-0.1, 0.5)
        
        with pytest.raises(ValueError):
            recommendation_engine.calculate_confidence(0.5, 1.5)
    
    def test_generate_recommendations(
        self,
        recommendation_engine,
        sample_policy_matches,
        sample_exclusion_results
    ):
        """Test recommendation generation"""
        recommendations = recommendation_engine.generate_recommendations(
            sample_policy_matches,
            sample_exclusion_results
        )
        
        # Should generate 3 recommendations
        assert len(recommendations) == 3
        
        # All should be Recommendation objects
        for rec in recommendations:
            assert isinstance(rec, Recommendation)
            assert rec.policy_id in ['POL-001', 'POL-002', 'POL-003']
            assert rec.action in ['claim', 'review', 'exclude']
            assert 0.0 <= rec.confidence <= 1.0
            assert rec.priority in [1, 2, 3]
            assert len(rec.next_steps) > 0
            assert rec.reasoning
    
    def test_recommendations_sorted_by_priority(
        self,
        recommendation_engine,
        sample_policy_matches,
        sample_exclusion_results
    ):
        """Test that recommendations are sorted by priority then confidence"""
        recommendations = recommendation_engine.generate_recommendations(
            sample_policy_matches,
            sample_exclusion_results
        )
        
        # Check sorting: priority ascending, confidence descending within same priority
        for i in range(len(recommendations) - 1):
            current = recommendations[i]
            next_rec = recommendations[i + 1]
            
            # Priority should be ascending
            if current.priority != next_rec.priority:
                assert current.priority < next_rec.priority
            else:
                # Within same priority, confidence should be descending
                assert current.confidence >= next_rec.confidence
    
    def test_action_determination_high_confidence(self, recommendation_engine):
        """Test action determination for high confidence with no exclusions"""
        exclusion_result = ExclusionResult(
            policy_id='POL-001',
            applies=True,
            confidence=0.9,
            reasoning='Clear match',
            exclusions_found=[],
            llm_model='gpt-3.5-turbo'
        )
        
        action = recommendation_engine._determine_action(0.85, exclusion_result)
        assert action == 'claim'
    
    def test_action_determination_medium_confidence(self, recommendation_engine):
        """Test action determination for medium confidence"""
        exclusion_result = ExclusionResult(
            policy_id='POL-002',
            applies=True,
            confidence=0.7,
            reasoning='Possible match',
            exclusions_found=[],
            llm_model='gpt-3.5-turbo'
        )
        
        action = recommendation_engine._determine_action(0.7, exclusion_result)
        assert action == 'review'
    
    def test_action_determination_with_exclusions(self, recommendation_engine):
        """Test action determination when exclusions are found"""
        exclusion_result = ExclusionResult(
            policy_id='POL-003',
            applies=False,
            confidence=0.8,
            reasoning='Exclusions apply',
            exclusions_found=['pre-existing condition'],
            llm_model='gpt-3.5-turbo'
        )
        
        action = recommendation_engine._determine_action(0.9, exclusion_result)
        assert action == 'exclude'
    
    def test_action_determination_low_confidence(self, recommendation_engine):
        """Test action determination for low confidence"""
        exclusion_result = ExclusionResult(
            policy_id='POL-004',
            applies=True,
            confidence=0.5,
            reasoning='Uncertain match',
            exclusions_found=[],
            llm_model='gpt-3.5-turbo'
        )
        
        action = recommendation_engine._determine_action(0.5, exclusion_result)
        assert action == 'exclude'
    
    def test_priority_determination(self, recommendation_engine):
        """Test priority ranking by confidence score"""
        # High confidence -> priority 1
        assert recommendation_engine._determine_priority(0.9) == 1
        
        # Medium confidence -> priority 2
        assert recommendation_engine._determine_priority(0.7) == 2
        
        # Low confidence -> priority 3
        assert recommendation_engine._determine_priority(0.5) == 3
        
        # Edge cases
        assert recommendation_engine._determine_priority(0.81) == 1  # Just above threshold
        assert recommendation_engine._determine_priority(0.8) == 2   # At threshold boundary
        assert recommendation_engine._determine_priority(0.6) == 2   # At lower threshold
    
    def test_next_steps_for_claim_action(self, recommendation_engine):
        """Test next steps generation for claim action"""
        exclusion_result = ExclusionResult(
            policy_id='POL-001',
            applies=True,
            confidence=0.9,
            reasoning='Clear match',
            exclusions_found=[],
            llm_model='gpt-3.5-turbo'
        )
        
        next_steps = recommendation_engine._generate_next_steps('claim', exclusion_result)
        
        assert len(next_steps) > 0
        assert any('claim' in step.lower() for step in next_steps)
        assert any('documentation' in step.lower() for step in next_steps)
    
    def test_next_steps_for_review_action(self, recommendation_engine):
        """Test next steps generation for review action"""
        exclusion_result = ExclusionResult(
            policy_id='POL-002',
            applies=True,
            confidence=0.7,
            reasoning='Needs review',
            exclusions_found=[],
            llm_model='gpt-3.5-turbo'
        )
        
        next_steps = recommendation_engine._generate_next_steps('review', exclusion_result)
        
        assert len(next_steps) > 0
        assert any('agent' in step.lower() or 'consultation' in step.lower() for step in next_steps)
    
    def test_next_steps_for_exclude_action(self, recommendation_engine):
        """Test next steps generation for exclude action"""
        exclusion_result = ExclusionResult(
            policy_id='POL-003',
            applies=False,
            confidence=0.8,
            reasoning='Does not apply',
            exclusions_found=['pre-existing condition'],
            llm_model='gpt-3.5-turbo'
        )
        
        next_steps = recommendation_engine._generate_next_steps('exclude', exclusion_result)
        
        assert len(next_steps) > 0
        assert any('pre-existing condition' in step for step in next_steps)
    
    def test_empty_policy_list(self, recommendation_engine):
        """Test handling of empty policy list"""
        recommendations = recommendation_engine.generate_recommendations([], [])
        assert recommendations == []
    
    def test_mismatched_inputs(
        self,
        recommendation_engine,
        sample_policy_matches
    ):
        """Test error handling for mismatched input lengths"""
        # Only 2 exclusion results for 3 policies
        exclusion_results = [
            ExclusionResult(
                policy_id='POL-001',
                applies=True,
                confidence=0.9,
                reasoning='Test',
                exclusions_found=[],
                llm_model='gpt-3.5-turbo'
            )
        ]
        
        with pytest.raises(ValueError, match="Mismatch"):
            recommendation_engine.generate_recommendations(
                sample_policy_matches,
                exclusion_results
            )
    
    def test_missing_exclusion_result(
        self,
        recommendation_engine,
        sample_policy_matches
    ):
        """Test handling when exclusion result is missing for a policy"""
        # Exclusion results with wrong policy IDs
        exclusion_results = [
            ExclusionResult(
                policy_id='POL-999',  # Wrong ID
                applies=True,
                confidence=0.9,
                reasoning='Test',
                exclusions_found=[],
                llm_model='gpt-3.5-turbo'
            ),
            ExclusionResult(
                policy_id='POL-998',  # Wrong ID
                applies=True,
                confidence=0.9,
                reasoning='Test',
                exclusions_found=[],
                llm_model='gpt-3.5-turbo'
            ),
            ExclusionResult(
                policy_id='POL-997',  # Wrong ID
                applies=True,
                confidence=0.9,
                reasoning='Test',
                exclusions_found=[],
                llm_model='gpt-3.5-turbo'
            )
        ]
        
        # Should skip policies without matching exclusion results
        recommendations = recommendation_engine.generate_recommendations(
            sample_policy_matches,
            exclusion_results
        )
        
        assert len(recommendations) == 0
    
    def test_recommendation_fields(
        self,
        recommendation_engine,
        sample_policy_matches,
        sample_exclusion_results
    ):
        """Test that all recommendation fields are properly populated"""
        recommendations = recommendation_engine.generate_recommendations(
            sample_policy_matches,
            sample_exclusion_results
        )
        
        for rec in recommendations:
            # Check all required fields are present and valid
            assert rec.policy_id
            assert rec.policy_name
            assert rec.action in ['claim', 'review', 'exclude']
            assert isinstance(rec.confidence, float)
            assert 0.0 <= rec.confidence <= 1.0
            assert rec.reasoning
            assert isinstance(rec.next_steps, list)
            assert len(rec.next_steps) > 0
            assert rec.priority in [1, 2, 3]
