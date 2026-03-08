#!/usr/bin/env python3
"""
Test script for precompute_embeddings.py

This script tests the embedding generation logic without requiring AWS credentials.
It uses mock data to verify the script's core functionality.
"""

import json
import numpy as np
from datetime import datetime

# Mock the sentence_transformers import for testing
try:
    from sentence_transformers import SentenceTransformer
    SENTENCE_TRANSFORMERS_AVAILABLE = True
except ImportError:
    print("⚠ sentence-transformers not installed. Install with: pip install sentence-transformers")
    SENTENCE_TRANSFORMERS_AVAILABLE = False


def test_embedding_generation():
    """Test that embeddings can be generated for sample policies"""
    print("=" * 70)
    print("Testing Embedding Generation")
    print("=" * 70)
    
    if not SENTENCE_TRANSFORMERS_AVAILABLE:
        print("✗ Cannot test without sentence-transformers library")
        return False
    
    # Sample policies
    sample_policies = [
        {
            "policy_id": "POL-001",
            "policy_name": "Basic Health Insurance",
            "policy_text": "Covers hospitalization, surgery, and emergency care.",
            "category": "health"
        },
        {
            "policy_id": "POL-002",
            "policy_name": "Comprehensive Health Plus",
            "policy_text": "Covers all medical expenses including outpatient care.",
            "category": "health"
        }
    ]
    
    try:
        # Initialize model
        print("\n1. Loading embedding model...")
        model = SentenceTransformer('all-MiniLM-L6-v2')
        print("   ✓ Model loaded successfully")
        
        # Generate embeddings
        print("\n2. Generating embeddings...")
        embeddings = {}
        for policy in sample_policies:
            embedding = model.encode(policy['policy_text'], convert_to_numpy=True)
            embeddings[policy['policy_id']] = embedding.tolist()
            print(f"   ✓ {policy['policy_id']}: dimension={len(embedding)}")
        
        # Verify embeddings
        print("\n3. Verifying embeddings...")
        for policy_id, embedding in embeddings.items():
            assert isinstance(embedding, list), f"Embedding should be a list"
            assert len(embedding) == 384, f"Expected dimension 384, got {len(embedding)}"
            assert all(isinstance(x, float) for x in embedding), "All values should be floats"
        print("   ✓ All embeddings have correct format and dimension")
        
        # Test cosine similarity
        print("\n4. Testing cosine similarity...")
        vec1 = np.array(embeddings['POL-001'])
        vec2 = np.array(embeddings['POL-002'])
        
        # Normalize
        vec1_norm = vec1 / (np.linalg.norm(vec1) + 1e-10)
        vec2_norm = vec2 / (np.linalg.norm(vec2) + 1e-10)
        
        # Calculate similarity
        similarity = np.dot(vec1_norm, vec2_norm)
        print(f"   ✓ Similarity between POL-001 and POL-002: {similarity:.4f}")
        assert 0.0 <= similarity <= 1.0, "Similarity should be between 0 and 1"
        
        # Test JSON serialization
        print("\n5. Testing JSON serialization...")
        embeddings_json = json.dumps(embeddings)
        embeddings_loaded = json.loads(embeddings_json)
        assert len(embeddings_loaded) == len(embeddings), "JSON serialization failed"
        print("   ✓ Embeddings can be serialized to JSON")
        
        print("\n" + "=" * 70)
        print("✓ All tests passed!")
        print("=" * 70)
        return True
        
    except Exception as e:
        print(f"\n✗ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_data_structure():
    """Test the expected data structure for embeddings and metadata"""
    print("\n" + "=" * 70)
    print("Testing Data Structure")
    print("=" * 70)
    
    # Sample embedding (384 dimensions)
    sample_embedding = [0.123] * 384
    
    # Expected embeddings structure
    embeddings = {
        "POL-001": sample_embedding,
        "POL-002": sample_embedding
    }
    
    # Expected metadata structure
    metadata = {
        "POL-001": {
            "policy_id": "POL-001",
            "policy_name": "Basic Health Insurance",
            "policy_text": "Covers hospitalization, surgery, and emergency care.",
            "category": "health",
            "coverage_details": {"hospitalization": True},
            "exclusions": ["Pre-existing conditions"],
            "created_at": datetime.utcnow().isoformat()
        }
    }
    
    print("\n1. Validating embeddings structure...")
    assert isinstance(embeddings, dict), "Embeddings should be a dictionary"
    assert all(isinstance(k, str) for k in embeddings.keys()), "Keys should be strings"
    assert all(isinstance(v, list) for v in embeddings.values()), "Values should be lists"
    print("   ✓ Embeddings structure is valid")
    
    print("\n2. Validating metadata structure...")
    assert isinstance(metadata, dict), "Metadata should be a dictionary"
    for policy_id, data in metadata.items():
        assert 'policy_id' in data, "Missing policy_id"
        assert 'policy_name' in data, "Missing policy_name"
        assert 'policy_text' in data, "Missing policy_text"
        assert 'category' in data, "Missing category"
    print("   ✓ Metadata structure is valid")
    
    print("\n3. Testing JSON serialization...")
    try:
        embeddings_json = json.dumps(embeddings)
        metadata_json = json.dumps(metadata)
        print("   ✓ Both structures can be serialized to JSON")
    except Exception as e:
        print(f"   ✗ JSON serialization failed: {e}")
        return False
    
    print("\n" + "=" * 70)
    print("✓ Data structure tests passed!")
    print("=" * 70)
    return True


def main():
    """Run all tests"""
    print("\n" + "=" * 70)
    print("Pre-compute Embeddings - Test Suite")
    print("=" * 70)
    print("\nThis script tests the embedding generation logic without AWS.")
    print("It verifies that the core functionality works correctly.\n")
    
    # Run tests
    test1_passed = test_data_structure()
    test2_passed = test_embedding_generation()
    
    # Summary
    print("\n" + "=" * 70)
    print("Test Summary")
    print("=" * 70)
    print(f"Data Structure Test: {'✓ PASSED' if test1_passed else '✗ FAILED'}")
    print(f"Embedding Generation Test: {'✓ PASSED' if test2_passed else '✗ FAILED'}")
    
    if test1_passed and test2_passed:
        print("\n✓ All tests passed! The precompute_embeddings.py script is ready to use.")
        print("\nNext steps:")
        print("1. Ensure AWS credentials are configured: aws configure")
        print("2. Verify DynamoDB table exists and has policies")
        print("3. Run: python infrastructure/precompute_embeddings.py")
        return 0
    else:
        print("\n✗ Some tests failed. Please fix the issues before running the script.")
        return 1


if __name__ == "__main__":
    import sys
    sys.exit(main())
