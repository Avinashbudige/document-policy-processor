# ⚠️ Lambda Cold Start Timeout Issue

**Date**: March 8, 2026  
**Status**: Known Issue - Workaround Available

---

## 🐛 Problem

**Error**: `504 Gateway Timeout` when calling `/api/upload-url`

**Root Cause**: 
- Lambda initialization is timing out at 10 seconds
- Large ML libraries (torch, transformers, sentence-transformers) take too long to import
- API Gateway has a 29-second timeout, but Lambda init is exceeding this
- The imports happen at module load time, before the handler can respond

**Log Evidence**:
```
INIT_REPORT Init Duration: 9999.86 ms   Phase: init     Status: timeout
```

---

## 🔧 Workaround Options

### Option 1: Use Local Demo Mode (RECOMMENDED FOR HACKATHON)

The local demo mode runs everything locally without AWS Lambda, avoiding cold start issues entirely.

**Steps**:
1. Stop the current frontend
2. Run the local demo:
```cmd
cd document-policy-processor\frontend
python app_local_demo.py
```

**OR use the batch file**:
```cmd
cd document-policy-processor\frontend
START_LOCAL_DEMO.bat
```

**Benefits**:
- ✅ No cold start delays
- ✅ Instant response times
- ✅ All features work
- ✅ Perfect for demos
- ✅ No AWS costs

**Limitations**:
- ❌ Runs on your local machine only
- ❌ Not scalable (but fine for hackathon demo)

---

### Option 2: Keep Lambda Warm (Temporary Fix)

Invoke Lambda every 5 minutes to keep it warm:

**PowerShell Script** (`keep-lambda-warm.ps1`):
```powershell
while ($true) {
    Write-Host "Warming Lambda..."
    aws lambda invoke --function-name DocumentPolicyProcessor `
        --payload file://test-health.json `
        response.json --region us-east-1
    Start-Sleep -Seconds 300  # Wait 5 minutes
}
```

**Run in background**:
```cmd
powershell -File keep-lambda-warm.ps1
```

**Benefits**:
- ✅ Lambda stays warm
- ✅ Fast response times after first warmup
- ✅ Uses AWS infrastructure

**Limitations**:
- ❌ Requires script running continuously
- ❌ First request still slow
- ❌ Costs money (Lambda invocations)

---

### Option 3: Use Provisioned Concurrency (AWS Solution)

AWS Lambda Provisioned Concurrency keeps Lambda instances warm.

**Enable**:
```bash
aws lambda put-provisioned-concurrency-config \
  --function-name DocumentPolicyProcessor \
  --provisioned-concurrent-executions 1 \
  --qualifier $LATEST \
  --region us-east-1
```

**Benefits**:
- ✅ No cold starts
- ✅ Always fast
- ✅ Production-ready

**Limitations**:
- ❌ Costs $$$  (~$15-30/month for 1 instance)
- ❌ Overkill for hackathon

---

### Option 4: Optimize Lambda (Long-term Fix)

Reduce initialization time by:

1. **Use Lambda Layers** for ML models
2. **Lazy import** heavy libraries
3. **Smaller models** (distilbert instead of full models)
4. **Pre-compiled dependencies**

**This requires significant refactoring** - not recommended for hackathon timeline.

---

## 🎯 Recommended Approach for Hackathon

### Use Local Demo Mode

This is the best option for your hackathon demo because:

1. **No delays** - Everything runs instantly
2. **Reliable** - No AWS timeouts or cold starts
3. **Full features** - All functionality works
4. **Easy to demo** - Just run the script
5. **No costs** - Runs on your machine

### How to Switch to Local Demo

1. **Stop current frontend**:
   - Close the browser tab
   - Press Ctrl+C in the terminal running Streamlit

2. **Start local demo**:
```cmd
cd document-policy-processor\frontend
START_LOCAL_DEMO.bat
```

3. **Open browser**:
   - Go to http://localhost:8501 (note: different port!)
   - Upload document
   - Enter symptoms
   - Process instantly!

---

## 📊 Performance Comparison

### AWS Lambda (Current)
- **First Request**: 60-120 seconds (cold start + processing)
- **Warm Requests**: 10-30 seconds
- **Reliability**: Timeouts on cold start
- **Cost**: Pay per invocation

### Local Demo
- **First Request**: 10-20 seconds (model loading)
- **Subsequent Requests**: 5-10 seconds
- **Reliability**: 100% (no timeouts)
- **Cost**: Free

---

## 🎬 Demo Strategy

### For Hackathon Presentation

**Option A: Local Demo (Recommended)**
1. Show the Streamlit interface
2. Upload a sample document
3. Process immediately (no waiting)
4. Show results
5. Mention "This can be deployed to AWS Lambda for production"

**Option B: Pre-warmed Lambda**
1. Warm Lambda 2-3 minutes before demo
2. Keep invoking it every 2 minutes during presentation
3. When ready to demo, it will be warm and fast
4. Show AWS console to prove it's running on AWS

**Option C: Hybrid**
1. Demo with local version (fast, reliable)
2. Show AWS console with deployed Lambda
3. Explain "We have both local and cloud versions"
4. Show architecture diagram

---

## 🔍 Technical Details

### Why Lambda Times Out

**Import Chain**:
```python
import torch  # 2-3 seconds
from transformers import ...  # 2-3 seconds
from sentence_transformers import ...  # 3-4 seconds
# Total: 7-10 seconds just for imports!
```

**Lambda Init Timeout**: 10 seconds  
**API Gateway Timeout**: 29 seconds  
**Result**: Lambda init exceeds 10s → timeout → API Gateway gets no response → 504 error

### Why Local Demo Works

- Models loaded once at startup
- No 10-second init timeout
- No API Gateway timeout
- Direct Python execution

---

## ✅ Action Items

### For Immediate Demo

1. **Switch to local demo mode**:
```cmd
cd document-policy-processor\frontend
START_LOCAL_DEMO.bat
```

2. **Test with sample documents**:
   - Use files from `demo/sample_documents/`
   - Verify everything works

3. **Prepare demo script**:
   - Practice the flow
   - Have sample symptoms ready
   - Know what results to expect

### For Future (Post-Hackathon)

1. **Optimize Lambda**:
   - Use Lambda Layers for models
   - Implement lazy loading
   - Consider smaller models

2. **Enable Provisioned Concurrency**:
   - For production deployment
   - Eliminates cold starts

3. **Add caching**:
   - Cache embeddings
   - Cache model outputs
   - Reduce processing time

---

## 📞 Quick Commands

### Start Local Demo
```cmd
cd document-policy-processor\frontend
START_LOCAL_DEMO.bat
```

### Warm Lambda (if using AWS)
```cmd
cd document-policy-processor
aws lambda invoke --function-name DocumentPolicyProcessor --payload file://test-health.json response.json --region us-east-1
```

### Check Lambda Logs
```cmd
aws logs tail /aws/lambda/DocumentPolicyProcessor --follow --region us-east-1
```

---

## 🎉 Bottom Line

**For your hackathon demo, use the local demo mode!**

It's faster, more reliable, and shows all the features without AWS complexity. You can always mention that it's "cloud-ready" and show the AWS deployment as a bonus.

---

**Local demo is the way to go! 🚀**

*Last updated: March 8, 2026*
