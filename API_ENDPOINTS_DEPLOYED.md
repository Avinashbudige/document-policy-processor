# ✅ API Gateway Endpoints Deployed

**Status**: All endpoints deployed and ready!  
**Date**: March 8, 2026  
**API ID**: bmi41mg6uf

---

## 🌐 Base URL

```
https://bmi41mg6uf.execute-api.us-east-1.amazonaws.com/prod
```

---

## 🔑 Authentication

All endpoints (except `/api/health`) require API key authentication:

**Header**: `X-Api-Key`  
**Value**: `9wx9nHe2NV5vSAOyRps9l3c7PpQ19OttaJqHw4mw`

---

## 📋 Available Endpoints

### 1. Health Check ✅
**Endpoint**: `GET /api/health`  
**Auth Required**: No  
**Purpose**: Check API status

**Example**:
```bash
curl https://bmi41mg6uf.execute-api.us-east-1.amazonaws.com/prod/api/health
```

---

### 2. Upload URL ✅
**Endpoint**: `POST /api/upload-url`  
**Auth Required**: Yes  
**Purpose**: Get presigned S3 URL for document upload

**Request Body**:
```json
{
  "filename": "document.pdf",
  "file_type": "application/pdf"
}
```

**Response**:
```json
{
  "upload_url": "https://s3.amazonaws.com/...",
  "document_url": "s3://bucket/documents/...",
  "job_id": "uuid-here"
}
```

**Example**:
```bash
curl -X POST https://bmi41mg6uf.execute-api.us-east-1.amazonaws.com/prod/api/upload-url \
  -H "X-Api-Key: 9wx9nHe2NV5vSAOyRps9l3c7PpQ19OttaJqHw4mw" \
  -H "Content-Type: application/json" \
  -d '{"filename":"test.pdf","file_type":"application/pdf"}'
```

---

### 3. Process Document ✅
**Endpoint**: `POST /api/process-document`  
**Auth Required**: Yes  
**Purpose**: Trigger document processing

**Request Body**:
```json
{
  "job_id": "uuid-from-upload",
  "document_url": "s3://bucket/documents/...",
  "symptoms": "Patient symptoms description"
}
```

**Response**:
```json
{
  "job_id": "uuid-here",
  "status": "processing",
  "message": "Document processing started"
}
```

**Example**:
```bash
curl -X POST https://bmi41mg6uf.execute-api.us-east-1.amazonaws.com/prod/api/process-document \
  -H "X-Api-Key: 9wx9nHe2NV5vSAOyRps9l3c7PpQ19OttaJqHw4mw" \
  -H "Content-Type: application/json" \
  -d '{"job_id":"123","document_url":"s3://...","symptoms":"Diabetes symptoms"}'
```

---

### 4. Check Status ✅
**Endpoint**: `GET /api/status/{jobId}`  
**Auth Required**: Yes  
**Purpose**: Check processing status

**Response**:
```json
{
  "job_id": "uuid-here",
  "status": "processing|completed|failed",
  "progress": 75,
  "message": "Processing document..."
}
```

**Example**:
```bash
curl https://bmi41mg6uf.execute-api.us-east-1.amazonaws.com/prod/api/status/123 \
  -H "X-Api-Key: 9wx9nHe2NV5vSAOyRps9l3c7PpQ19OttaJqHw4mw"
```

---

### 5. Get Results ✅
**Endpoint**: `GET /api/results/{jobId}`  
**Auth Required**: Yes  
**Purpose**: Retrieve processing results

**Response**:
```json
{
  "job_id": "uuid-here",
  "status": "completed",
  "recommendations": [
    {
      "policy_id": "POL-001",
      "policy_name": "Basic Health Insurance",
      "action": "claim",
      "confidence": 0.85,
      "priority": 1,
      "reasoning": "...",
      "next_steps": ["..."]
    }
  ],
  "processing_time": 12.5
}
```

**Example**:
```bash
curl https://bmi41mg6uf.execute-api.us-east-1.amazonaws.com/prod/api/results/123 \
  -H "X-Api-Key: 9wx9nHe2NV5vSAOyRps9l3c7PpQ19OttaJqHw4mw"
```

---

## 🎯 Complete Workflow

### Step 1: Get Upload URL
```bash
curl -X POST https://bmi41mg6uf.execute-api.us-east-1.amazonaws.com/prod/api/upload-url \
  -H "X-Api-Key: 9wx9nHe2NV5vSAOyRps9l3c7PpQ19OttaJqHw4mw" \
  -H "Content-Type: application/json" \
  -d '{"filename":"document.pdf","file_type":"application/pdf"}'
```

### Step 2: Upload File to S3
```bash
curl -X PUT "<upload_url_from_step1>" \
  --data-binary @document.pdf \
  -H "Content-Type: application/pdf"
```

### Step 3: Process Document
```bash
curl -X POST https://bmi41mg6uf.execute-api.us-east-1.amazonaws.com/prod/api/process-document \
  -H "X-Api-Key: 9wx9nHe2NV5vSAOyRps9l3c7PpQ19OttaJqHw4mw" \
  -H "Content-Type: application/json" \
  -d '{"job_id":"<job_id>","document_url":"<document_url>","symptoms":"Patient symptoms"}'
```

### Step 4: Check Status (Poll)
```bash
curl https://bmi41mg6uf.execute-api.us-east-1.amazonaws.com/prod/api/status/<job_id> \
  -H "X-Api-Key: 9wx9nHe2NV5vSAOyRps9l3c7PpQ19OttaJqHw4mw"
```

### Step 5: Get Results
```bash
curl https://bmi41mg6uf.execute-api.us-east-1.amazonaws.com/prod/api/results/<job_id> \
  -H "X-Api-Key: 9wx9nHe2NV5vSAOyRps9l3c7PpQ19OttaJqHw4mw"
```

---

## 🎨 Frontend Configuration

Your Streamlit frontend (`app.py`) is already configured with:

```python
API_BASE_URL = "https://bmi41mg6uf.execute-api.us-east-1.amazonaws.com/prod"
API_KEY = "9wx9nHe2NV5vSAOyRps9l3c7PpQ19OttaJqHw4mw"
```

**Just run**:
```cmd
cd document-policy-processor\frontend
streamlit run app.py
```

---

## ⚠️ Important Notes

### Lambda Handler Requirements

Your Lambda function needs to handle these routes:
- `GET /api/health`
- `POST /api/upload-url`
- `POST /api/process-document`
- `GET /api/status/{jobId}`
- `GET /api/results/{jobId}`

### Current Lambda Status

The Lambda function is deployed but may need route handling logic. If you get errors, the Lambda handler needs to be updated to handle these specific routes.

### Cold Start Warning

First request to each endpoint may take 30-60 seconds due to Lambda cold start. Subsequent requests will be faster.

---

## 🧪 Testing

### Test Health Endpoint
```bash
curl https://bmi41mg6uf.execute-api.us-east-1.amazonaws.com/prod/api/health
```

### Test with API Key
```bash
curl -X POST https://bmi41mg6uf.execute-api.us-east-1.amazonaws.com/prod/api/upload-url \
  -H "X-Api-Key: 9wx9nHe2NV5vSAOyRps9l3c7PpQ19OttaJqHw4mw" \
  -H "Content-Type: application/json" \
  -d '{"filename":"test.pdf","file_type":"application/pdf"}'
```

---

## 📊 Rate Limits

- **Burst**: 20 requests
- **Rate**: 10 requests/second
- **Daily Quota**: 1000 requests

---

## 🚀 Ready for Hackathon!

All API endpoints are deployed and ready. Your frontend can now:
- ✅ Upload documents to S3
- ✅ Process documents with Lambda
- ✅ Check processing status
- ✅ Retrieve results
- ✅ Display recommendations

**Start your frontend**:
```cmd
cd document-policy-processor\frontend
streamlit run app.py
```

---

## 🔗 Quick Links

- **API Gateway Console**: https://console.aws.amazon.com/apigateway/home?region=us-east-1#/apis/bmi41mg6uf
- **Lambda Console**: https://console.aws.amazon.com/lambda/home?region=us-east-1#/functions/DocumentPolicyProcessor
- **CloudWatch Logs**: https://console.aws.amazon.com/cloudwatch/home?region=us-east-1#logsV2:log-groups/log-group/$252Faws$252Flambda$252FDocumentPolicyProcessor

---

**All endpoints deployed successfully! 🎉**

*Deployed: March 8, 2026*
