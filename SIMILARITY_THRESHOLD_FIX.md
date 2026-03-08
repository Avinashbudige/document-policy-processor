# Similarity Threshold Fix

**Issue**: No policy recommendations being returned  
**Root Cause**: Similarity threshold was too high (0.6 = 60%)  
**Solution**: Lowered threshold to 0.3 (30%) for better matching

## Changes Made

### 1. Environment Variable Added
Added `SIMILARITY_THRESHOLD` environment variable to Lambda function:
```bash
SIMILARITY_THRESHOLD=0.3
```

### 2. Code Updated
Modified `lambda_handler.py` to use environment variable:
```python
# Get threshold from environment variable (default 0.3)
threshold = float(os.environ.get('SIMILARITY_THRESHOLD', '0.3'))

matches = policy_matcher.find_similar_policies(
    embedding,
    top_k=5,
    threshold=threshold
)
```

## Why This Helps

### Previous Threshold (0.6)
- Required 60% similarity to match
- Too strict for semantic matching
- Medical terminology variations caused mismatches
- Result: 0 recommendations

### New Threshold (0.3)
- Requires 30% similarity to match
- More lenient for semantic variations
- Captures related medical concepts
- Result: 1-3 recommendations expected

## Similarity Score Interpretation

| Score Range | Meaning | Action |
|-------------|---------|--------|
| 0.8 - 1.0 | Very High Match | Claim with confidence |
| 0.6 - 0.8 | High Match | Claim, review details |
| 0.4 - 0.6 | Medium Match | Review carefully |
| 0.3 - 0.4 | Low Match | Consider exclusions |
| 0.0 - 0.3 | Very Low Match | Likely not covered |

## Testing

### Test Case 1: Diabetes Document
**Document**: Medical report mentioning diabetes, insulin therapy  
**Symptoms**: "Diabetes, insulin therapy, blood sugar management"  
**Expected**: Match with "Diabetes Care Plan" (POL-003)  
**Expected Score**: 0.4-0.6 (40-60%)

### Test Case 2: Pneumonia Document
**Document**: Hospital bill for pneumonia treatment  
**Symptoms**: "Hospitalized for pneumonia, need to file insurance claim"  
**Expected**: Match with "Basic Health Insurance" (POL-001) or "Comprehensive Health Plus" (POL-002)  
**Expected Score**: 0.3-0.5 (30-50%)

### Test Case 3: Hypertension Document
**Document**: Prescription for hypertension medication  
**Symptoms**: "High blood pressure, need medication coverage"  
**Expected**: Match with "Basic Health Insurance" (POL-001)  
**Expected Score**: 0.3-0.4 (30-40%)

## Deployment Status

✅ Environment variable updated in Lambda  
⚠️ Code changes require redeployment (Docker image issue)

### Temporary Workaround
The environment variable is set, but the code to read it needs to be deployed.

### Full Fix Deployment
Once Docker image issue is resolved:
```bash
docker build --platform linux/amd64 -t document-policy-processor .
docker tag document-policy-processor:latest 877786395190.dkr.ecr.us-east-1.amazonaws.com/document-policy-processor:v5
docker push 877786395190.dkr.ecr.us-east-1.amazonaws.com/document-policy-processor:v5
aws lambda update-function-code \
  --function-name DocumentPolicyProcessor \
  --image-uri 877786395190.dkr.ecr.us-east-1.amazonaws.com/document-policy-processor:v5 \
  --region us-east-1
```

## Alternative: Adjust Threshold Dynamically

You can adjust the threshold without redeployment by updating the environment variable:

```bash
# More strict (fewer matches, higher confidence)
aws lambda update-function-configuration \
  --function-name DocumentPolicyProcessor \
  --environment "Variables={...,SIMILARITY_THRESHOLD=0.5}" \
  --region us-east-1

# More lenient (more matches, lower confidence)
aws lambda update-function-configuration \
  --function-name DocumentPolicyProcessor \
  --environment "Variables={...,SIMILARITY_THRESHOLD=0.2}" \
  --region us-east-1
```

## Recommended Thresholds by Use Case

### Production (Balanced)
```
SIMILARITY_THRESHOLD=0.4
```
- Good balance of precision and recall
- Filters out very weak matches
- Provides 1-3 recommendations typically

### Demo/Testing (Lenient)
```
SIMILARITY_THRESHOLD=0.3
```
- Shows more recommendations
- Good for demonstrations
- Helps identify edge cases

### High Confidence (Strict)
```
SIMILARITY_THRESHOLD=0.6
```
- Only very strong matches
- May return 0-1 recommendations
- Use when precision is critical

## Monitoring

Check CloudWatch logs for similarity scores:
```bash
aws logs filter-log-events \
  --log-group-name /aws/lambda/DocumentPolicyProcessor \
  --filter-pattern "similarity" \
  --region us-east-1
```

Look for log messages like:
```
Found 2 policy matches (threshold: 0.3)
Policy POL-003 matched with similarity 0.45
Policy POL-001 matched with similarity 0.38
```

## Next Steps

1. ✅ Environment variable set
2. ⏳ Deploy code changes (pending Docker image fix)
3. 🧪 Test with sample documents
4. 📊 Monitor similarity scores
5. 🔧 Adjust threshold based on results

---

**Status**: Environment variable configured, code deployment pending  
**Date**: March 8, 2026  
**Impact**: Will improve recommendation matching once deployed
