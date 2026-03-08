# Recommendation Engine Usage Guide

## Overview

The `RecommendationEngine` module generates actionable recommendations based on validated policies, combining similarity scores from PolicyMatcher with exclusion results from LLMExclusionChecker.

## Features

- **Intelligent Action Determination**: Automatically determines whether to claim, review, or exclude policies
- **Confidence Scoring**: Combines similarity and LLM confidence using weighted averages
- **Priority Ranking**: Prioritizes recommendations by confidence level
- **Actionable Next Steps**: Generates specific next steps based on action type
- **Flexible Configuration**: Customizable weights for confidence calculation

## Installation

No additional dependencies required beyond the core project dependencies.

## Basic Usage

```python
from src.recommendation_engine import RecommendationEngine
from src.policy_matcher import PolicyMatcher, PolicyMatch
from src.llm_exclusion_checker import LLMExclusionChecker

# Initialize the recommendation engine
engine = RecommendationEngine(
    similarity_weight=0.4,
    llm_confidence_weight=0.6
)

# Assume you have policy matches and exclusion results
policy_matches = [...]  # From PolicyMatcher
exclusion_results = [...]  # From LLMExclusionChecker

# Generate recommendations
recommendations = engine.generate_recommendations(
    validated_policies=policy_matches,
    exclusion_results=exclusion_results
)

# Process recommendations
for rec in recommendations:
    print(f"Policy: {rec.policy_name}")
    print(f"Action: {rec.action}")
    print(f"Confidence: {rec.confidence:.2%}")
    print(f"Priority: {rec.priority}")
    print(f"Reasoning: {rec.reasoning}")
    print(f"Next Steps:")
    for step in rec.next_steps:
        print(f"  - {step}")
    print()
```

## Configuration Options

### Weight Configuration

The engine uses weighted averaging to combine similarity scores and LLM confidence:

```python
# Default: LLM confidence weighted more heavily
engine = RecommendationEngine(
    similarity_weight=0.4,      # 40% weight to similarity score
    llm_confidence_weight=0.6   # 60% weight to LLM confidence
)

# Equal weighting
engine = RecommendationEngine(
    similarity_weight=0.5,
    llm_confidence_weight=0.5
)

# Prioritize similarity score
engine = RecommendationEngine(
    similarity_weight=0.7,
    llm_confidence_weight=0.3
)
```

**Note**: Weights are automatically normalized to sum to 1.0.

## Recommendation Structure

```python
@dataclass
class Recommendation:
    policy_id: str          # Policy identifier
    policy_name: str        # Human-readable policy name
    action: str             # "claim", "review", or "exclude"
    confidence: float       # Overall confidence (0.0 to 1.0)
    reasoning: str          # Explanation from LLM
    next_steps: List[str]   # Actionable next steps
    priority: int           # 1 (high), 2 (medium), or 3 (low)
```

## Action Types

### Claim
**When**: High confidence (>0.8) and no exclusions found

**Meaning**: Policy clearly applies, proceed with claim filing

**Next Steps**:
- Proceed with filing a claim under this policy
- Gather all required documentation for claim submission
- Contact the insurance provider to initiate the claim process
- Keep copies of all submitted documents for your records

### Review
**When**: Medium confidence (0.6-0.8) and no exclusions

**Meaning**: Policy likely applies but requires expert review

**Next Steps**:
- Schedule a consultation with an insurance agent for detailed review
- Prepare questions about policy coverage and exclusions
- Bring all relevant documents to the consultation
- Request clarification on any ambiguous policy terms

### Exclude
**When**: Low confidence (<0.6) or exclusions found or policy doesn't apply

**Meaning**: Policy may not apply to the situation

**Next Steps**:
- This policy may not apply to your situation
- Review other available policies that may be more suitable
- Consult with an insurance advisor for alternative options
- Note: Exclusions detected or policy terms don't match

## Priority Levels

Recommendations are sorted by priority (ascending) then confidence (descending):

- **Priority 1 (High)**: Confidence > 0.8 - Immediate action recommended
- **Priority 2 (Medium)**: Confidence 0.6-0.8 - Review recommended
- **Priority 3 (Low)**: Confidence < 0.6 - Alternative options recommended

## Complete Integration Example

```python
from src.text_extractor import TextExtractor
from src.policy_matcher import PolicyMatcher
from src.llm_exclusion_checker import LLMExclusionChecker
from src.recommendation_engine import RecommendationEngine
import os

# Set up API key
os.environ['OPENAI_API_KEY'] = 'your-api-key'

# Initialize all components
extractor = TextExtractor()
matcher = PolicyMatcher()
checker = LLMExclusionChecker()
engine = RecommendationEngine()

# Load policy embeddings
matcher.load_policy_embeddings('my-s3-bucket')

# Step 1: Extract text from document
document_text = extractor.extract_from_pdf('medical_document.pdf')
normalized_text = extractor.normalize_text(document_text)

# Step 2: Find matching policies
symptoms = "Experiencing chest pain and shortness of breath"
combined_text = f"{normalized_text} {symptoms}"
embedding = matcher.generate_embedding(combined_text)
policy_matches = matcher.find_similar_policies(embedding, top_k=5)

# Step 3: Check exclusions for each match
exclusion_results = []
for policy in policy_matches:
    result = checker.check_exclusions(
        document_text=normalized_text,
        symptoms=symptoms,
        policy=policy
    )
    exclusion_results.append(result)

# Step 4: Generate recommendations
recommendations = engine.generate_recommendations(
    validated_policies=policy_matches,
    exclusion_results=exclusion_results
)

# Step 5: Display results
print(f"Found {len(recommendations)} recommendations:\n")

for i, rec in enumerate(recommendations, 1):
    print(f"{i}. {rec.policy_name}")
    print(f"   Action: {rec.action.upper()}")
    print(f"   Confidence: {rec.confidence:.1%}")
    print(f"   Priority: {'High' if rec.priority == 1 else 'Medium' if rec.priority == 2 else 'Low'}")
    print(f"   Reasoning: {rec.reasoning}")
    print(f"   Next Steps:")
    for step in rec.next_steps:
        print(f"     • {step}")
    print()
```

## Confidence Calculation

The overall confidence is calculated as a weighted average:

```
confidence = (similarity_weight × similarity_score) + (llm_weight × llm_confidence)
```

Example with default weights (0.4, 0.6):
- Similarity score: 0.85
- LLM confidence: 0.90
- Overall confidence: (0.4 × 0.85) + (0.6 × 0.90) = 0.34 + 0.54 = 0.88

## Error Handling

```python
try:
    recommendations = engine.generate_recommendations(
        validated_policies=policy_matches,
        exclusion_results=exclusion_results
    )
except ValueError as e:
    print(f"Invalid input: {e}")
    # Handle mismatched inputs or empty lists
```

Common errors:
- **ValueError**: Mismatched number of policies and exclusion results
- **ValueError**: Invalid confidence scores (outside 0.0-1.0 range)
- **ValueError**: Empty exclusion results list

## Best Practices

1. **Match Inputs**: Ensure policy_matches and exclusion_results have the same length and matching policy_ids
2. **Filter Low Scores**: Consider filtering out very low confidence recommendations (<0.5)
3. **Present Top Results**: Show only top 3-5 recommendations to avoid overwhelming users
4. **Explain Actions**: Always display the reasoning and next steps to users
5. **Manual Review**: Recommend human review for medium-priority items
6. **Weight Tuning**: Adjust weights based on your domain and accuracy requirements

## Testing

Run the comprehensive test suite:

```bash
pytest tests/test_recommendation_engine.py -v
```

The test suite includes:
- Initialization and configuration tests
- Confidence calculation tests
- Action determination tests
- Priority ranking tests
- Next steps generation tests
- Edge case handling tests
- Input validation tests

## Performance Considerations

- **Computation**: Very fast, no external API calls
- **Memory**: Minimal, only stores configuration and processes lists
- **Scalability**: Can handle hundreds of recommendations efficiently
- **Latency**: Sub-millisecond processing time

## Customization

### Custom Action Logic

You can extend the engine by subclassing and overriding methods:

```python
class CustomRecommendationEngine(RecommendationEngine):
    def _determine_action(self, confidence, exclusion_result):
        # Custom logic for your domain
        if exclusion_result.exclusions_found:
            return "exclude"
        
        # More conservative thresholds
        if confidence > 0.9:
            return "claim"
        elif confidence > 0.7:
            return "review"
        else:
            return "exclude"
```

### Custom Next Steps

```python
class CustomRecommendationEngine(RecommendationEngine):
    def _generate_next_steps(self, action, exclusion_result):
        # Add domain-specific next steps
        if action == "claim":
            return [
                "Step 1: Custom instruction",
                "Step 2: Another custom instruction",
                # ...
            ]
        return super()._generate_next_steps(action, exclusion_result)
```

## Output Formatting

### JSON Export

```python
import json
from dataclasses import asdict

recommendations_json = [asdict(rec) for rec in recommendations]
print(json.dumps(recommendations_json, indent=2))
```

### HTML Report

```python
def generate_html_report(recommendations):
    html = "<html><body><h1>Policy Recommendations</h1>"
    
    for rec in recommendations:
        html += f"""
        <div class="recommendation">
            <h2>{rec.policy_name}</h2>
            <p><strong>Action:</strong> {rec.action}</p>
            <p><strong>Confidence:</strong> {rec.confidence:.1%}</p>
            <p><strong>Reasoning:</strong> {rec.reasoning}</p>
            <h3>Next Steps:</h3>
            <ul>
                {''.join(f'<li>{step}</li>' for step in rec.next_steps)}
            </ul>
        </div>
        """
    
    html += "</body></html>"
    return html
```

## Troubleshooting

### No Recommendations Generated
**Cause**: Empty policy matches or all policies filtered out
**Solution**: Check that PolicyMatcher returned results and exclusion checking completed

### Mismatched Input Error
**Cause**: Different number of policies and exclusion results
**Solution**: Ensure you run exclusion checking for every policy match

### All Recommendations Have "Exclude" Action
**Cause**: Low confidence scores or many exclusions found
**Solution**: Review policy matching threshold and LLM prompt tuning

### Unexpected Priority Ordering
**Cause**: Confidence scores very close together
**Solution**: This is expected; recommendations with similar confidence may have similar priority

## Future Enhancements

Potential improvements for future versions:
- Machine learning-based action prediction
- User feedback integration for continuous improvement
- Multi-criteria decision analysis (MCDA) support
- Explanation generation using LLM
- A/B testing framework for different weighting strategies
- Integration with claim filing systems

## Related Documentation

- [PolicyMatcher Usage Guide](./POLICY_MATCHER_USAGE.md)
- [LLM Exclusion Checker Usage Guide](./LLM_EXCLUSION_CHECKER_USAGE.md)
- [Text Extractor Usage Guide](./TEXT_EXTRACTOR_USAGE.md)
