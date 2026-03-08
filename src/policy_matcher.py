"""
Policy Matcher Module

This module handles semantic policy matching using sentence-transformers embeddings.
It generates embeddings for document text and matches them against pre-computed 
policy embeddings using cosine similarity.
"""

import numpy as np
from typing import Dict, List, Optional
from dataclasses import dataclass
import json
import boto3
from sentence_transformers import SentenceTransformer


@dataclass
class PolicyMatch:
    """Represents a matched policy with similarity score"""
    policy_id: str
    policy_text: str
    similarity_score: float
    metadata: Dict


class PolicyMatcher:
    """
    Handles semantic policy matching using embeddings.
    
    Uses sentence-transformers to generate embeddings and cosine similarity
    to find the most relevant policies for a given document/symptom text.
    """
    
    def __init__(self, embedding_model: str = 'all-MiniLM-L6-v2'):
        """
        Initialize PolicyMatcher with specified embedding model.
        
        Args:
            embedding_model: Name of the sentence-transformers model to use
        """
        self.model_name = embedding_model
        self.model = SentenceTransformer(embedding_model)
        self.policy_embeddings: Optional[Dict[str, np.ndarray]] = None
        self.policy_metadata: Optional[Dict[str, Dict]] = None
        self.s3_client = boto3.client('s3')
        
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
            
        # Generate embedding using sentence-transformers
        embedding = self.model.encode(text, convert_to_numpy=True)
        return embedding
    
    def find_similar_policies(
        self, 
        query_embedding: np.ndarray, 
        top_k: int = 5,
        threshold: float = 0.6
    ) -> List[PolicyMatch]:
        """
        Find top-k most similar policies using cosine similarity.
        
        Args:
            query_embedding: Embedding vector for the query text
            top_k: Number of top matches to return
            threshold: Minimum similarity score threshold (0.0 to 1.0)
            
        Returns:
            List of PolicyMatch objects sorted by similarity score (descending)
        """
        if self.policy_embeddings is None:
            raise RuntimeError("Policy embeddings not loaded. Call load_policy_embeddings() first.")
        
        if query_embedding is None or len(query_embedding) == 0:
            raise ValueError("Query embedding cannot be empty")
        
        # Calculate cosine similarity with all policy embeddings
        similarities = {}
        for policy_id, policy_embedding in self.policy_embeddings.items():
            similarity = self._cosine_similarity(query_embedding, policy_embedding)
            similarities[policy_id] = similarity
        
        # Filter by threshold and sort by similarity score
        filtered_policies = {
            pid: score for pid, score in similarities.items() 
            if score >= threshold
        }
        
        # Sort by similarity score (descending) and take top_k
        sorted_policies = sorted(
            filtered_policies.items(), 
            key=lambda x: x[1], 
            reverse=True
        )[:top_k]
        
        # Create PolicyMatch objects
        matches = []
        for policy_id, score in sorted_policies:
            metadata = self.policy_metadata.get(policy_id, {})
            matches.append(PolicyMatch(
                policy_id=policy_id,
                policy_text=metadata.get('policy_text', ''),
                similarity_score=float(score),
                metadata=metadata
            ))
        
        return matches
    
    def load_policy_embeddings(
        self, 
        bucket_name: str, 
        embeddings_key: str = 'embeddings/policy_embeddings.json',
        metadata_key: str = 'embeddings/policy_metadata.json'
    ) -> None:
        """
        Load pre-computed policy embeddings from S3.
        
        Args:
            bucket_name: S3 bucket name containing the embeddings
            embeddings_key: S3 key for the embeddings file
            metadata_key: S3 key for the policy metadata file
        """
        # Check if already loaded (caching)
        if self.policy_embeddings is not None:
            return
        
        try:
            # Load embeddings from S3
            embeddings_obj = self.s3_client.get_object(
                Bucket=bucket_name,
                Key=embeddings_key
            )
            embeddings_data = json.loads(embeddings_obj['Body'].read().decode('utf-8'))
            
            # Convert lists back to numpy arrays
            self.policy_embeddings = {
                policy_id: np.array(embedding)
                for policy_id, embedding in embeddings_data.items()
            }
            
            # Load policy metadata from S3
            metadata_obj = self.s3_client.get_object(
                Bucket=bucket_name,
                Key=metadata_key
            )
            self.policy_metadata = json.loads(metadata_obj['Body'].read().decode('utf-8'))
            
        except self.s3_client.exceptions.NoSuchKey as e:
            raise FileNotFoundError(
                f"Embeddings or metadata file not found in S3: {e}"
            )
        except Exception as e:
            raise RuntimeError(f"Failed to load policy embeddings from S3: {e}")
    
    def calculate_similarity(self, vec1: np.ndarray, vec2: np.ndarray) -> float:
        """
        Calculate cosine similarity between two vectors (public method).
        
        Args:
            vec1: First vector
            vec2: Second vector
            
        Returns:
            Cosine similarity score (0.0 to 1.0)
        """
        return self._cosine_similarity(vec1, vec2)
    
    def _cosine_similarity(self, vec1: np.ndarray, vec2: np.ndarray) -> float:
        """
        Calculate cosine similarity between two vectors.
        
        Args:
            vec1: First vector
            vec2: Second vector
            
        Returns:
            Cosine similarity score (0.0 to 1.0)
        """
        # Normalize vectors
        vec1_norm = vec1 / (np.linalg.norm(vec1) + 1e-10)
        vec2_norm = vec2 / (np.linalg.norm(vec2) + 1e-10)
        
        # Calculate dot product
        similarity = np.dot(vec1_norm, vec2_norm)
        
        # Ensure result is in [0, 1] range (handle floating point errors)
        return float(np.clip(similarity, 0.0, 1.0))
    def calculate_similarity(self, vec1: np.ndarray, vec2: np.ndarray) -> float:
        """
        Calculate cosine similarity between two vectors (public method).

        Args:
            vec1: First vector
            vec2: Second vector

        Returns:
            Cosine similarity score (0.0 to 1.0)
        """
        return self._cosine_similarity(vec1, vec2)

    def _cosine_similarity(self, vec1: np.ndarray, vec2: np.ndarray) -> float:
        """
        Calculate cosine similarity between two vectors.

        Args:
            vec1: First vector
            vec2: Second vector

        Returns:
            Cosine similarity score (0.0 to 1.0)
        """
        # Normalize vectors
        vec1_norm = vec1 / (np.linalg.norm(vec1) + 1e-10)
        vec2_norm = vec2 / (np.linalg.norm(vec2) + 1e-10)

        # Calculate dot product
        similarity = np.dot(vec1_norm, vec2_norm)

        # Ensure result is in [0, 1] range (handle floating point errors)
        return float(np.clip(similarity, 0.0, 1.0))
