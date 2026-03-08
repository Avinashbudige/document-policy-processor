"""
Quick test to verify PolicyMatcher.calculate_similarity works
"""

import sys
from pathlib import Path
import numpy as np

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from policy_matcher import PolicyMatcher

def test_calculate_similarity():
    """Test that calculate_similarity method exists and works"""
    print("Testing PolicyMatcher.calculate_similarity...")
    
    # Create matcher
    matcher = PolicyMatcher()
    
    # Create two test vectors
    vec1 = np.array([1.0, 0.0, 0.0])
    vec2 = np.array([1.0, 0.0, 0.0])
    
    # Test calculate_similarity
    try:
        similarity = matcher.calculate_similarity(vec1, vec2)
        print(f"✓ calculate_similarity works! Similarity: {similarity}")
        assert 0.99 <= similarity <= 1.01, f"Expected ~1.0, got {similarity}"
        print("✓ Similarity score is correct")
        return True
    except AttributeError as e:
        print(f"✗ Error: {e}")
        return False
    except Exception as e:
        print(f"✗ Unexpected error: {e}")
        return False

if __name__ == "__main__":
    success = test_calculate_similarity()
    if success:
        print("\n✓ All tests passed!")
        sys.exit(0)
    else:
        print("\n✗ Tests failed!")
        sys.exit(1)
