"""
Recommendation Engine Module

This module generates actionable recommendations based on validated policies,
combining similarity scores from PolicyMatcher with exclusion results from LLMExclusionChecker.
"""

import logging
from typing import List
from dataclasses import dataclass
try:
    # Try relative imports first (for package usage)
    from .policy_matcher import PolicyMatch
    from .llm_exclusion_checker import ExclusionResult
except ImportError:
    # Fall back to absolute imports (for direct execution)
    from policy_matcher import PolicyMatch
    from llm_exclusion_checker import ExclusionResult

# Configure logging
logger = logging.getLogger(__name__)


@dataclass
class Recommendation:
    """Represents an actionable recommendation for a policy"""
    policy_id: str
    policy_name: str
    action: str  # "claim", "review", "exclude"
    confidence: float
    reasoning: str
    next_steps: List[str]
    priority: int  # 1 (high) to 3 (low)


class RecommendationEngine:
    """
    Generates actionable recommendations based on validated policies.
    
    Combines policy matching results with LLM exclusion checking to produce
    prioritized recommendations with confidence scores and next steps.
    """
    
    def __init__(
        self,
        similarity_weight: float = 0.4,
        llm_confidence_weight: float = 0.6
    ):
        """
        Initialize RecommendationEngine with confidence calculation weights.
        
        Args:
            similarity_weight: Weight for similarity score in confidence calculation (0.0-1.0)
            llm_confidence_weight: Weight for LLM confidence in confidence calculation (0.0-1.0)
        """
        if not 0.0 <= similarity_weight <= 1.0:
            raise ValueError("similarity_weight must be between 0.0 and 1.0")
        
        if not 0.0 <= llm_confidence_weight <= 1.0:
            raise ValueError("llm_confidence_weight must be between 0.0 and 1.0")
        
        # Normalize weights to sum to 1.0
        total_weight = similarity_weight + llm_confidence_weight
        self.similarity_weight = similarity_weight / total_weight
        self.llm_confidence_weight = llm_confidence_weight / total_weight
        
        logger.info(
            f"Initialized RecommendationEngine with weights: "
            f"similarity={self.similarity_weight:.2f}, llm={self.llm_confidence_weight:.2f}"
        )
    
    def generate_recommendations(
        self,
        validated_policies: List[PolicyMatch],
        exclusion_results: List[ExclusionResult]
    ) -> List[Recommendation]:
        """
        Generate prioritized recommendations from validated policies.
        
        Combines policy matching scores with LLM exclusion checking results
        to produce actionable recommendations sorted by priority.
        
        Args:
            validated_policies: List of PolicyMatch objects from PolicyMatcher
            exclusion_results: List of ExclusionResult objects from LLMExclusionChecker
            
        Returns:
            List of Recommendation objects sorted by priority (high to low)
            
        Raises:
            ValueError: If inputs are invalid or mismatched
        """
        if not validated_policies:
            logger.warning("No validated policies provided")
            return []
        
        if not exclusion_results:
            raise ValueError("Exclusion results cannot be empty")
        
        if len(validated_policies) != len(exclusion_results):
            raise ValueError(
                f"Mismatch between policies ({len(validated_policies)}) "
                f"and exclusion results ({len(exclusion_results)})"
            )
        
        # Create exclusion results lookup by policy_id
        exclusion_map = {result.policy_id: result for result in exclusion_results}
        
        recommendations = []
        
        for policy in validated_policies:
            # Get corresponding exclusion result
            exclusion_result = exclusion_map.get(policy.policy_id)
            
            if not exclusion_result:
                logger.warning(
                    f"No exclusion result found for policy {policy.policy_id}, skipping"
                )
                continue
            
            # Calculate overall confidence
            confidence = self.calculate_confidence(
                policy.similarity_score,
                exclusion_result.confidence
            )
            
            # Determine action based on confidence and exclusion result
            action = self._determine_action(confidence, exclusion_result)
            
            # Determine priority based on confidence
            priority = self._determine_priority(confidence)
            
            # Generate next steps based on action
            next_steps = self._generate_next_steps(action, exclusion_result)
            
            # Get policy name from metadata
            policy_name = policy.metadata.get('policy_name', f"Policy {policy.policy_id}")
            
            # Create recommendation
            recommendation = Recommendation(
                policy_id=policy.policy_id,
                policy_name=policy_name,
                action=action,
                confidence=confidence,
                reasoning=exclusion_result.reasoning,
                next_steps=next_steps,
                priority=priority
            )
            
            recommendations.append(recommendation)
            
            logger.debug(
                f"Generated recommendation for {policy.policy_id}: "
                f"action={action}, confidence={confidence:.2f}, priority={priority}"
            )
        
        # Sort by priority (ascending) then by confidence (descending)
        recommendations.sort(key=lambda r: (r.priority, -r.confidence))
        
        logger.info(f"Generated {len(recommendations)} recommendations")
        
        return recommendations
    
    def calculate_confidence(
        self,
        similarity_score: float,
        llm_confidence: float
    ) -> float:
        """
        Calculate overall confidence score using weighted average.
        
        Combines the similarity score from policy matching with the LLM's
        confidence score to produce a single confidence metric.
        
        Args:
            similarity_score: Cosine similarity score from PolicyMatcher (0.0-1.0)
            llm_confidence: Confidence score from LLMExclusionChecker (0.0-1.0)
            
        Returns:
            Overall confidence score (0.0-1.0)
            
        Raises:
            ValueError: If scores are out of valid range
        """
        if not 0.0 <= similarity_score <= 1.0:
            raise ValueError(f"similarity_score must be between 0.0 and 1.0, got {similarity_score}")
        
        if not 0.0 <= llm_confidence <= 1.0:
            raise ValueError(f"llm_confidence must be between 0.0 and 1.0, got {llm_confidence}")
        
        # Weighted average
        confidence = (
            self.similarity_weight * similarity_score +
            self.llm_confidence_weight * llm_confidence
        )
        
        # Ensure result is in valid range (handle floating point errors)
        confidence = max(0.0, min(1.0, confidence))
        
        return confidence
    
    def _determine_action(
        self,
        confidence: float,
        exclusion_result: ExclusionResult
    ) -> str:
        """
        Determine recommended action based on confidence and exclusion result.
        
        Args:
            confidence: Overall confidence score
            exclusion_result: ExclusionResult from LLM checker
            
        Returns:
            Action string: "claim", "review", or "exclude"
        """
        # If policy doesn't apply or has exclusions, recommend exclusion
        if not exclusion_result.applies or exclusion_result.exclusions_found:
            return "exclude"
        
        # High confidence and no exclusions -> proceed with claim
        if confidence > 0.8:
            return "claim"
        
        # Medium confidence -> review with agent
        if confidence >= 0.6:
            return "review"
        
        # Low confidence -> exclude
        return "exclude"
    
    def _determine_priority(self, confidence: float) -> int:
        """
        Determine priority level based on confidence score.
        
        Args:
            confidence: Overall confidence score
            
        Returns:
            Priority level: 1 (high), 2 (medium), or 3 (low)
        """
        if confidence > 0.8:
            return 1  # High priority
        elif confidence >= 0.6:
            return 2  # Medium priority
        else:
            return 3  # Low priority
    
    def _generate_next_steps(
        self,
        action: str,
        exclusion_result: ExclusionResult
    ) -> List[str]:
        """
        Generate next steps based on action type.
        
        Args:
            action: Recommended action ("claim", "review", "exclude")
            exclusion_result: ExclusionResult from LLM checker
            
        Returns:
            List of next step strings
        """
        if action == "claim":
            next_steps = [
                "Proceed with filing a claim under this policy",
                "Gather all required documentation for claim submission",
                "Contact the insurance provider to initiate the claim process",
                "Keep copies of all submitted documents for your records"
            ]
        
        elif action == "review":
            next_steps = [
                "Schedule a consultation with an insurance agent for detailed review",
                "Prepare questions about policy coverage and exclusions",
                "Bring all relevant documents to the consultation",
                "Request clarification on any ambiguous policy terms"
            ]
            
            # Add specific notes about exclusions if found
            if exclusion_result.exclusions_found:
                next_steps.append(
                    f"Discuss these potential concerns: {', '.join(exclusion_result.exclusions_found)}"
                )
        
        elif action == "exclude":
            next_steps = [
                "This policy may not apply to your situation",
                "Review other available policies that may be more suitable",
                "Consult with an insurance advisor for alternative options"
            ]
            
            # Add specific exclusion information
            if exclusion_result.exclusions_found:
                next_steps.append(
                    f"Note: Exclusions detected - {', '.join(exclusion_result.exclusions_found)}"
                )
            elif not exclusion_result.applies:
                next_steps.append(
                    "The policy terms do not match your documented situation"
                )
        
        else:
            # Fallback for unknown action
            next_steps = ["Consult with an insurance professional for guidance"]
        
        return next_steps
