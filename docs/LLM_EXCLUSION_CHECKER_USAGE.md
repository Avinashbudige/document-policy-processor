# LLM Exclusion Checker Usage Guide

## Overview

The `LLMExclusionChecker` module validates policy matches using an LLM (Large Language Model) to check for exclusions and determine if a policy applies to the user's document and symptoms.

## Features

- **OpenAI API Integration**: Uses GPT-3.5-turbo or GPT-4 for intelligent policy analysis
- **Retry Logic**: Implements exponential backoff for handling transient API failures
- **Fallback Mechanism**: Falls back to rule-based checking if LLM API is unavailable
- **Structured Output**: Returns detailed results with confidence scores and reasoning
- **Flexible Configuration**: Customizable model, retry attempts, and delay settings

## Installation

```bash
pip install openai>=1.0.0
```

## Basic Usage

```python
from src.llm_exclusion_checker import LLMExclusionChecker
from src.policy_matcher import PolicyMatch
import os

# Set your OpenAI API key
os.environ['OPENAI_API_KEY'] = 'your-api-key-here'

# Initialize the checker
checker = LLMExclusionChecker(
    model='gpt-3.5-turbo',
    max_retries=3,
    initial_retry_delay=1.0
)

# Create a policy match (from PolicyMatcher)
policy = PolicyMatch(
    policy_id='POL-001',
    policy_text='Basic health insurance covers hospitalization...',
    similarity_score=0.85,
    metadata={'category': 'health'}
)

# Check exclusions
result = checker.check_exclusions(
    document_text="Patient medical record showing...",
    symptoms="Experiencing chest pain and shortness of breath",
    policy=policy
)

# Access results
print(f"Policy applies: {result.applies}")
print(f"Confidence: {result.confidence}")
print(f"Reasoning: {result.reasoning}")
print(f"Exclusions found: {result.exclusions_found}")

# Generate human-readable explanation
explanation = checker.generate_reasoning(result)
print(explanation)
```

## Configuration Options

### Model Selection

```python
# Use GPT-3.5-turbo (faster, cheaper)
checker = LLMExclusionChecker(model='gpt-3.5-turbo')

# Use GPT-4 (more accurate, slower, more expensive)
checker = LLMExclusionChecker(model='gpt-4')
```

### Retry Configuration

```python
checker = LLMExclusionChecker(
    model='gpt-3.5-turbo',
    max_retries=5,              # Maximum retry attempts
    initial_retry_delay=2.0     # Initial delay in seconds (doubles each retry)
)
```

### API Key Configuration

```python
# Option 1: Environment variable (recommended)
os.environ['OPENAI_API_KEY'] = 'your-api-key'
checker = LLMExclusionChecker()

# Option 2: Direct parameter
checker = LLMExclusionChecker(api_key='your-api-key')
```

## ExclusionResult Structure

```python
@dataclass
class ExclusionResult:
    policy_id: str              # Policy identifier
    applies: bool               # Whether policy applies
    confidence: float           # Confidence score (0.0 to 1.0)
    reasoning: str              # Explanation of determination
    exclusions_found: List[str] # List of exclusions identified
    llm_model: str              # Model used for analysis
```

## Error Handling

The checker implements robust error handling:

1. **Retry Logic**: Automatically retries on transient failures with exponential backoff
2. **Fallback Mechanism**: Falls back to rule-based checking if LLM API fails
3. **Input Validation**: Validates inputs and raises clear error messages

```python
try:
    result = checker.check_exclusions(document_text, symptoms, policy)
except ValueError as e:
    print(f"Invalid input: {e}")
except RuntimeError as e:
    print(f"Processing error: {e}")
```

## Rule-Based Fallback

If the LLM API fails after all retries, the checker automatically falls back to rule-based exclusion checking:

- Searches for common exclusion keywords in policy text
- Returns moderate confidence scores (0.5-0.6)
- Recommends manual review
- Sets `llm_model` to "rule-based-fallback"

## Best Practices

1. **Set API Key Securely**: Use environment variables, not hardcoded keys
2. **Handle Fallback Results**: Check `llm_model` field to detect fallback usage
3. **Monitor Confidence Scores**: Low confidence (<0.6) suggests manual review needed
4. **Implement Caching**: Cache results for identical inputs to reduce API costs
5. **Rate Limiting**: Be aware of OpenAI API rate limits for your tier

## Integration Example

```python
from src.text_extractor import TextExtractor
from src.policy_matcher import PolicyMatcher
from src.llm_exclusion_checker import LLMExclusionChecker

# Initialize components
extractor = TextExtractor()
matcher = PolicyMatcher()
checker = LLMExclusionChecker()

# Load policy embeddings
matcher.load_policy_embeddings('my-bucket')

# Process document
document_text = extractor.extract_from_pdf('document.pdf')
normalized_text = extractor.normalize_text(document_text)

# Find matching policies
embedding = matcher.generate_embedding(normalized_text)
policy_matches = matcher.find_similar_policies(embedding, top_k=5)

# Check exclusions for each match
results = []
for policy in policy_matches:
    result = checker.check_exclusions(
        document_text=normalized_text,
        symptoms="User symptoms here",
        policy=policy
    )
    results.append(result)

# Filter to policies that apply
applicable_policies = [r for r in results if r.applies and r.confidence > 0.7]
```

## Testing

Run the comprehensive test suite:

```bash
pytest tests/test_llm_exclusion_checker.py -v
```

The test suite includes:
- Unit tests for all methods
- Mock-based tests for API integration
- Fallback mechanism tests
- Edge case handling tests

## Environment Variables

- `OPENAI_API_KEY`: Your OpenAI API key (required)

## Dependencies

- `openai>=1.0.0`: OpenAI Python client
- `dataclasses`: For structured results (built-in Python 3.7+)
- `json`: For response parsing (built-in)
- `re`: For text processing (built-in)
- `time`: For retry delays (built-in)

## Troubleshooting

### API Key Errors
```
Error: Incorrect API key provided
```
**Solution**: Verify your OpenAI API key is set correctly

### Rate Limit Errors
```
Error: Rate limit exceeded
```
**Solution**: Implement request throttling or upgrade your OpenAI plan

### Timeout Errors
```
Error: Request timeout
```
**Solution**: Increase `max_retries` or check network connectivity

### Fallback Activation
```
WARNING: Falling back to rule-based exclusion checking
```
**Solution**: This is expected behavior when LLM API is unavailable. Results will have lower confidence.

## Performance Considerations

- **API Latency**: LLM API calls typically take 1-3 seconds
- **Cost**: GPT-3.5-turbo costs ~$0.002 per request (varies by token count)
- **Throughput**: Limited by OpenAI API rate limits (varies by tier)
- **Caching**: Implement result caching to reduce costs and improve performance

## Future Enhancements

Potential improvements for future versions:
- AWS Bedrock integration as alternative to OpenAI
- Batch processing support for multiple policies
- Streaming responses for faster perceived performance
- Fine-tuned models for insurance domain
- Multi-language support
