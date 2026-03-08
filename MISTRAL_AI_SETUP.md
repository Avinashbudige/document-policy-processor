# Mistral AI Configuration

**API Key Added**: ✅ `bzXoA00s7QBkSXuCEakYp0aY26TsjA8Vof`  
**Model**: `mistral-small-latest`  
**Status**: Environment variable configured, code update needed

---

## Current Status

The Mistral API key has been added to the Lambda function environment variables:

```bash
MISTRAL_API_KEY=bzXoA00s7QBkSXuCEakYp0aY26TsjA8Vof
LLM_MODEL=mistral-small-latest
```

However, the Lambda function code currently uses OpenAI's API. To use Mistral AI, you need to update the code.

---

## Option 1: Quick Fix - Use OpenAI-Compatible Endpoint

Mistral AI provides an OpenAI-compatible API. You can use it with minimal code changes:

### Update `src/llm_exclusion_checker.py`:

```python
from openai import OpenAI

# In __init__ method:
self.client = OpenAI(
    api_key=api_key or os.environ.get('MISTRAL_API_KEY'),
    base_url="https://api.mistral.ai/v1"  # Add this line
)
```

This allows you to use Mistral AI with the existing OpenAI client library.

---

## Option 2: Use Mistral's Native SDK

Install the Mistral SDK and update the code:

### 1. Update `src/requirements.txt`:

```txt
# Replace openai>=1.0.0 with:
mistralai>=0.1.0
```

### 2. Update `src/llm_exclusion_checker.py`:

```python
from mistralai.client import MistralClient
from mistralai.models.chat_completion import ChatMessage

class LLMExclusionChecker:
    def __init__(self, model='mistral-small-latest', api_key=None):
        self.model = model
        self.client = MistralClient(api_key=api_key or os.environ.get('MISTRAL_API_KEY'))
    
    def check_exclusions(self, document_text, symptoms, policy):
        messages = [
            ChatMessage(role="system", content="You are a medical insurance policy expert..."),
            ChatMessage(role="user", content=prompt)
        ]
        
        response = self.client.chat(
            model=self.model,
            messages=messages,
            temperature=0.1
        )
        
        return response.choices[0].message.content
```

### 3. Update `src/lambda_handler.py`:

```python
# Change this line:
OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY')

# To:
MISTRAL_API_KEY = os.environ.get('MISTRAL_API_KEY')

# And update the initialization:
llm_checker = LLMExclusionChecker(
    model=os.environ.get('LLM_MODEL', 'mistral-small-latest'),
    api_key=MISTRAL_API_KEY
)
```

---

## Rebuild and Redeploy

After making code changes:

### 1. Rebuild Docker Image

```bash
cd document-policy-processor
docker build --platform linux/amd64 -t document-policy-processor:latest .
```

### 2. Tag and Push to ECR

```bash
docker tag document-policy-processor:latest 877786395190.dkr.ecr.us-east-1.amazonaws.com/document-policy-processor:latest
docker push 877786395190.dkr.ecr.us-east-1.amazonaws.com/document-policy-processor:latest
```

### 3. Update Lambda Function

```bash
aws lambda update-function-code \
  --function-name DocumentPolicyProcessor \
  --image-uri 877786395190.dkr.ecr.us-east-1.amazonaws.com/document-policy-processor:latest \
  --region us-east-1
```

### 4. Wait for Update

```bash
aws lambda wait function-updated \
  --function-name DocumentPolicyProcessor \
  --region us-east-1
```

---

## Testing with Mistral AI

Once updated, test the function:

```bash
# Test Lambda directly
aws lambda invoke \
  --function-name DocumentPolicyProcessor \
  --payload '{"body": "{\"document_text\":\"Patient diagnosed with diabetes\",\"symptoms\":\"High blood sugar\"}"}' \
  response.json \
  --region us-east-1

# View response
cat response.json
```

---

## Mistral AI Models Available

- `mistral-tiny` - Fastest, cheapest
- `mistral-small-latest` - Good balance (currently configured)
- `mistral-medium-latest` - More capable
- `mistral-large-latest` - Most capable

---

## Cost Comparison

### Mistral AI Pricing
- **mistral-small**: $0.001 per 1K tokens (input), $0.003 per 1K tokens (output)
- **mistral-medium**: $0.0027 per 1K tokens (input), $0.0081 per 1K tokens (output)
- **mistral-large**: $0.008 per 1K tokens (input), $0.024 per 1K tokens (output)

### OpenAI Pricing (for comparison)
- **gpt-3.5-turbo**: $0.0015 per 1K tokens (input), $0.002 per 1K tokens (output)
- **gpt-4**: $0.03 per 1K tokens (input), $0.06 per 1K tokens (output)

Mistral AI is generally more cost-effective!

---

## Current Lambda Configuration

```json
{
  "Environment": {
    "Variables": {
      "S3_BUCKET_NAME": "document-policy-processor-uploads",
      "DYNAMODB_TABLE_POLICIES": "Policies",
      "DYNAMODB_TABLE_JOBS": "ProcessingJobs",
      "EMBEDDING_MODEL": "all-MiniLM-L6-v2",
      "LLM_MODEL": "mistral-small-latest",
      "MISTRAL_API_KEY": "bzXoA00s7QBkSXuCEakYp0aY26TsjA8Vof"
    }
  }
}
```

---

## Quick Start (Recommended)

For the hackathon, I recommend **Option 1** (OpenAI-compatible endpoint) as it requires minimal code changes:

1. Update only `src/llm_exclusion_checker.py` to add `base_url`
2. Rebuild Docker image (~5 minutes)
3. Push to ECR (~2 minutes)
4. Update Lambda (~2 minutes)
5. Test (~1 minute)

**Total time**: ~10 minutes

---

## Alternative: Test Locally First

Before redeploying to Lambda, test locally:

```bash
cd document-policy-processor

# Set environment variables
export MISTRAL_API_KEY=bzXoA00s7QBkSXuCEakYp0aY26TsjA8Vof
export LLM_MODEL=mistral-small-latest

# Run local demo
cd frontend
streamlit run app_local_demo.py
```

This lets you verify Mistral AI integration works before deploying to AWS.

---

## Need Help?

If you want me to make these code changes and redeploy, just let me know! I can:

1. Update the code to use Mistral AI
2. Rebuild the Docker image
3. Push to ECR
4. Update the Lambda function
5. Test the deployment

Just say "update code for Mistral AI" and I'll do it all for you!

---

**Status**: API key configured ✅  
**Next**: Code update needed for full Mistral AI integration
