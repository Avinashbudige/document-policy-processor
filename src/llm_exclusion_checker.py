"""
LLM Exclusion Checker Module

This module validates policy matches using an LLM to check for exclusions and determine
if a policy applies to the user's document and symptoms.
"""

import json
import logging
import time
from typing import Dict, List, Optional
from dataclasses import dataclass
import re

import openai
from openai import OpenAI

# Configure logging
logger = logging.getLogger(__name__)


@dataclass
class ExclusionResult:
    """Represents the result of LLM exclusion checking"""
    policy_id: str
    applies: bool
    confidence: float
    reasoning: str
    exclusions_found: List[str]
    llm_model: str


class LLMExclusionChecker:
    """
    Validates policy matches and checks for exclusions using LLM.
    
    Uses OpenAI API (or AWS Bedrock) to analyze whether a policy applies
    given the document content and user symptoms, checking for exclusions.
    """
    
    def __init__(
        self, 
        model: str = 'gpt-3.5-turbo',
        api_key: Optional[str] = None,
        max_retries: int = 3,
        initial_retry_delay: float = 1.0
    ):
        """
        Initialize LLMExclusionChecker with OpenAI-compatible model.
        
        Supports both OpenAI and Mistral AI models.
        
        Args:
            model: Model name (e.g., 'gpt-3.5-turbo', 'mistral-small-latest')
            api_key: API key (if None, uses OPENAI_API_KEY or MISTRAL_API_KEY env var)
            max_retries: Maximum number of retry attempts for API calls
            initial_retry_delay: Initial delay in seconds for exponential backoff
        """
        self.model = model
        self.max_retries = max_retries
        self.initial_retry_delay = initial_retry_delay
        
        # Detect if using Mistral model
        is_mistral = 'mistral' in model.lower()
        
        # Initialize OpenAI-compatible client
        if api_key:
            if is_mistral:
                # Use Mistral API endpoint
                self.client = OpenAI(
                    api_key=api_key,
                    base_url="https://api.mistral.ai/v1"
                )
            else:
                # Use OpenAI API endpoint
                self.client = OpenAI(api_key=api_key)
        else:
            # Will use OPENAI_API_KEY or MISTRAL_API_KEY environment variable
            if is_mistral:
                self.client = OpenAI(base_url="https://api.mistral.ai/v1")
            else:
                self.client = OpenAI()
        
        logger.info(f"Initialized LLMExclusionChecker with model: {model} (Mistral: {is_mistral})")
    
    def check_exclusions(
        self,
        document_text: str,
        symptoms: str,
        policy: 'PolicyMatch'
    ) -> ExclusionResult:
        """
        Check if policy applies given document and symptoms.
        
        Uses LLM to analyze the policy text against the document and symptoms,
        identifying any exclusions that would prevent the policy from applying.
        
        Args:
            document_text: Extracted text from user's document
            symptoms: User-provided symptom description
            policy: PolicyMatch object containing policy details
            
        Returns:
            ExclusionResult with determination and reasoning
            
        Raises:
            RuntimeError: If LLM API fails after all retries
        """
        if not document_text or not document_text.strip():
            raise ValueError("Document text cannot be empty")
        
        if not symptoms or not symptoms.strip():
            raise ValueError("Symptoms cannot be empty")
        
        # Generate the prompt
        prompt = self._generate_prompt(document_text, symptoms, policy)
        
        # Call LLM with retry logic
        try:
            response_text = self._call_llm_with_retry(prompt)
            
            # Parse the response
            result = self._parse_response(response_text, policy.policy_id)
            
            logger.info(
                f"LLM exclusion check completed for policy {policy.policy_id}: "
                f"applies={result.applies}, confidence={result.confidence}"
            )
            
            return result
            
        except Exception as e:
            logger.error(f"LLM API failed after retries: {str(e)}")
            
            # Fallback to rule-based checking
            logger.warning("Falling back to rule-based exclusion checking")
            return self._rule_based_fallback(document_text, symptoms, policy)
    
    def generate_reasoning(self, result: ExclusionResult) -> str:
        """
        Generate human-readable explanation from ExclusionResult.
        
        Args:
            result: ExclusionResult object
            
        Returns:
            Human-readable explanation string
        """
        if result.applies:
            explanation = (
                f"This policy appears to apply to your situation "
                f"(confidence: {result.confidence:.0%}). "
            )
            if result.exclusions_found:
                explanation += (
                    f"However, note these potential considerations: "
                    f"{', '.join(result.exclusions_found)}. "
                )
            explanation += f"Reasoning: {result.reasoning}"
        else:
            explanation = (
                f"This policy may not apply to your situation "
                f"(confidence: {result.confidence:.0%}). "
            )
            if result.exclusions_found:
                explanation += (
                    f"Exclusions found: {', '.join(result.exclusions_found)}. "
                )
            explanation += f"Reasoning: {result.reasoning}"
        
        return explanation
    
    def _generate_prompt(
        self,
        document_text: str,
        symptoms: str,
        policy: 'PolicyMatch'
    ) -> str:
        """
        Generate prompt for LLM exclusion checking.
        
        Args:
            document_text: Extracted document text
            symptoms: User symptoms
            policy: PolicyMatch object
            
        Returns:
            Formatted prompt string
        """
        # Truncate long texts to avoid token limits
        max_doc_length = 2000
        max_policy_length = 1500
        
        truncated_doc = (
            document_text[:max_doc_length] + "..."
            if len(document_text) > max_doc_length
            else document_text
        )
        
        truncated_policy = (
            policy.policy_text[:max_policy_length] + "..."
            if len(policy.policy_text) > max_policy_length
            else policy.policy_text
        )
        
        prompt = f"""You are an insurance policy analyst. Given the following information, determine if this policy applies or if there are any exclusions.

Document: {truncated_doc}

Symptoms: {symptoms}

Policy: {truncated_policy}

Analyze whether this policy applies to the user's situation based on their document and symptoms. Check for any exclusions that would prevent coverage.

Respond in JSON format with the following structure:
{{
  "applies": true or false,
  "confidence": 0.0 to 1.0,
  "reasoning": "brief explanation of your determination",
  "exclusions_found": ["list of specific exclusions if any, otherwise empty list"]
}}

Respond ONLY with the JSON object, no additional text."""
        
        return prompt
    
    def _call_llm_with_retry(self, prompt: str) -> str:
        """
        Call LLM API with exponential backoff retry logic.
        
        Args:
            prompt: Prompt to send to LLM
            
        Returns:
            LLM response text
            
        Raises:
            RuntimeError: If all retry attempts fail
        """
        last_exception = None
        retry_delay = self.initial_retry_delay
        
        for attempt in range(self.max_retries):
            try:
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=[
                        {
                            "role": "system",
                            "content": "You are an insurance policy analyst. Respond only with valid JSON."
                        },
                        {
                            "role": "user",
                            "content": prompt
                        }
                    ],
                    temperature=0.3,  # Lower temperature for more consistent results
                    max_tokens=500
                )
                
                # Extract response text
                response_text = response.choices[0].message.content
                
                logger.debug(f"LLM API call successful on attempt {attempt + 1}")
                return response_text
                
            except openai.RateLimitError as e:
                last_exception = e
                logger.warning(
                    f"Rate limit error on attempt {attempt + 1}/{self.max_retries}: {str(e)}"
                )
                
            except openai.APIError as e:
                last_exception = e
                logger.warning(
                    f"API error on attempt {attempt + 1}/{self.max_retries}: {str(e)}"
                )
                
            except Exception as e:
                last_exception = e
                logger.warning(
                    f"Unexpected error on attempt {attempt + 1}/{self.max_retries}: {str(e)}"
                )
            
            # Don't sleep after the last attempt
            if attempt < self.max_retries - 1:
                logger.info(f"Retrying in {retry_delay:.1f} seconds...")
                time.sleep(retry_delay)
                # Exponential backoff
                retry_delay *= 2
        
        # All retries failed
        raise RuntimeError(
            f"LLM API failed after {self.max_retries} attempts: {str(last_exception)}"
        )
    
    def _parse_response(self, response_text: str, policy_id: str) -> ExclusionResult:
        """
        Parse LLM response into ExclusionResult.
        
        Args:
            response_text: Raw LLM response
            policy_id: Policy ID for the result
            
        Returns:
            ExclusionResult object
            
        Raises:
            ValueError: If response cannot be parsed
        """
        try:
            # Extract JSON from response (handle cases where LLM adds extra text)
            json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
            if json_match:
                json_str = json_match.group(0)
            else:
                json_str = response_text
            
            # Parse JSON
            data = json.loads(json_str)
            
            # Validate required fields
            required_fields = ['applies', 'confidence', 'reasoning', 'exclusions_found']
            for field in required_fields:
                if field not in data:
                    raise ValueError(f"Missing required field: {field}")
            
            # Create ExclusionResult
            result = ExclusionResult(
                policy_id=policy_id,
                applies=bool(data['applies']),
                confidence=float(data['confidence']),
                reasoning=str(data['reasoning']),
                exclusions_found=list(data['exclusions_found']),
                llm_model=self.model
            )
            
            # Validate confidence range
            if not 0.0 <= result.confidence <= 1.0:
                logger.warning(
                    f"Confidence {result.confidence} out of range, clipping to [0, 1]"
                )
                result.confidence = max(0.0, min(1.0, result.confidence))
            
            return result
            
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse LLM response as JSON: {str(e)}")
            logger.error(f"Response text: {response_text}")
            raise ValueError(f"Invalid JSON response from LLM: {str(e)}")
            
        except Exception as e:
            logger.error(f"Failed to parse LLM response: {str(e)}")
            raise ValueError(f"Failed to parse LLM response: {str(e)}")
    
    def _rule_based_fallback(
        self,
        document_text: str,
        symptoms: str,
        policy: 'PolicyMatch'
    ) -> ExclusionResult:
        """
        Fallback to rule-based exclusion checking if LLM fails.
        
        Uses simple keyword matching to detect common exclusions.
        
        Args:
            document_text: Extracted document text
            symptoms: User symptoms
            policy: PolicyMatch object
            
        Returns:
            ExclusionResult based on rule-based analysis
        """
        logger.info(f"Performing rule-based exclusion check for policy {policy.policy_id}")
        
        # Common exclusion keywords
        exclusion_keywords = [
            'pre-existing condition',
            'excluded',
            'not covered',
            'does not cover',
            'waiting period',
            'limitation',
            'restriction'
        ]
        
        # Check for exclusions in policy text
        policy_lower = policy.policy_text.lower()
        found_exclusions = []
        
        for keyword in exclusion_keywords:
            if keyword in policy_lower:
                found_exclusions.append(keyword)
        
        # Simple heuristic: if exclusions found, policy may not apply
        if found_exclusions:
            applies = False
            confidence = 0.5  # Low confidence for rule-based
            reasoning = (
                "Rule-based analysis detected potential exclusions. "
                "Manual review recommended."
            )
        else:
            applies = True
            confidence = 0.6  # Moderate confidence for rule-based
            reasoning = (
                "Rule-based analysis found no obvious exclusions. "
                "Manual review recommended for accuracy."
            )
        
        return ExclusionResult(
            policy_id=policy.policy_id,
            applies=applies,
            confidence=confidence,
            reasoning=reasoning,
            exclusions_found=found_exclusions,
            llm_model="rule-based-fallback"
        )
