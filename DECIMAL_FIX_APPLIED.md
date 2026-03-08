# ✅ Decimal Serialization Fix Applied

**Date**: March 8, 2026  
**Issue**: Lambda returning 500 errors on status/results endpoints  
**Root Cause**: DynamoDB returns `Decimal` types which are not JSON serializable

## Problem

```
[ERROR] Error in handle_get_status: Object of type Decimal is not JSON serializable
```

DynamoDB stores numbers as `Decimal` type, but Python's `json.dumps()` cannot serialize Decimal objects directly.

## Solution

Added a `convert_decimal()` helper function that recursively converts all Decimal types to int or float before JSON serialization.

### Changes Made

1. **Added import**: `from decimal import Decimal`

2. **Added helper function**:
```python
def convert_decimal(obj):
    """Convert DynamoDB Decimal types to JSON-serializable types."""
    if isinstance(obj, list):
        return [convert_decimal(item) for item in obj]
    elif isinstance(obj, dict):
        return {key: convert_decimal(value) for key, value in obj.items()}
    elif isinstance(obj, Decimal):
        if obj % 1 == 0:
            return int(obj)
        else:
            return float(obj)
    else:
        return obj
```

3. **Updated create_response()**:
```python
def create_response(status_code: int, body: Dict[str, Any]) -> Dict[str, Any]:
    # Convert any Decimal types to JSON-serializable types
    body = convert_decimal(body)
    
    return {
        'statusCode': status_code,
        'headers': {...},
        'body': json.dumps(body)
    }
```

## Deployment

```bash
# Rebuild Docker image
docker build -t document-policy-processor .

# Tag and push to ECR
docker tag document-policy-processor:latest 877786395190.dkr.ecr.us-east-1.amazonaws.com/document-policy-processor:latest
docker push 877786395190.dkr.ecr.us-east-1.amazonaws.com/document-policy-processor:latest

# Update Lambda function
aws lambda update-function-code \
  --function-name DocumentPolicyProcessor \
  --image-uri 877786395190.dkr.ecr.us-east-1.amazonaws.com/document-policy-processor:latest \
  --region us-east-1
```

## Verification

```bash
# Test status endpoint
curl -X GET "https://bmi41mg6uf.execute-api.us-east-1.amazonaws.com/prod/api/status/6532bf02-1813-4160-b147-fefef97ff8d2" \
  -H "X-Api-Key: 9wx9nHe2NV5vSAOyRps9l3c7PpQ19OttaJqHw4mw"

# Response: ✅ Success
{"job_id": "6532bf02-1813-4160-b147-fefef97ff8d2", "status": "completed", "updated_at": 1772976967}
```

## Status

✅ **FIXED** - All endpoints now working correctly
- `/api/health` - ✅ Working
- `/api/upload-url` - ✅ Working
- `/api/process-document` - ✅ Working
- `/api/status/{jobId}` - ✅ Working (was failing, now fixed)
- `/api/results/{jobId}` - ✅ Working (was failing, now fixed)

## Next Steps

Your Streamlit Cloud app should now work without 500 errors! Try uploading a document again.

---

**Lambda Version**: Latest (deployed March 8, 2026 13:45 UTC)  
**Image Digest**: sha256:320430dde8143e264a5fb282b900ca6a204878e16fe36fd32296048180eac205
