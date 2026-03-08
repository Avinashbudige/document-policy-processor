# 🚀 Backend Endpoints - Ready for Use!

**Status**: ✅ All endpoints deployed and tested  
**Frontend**: ✅ Running and connected  
**Date**: March 8, 2026

---

## 🌐 Access Your Application

### Frontend (Streamlit)
**Local URL**: http://localhost:8502  
**Network URL**: http://192.168.1.9:8502

Open either URL in your browser to access the Document Policy Processor interface.

---

## 📡 Backend API Endpoints

### Base URL
```
https://bmi41mg6uf.execute-api.us-east-1.amazonaws.com/prod
```

### Authentication
All endpoints (except health) require API key in header:
```
X-Api-Key: 9wx9nHe2NV5vSAOyRps9l3c7PpQ19OttaJqHw4mw
```

---

## 🔌 Available Endpoints

### 1. Health Check ✅
**Endpoint**: `GET /api/health`  
**Auth**: Not required  
**Purpose**: Verify API is running

**Example**:
```bash
curl https://bmi41mg6uf.execute-api.us-east-1.amazonaws.com/prod/api/health
```

**Response**:
```json
{
  "status": "healthy",
  "service": "Document Policy Processor",
  "version": "1.0.0",
  "timestamp": 1772968278
}
```

---

### 2. Generate Upload URL ✅
**Endpoint**: `POST /api/upload-url`  
**Auth**: Required  
**Purpose**: Get presigned S3 URL for document upload

**Request**:
```json
{
  "filename": "medical_report.pdf",
  "file_type": "application/pdf"
}
```

**Response**:
```json
{
  "upload_url": "https://s3.amazonaws.com/...",
  "document_url": "s3://document-policy-processor-uploads/documents/uuid/file.pdf",
  "job_id": "1aee0953-dac3-4708-92b5-2741eaf74b6a",
  "expires_in": 3600,
  "upload_method": "PUT"
}
```

**cURL Example**:
```bash
curl -X POST https://bmi41mg6uf.execute-api.us-east-1.amazonaws.com/prod/api/upload-url \
  -H "X-Api-Key: 9wx9nHe2NV5vSAOyRps9l3c7PpQ19OttaJqHw4mw" \
  -H "Content-Type: application/json" \
  -d '{"filename":"report.pdf","file_type":"application/pdf"}'
```

---

### 3. Process Document ✅
**Endpoint**: `POST /api/process-document`  
**Auth**: Required  
**Purpose**: Trigger document processing and policy matching

**Request**:
```json
{
  "job_id": "1aee0953-dac3-4708-92b5-2741eaf74b6a",
  "document_url": "s3://document-policy-processor-uploads/documents/uuid/file.pdf",
  "symptoms": "Patient experiencing chest pain and shortness of breath"
}
```

**Response**:
```json
{
  "job_id": "1aee0953-dac3-4708-92b5-2741eaf74b6a",
  "status": "completed",
  "recommendations": [
    {
      "policy_id": "POL-001",
      "policy_name": "Basic Health Insurance",
      "action": "claim",
      "confidence": 0.85,
      "priority": 1,
      "reasoning": "Document matches policy coverage criteria",
      "next_steps": ["Submit claim form", "Attach medical records"]
    }
  ],
  "processing_time": 12.5,
  "document_summary": "Medical report showing..."
}
```

**cURL Example**:
```bash
curl -X POST https://bmi41mg6uf.execute-api.us-east-1.amazonaws.com/prod/api/process-document \
  -H "X-Api-Key: 9wx9nHe2NV5vSAOyRps9l3c7PpQ19OttaJqHw4mw" \
  -H "Content-Type: application/json" \
  -d '{
    "job_id":"uuid-here",
    "document_url":"s3://bucket/path",
    "symptoms":"Patient symptoms"
  }'
```

---

### 4. Check Status ✅
**Endpoint**: `GET /api/status/{jobId}`  
**Auth**: Required  
**Purpose**: Check processing status

**Response**:
```json
{
  "job_id": "1aee0953-dac3-4708-92b5-2741eaf74b6a",
  "status": "processing",
  "updated_at": 1772968278
}
```

**Status Values**:
- `processing` - Document is being processed
- `completed` - Processing finished successfully
- `failed` - Processing failed (check error message)

**cURL Example**:
```bash
curl https://bmi41mg6uf.execute-api.us-east-1.amazonaws.com/prod/api/status/uuid-here \
  -H "X-Api-Key: 9wx9nHe2NV5vSAOyRps9l3c7PpQ19OttaJqHw4mw"
```

---

### 5. Get Results ✅
**Endpoint**: `GET /api/results/{jobId}`  
**Auth**: Required  
**Purpose**: Retrieve processing results

**Response (Completed)**:
```json
{
  "job_id": "1aee0953-dac3-4708-92b5-2741eaf74b6a",
  "status": "completed",
  "recommendations": [...],
  "processing_time": 12.5
}
```

**Response (Still Processing)**:
```json
{
  "job_id": "1aee0953-dac3-4708-92b5-2741eaf74b6a",
  "status": "processing",
  "message": "Job is still processing. Please check back later."
}
```

**cURL Example**:
```bash
curl https://bmi41mg6uf.execute-api.us-east-1.amazonaws.com/prod/api/results/uuid-here \
  -H "X-Api-Key: 9wx9nHe2NV5vSAOyRps9l3c7PpQ19OttaJqHw4mw"
```

---

## 🔄 Complete Workflow

### Step-by-Step Process

1. **Get Upload URL**
   ```
   POST /api/upload-url
   → Returns: upload_url, document_url, job_id
   ```

2. **Upload File to S3**
   ```
   PUT {upload_url}
   Body: Binary file data
   Header: Content-Type: application/pdf
   ```

3. **Process Document**
   ```
   POST /api/process-document
   Body: {job_id, document_url, symptoms}
   → Returns: Immediate response or results
   ```

4. **Check Status (if needed)**
   ```
   GET /api/status/{jobId}
   → Poll until status is "completed"
   ```

5. **Get Results**
   ```
   GET /api/results/{jobId}
   → Returns: recommendations and analysis
   ```

---

## 🎨 Frontend Integration

The Streamlit frontend automatically handles this workflow:

1. User uploads document through UI
2. Frontend calls `/api/upload-url`
3. Frontend uploads file to S3 using presigned URL
4. Frontend calls `/api/process-document`
5. Frontend displays results or polls for status
6. User sees policy recommendations

**No manual API calls needed when using the frontend!**

---

## 🧪 Testing Endpoints

### Quick Test Script (PowerShell)

```powershell
# Test health endpoint
Invoke-WebRequest -Uri "https://bmi41mg6uf.execute-api.us-east-1.amazonaws.com/prod/api/health"

# Test upload URL generation
$headers = @{
    "X-Api-Key" = "9wx9nHe2NV5vSAOyRps9l3c7PpQ19OttaJqHw4mw"
    "Content-Type" = "application/json"
}
$body = @{
    filename = "test.pdf"
    file_type = "application/pdf"
} | ConvertTo-Json

Invoke-WebRequest -Uri "https://bmi41mg6uf.execute-api.us-east-1.amazonaws.com/prod/api/upload-url" `
    -Method POST -Headers $headers -Body $body
```

---

## 📊 Backend Configuration

### Lambda Function
- **Name**: DocumentPolicyProcessor
- **Memory**: 2048 MB
- **Timeout**: 300 seconds
- **Runtime**: Container Image (Python 3.11)

### Environment Variables
- `S3_BUCKET_NAME`: document-policy-processor-uploads
- `DYNAMODB_TABLE_POLICIES`: Policies
- `DYNAMODB_TABLE_JOBS`: ProcessingJobs
- `EMBEDDING_MODEL`: all-MiniLM-L6-v2
- `LLM_MODEL`: mistral-small-latest
- `MISTRAL_API_KEY`: bzXoA00s7QBkSXuCEakYp0aY26TsjA8Vof

### AWS Resources
- **S3 Bucket**: document-policy-processor-uploads
- **DynamoDB Tables**: Policies, ProcessingJobs
- **API Gateway**: bmi41mg6uf
- **Region**: us-east-1
- **Account**: 877786395190

---

## ⚡ Performance Notes

### Cold Start
- First request may take 30-60 seconds
- Lambda needs to load ML models (sentence-transformers, torch)
- Subsequent requests are much faster (warm start)

### Processing Time
- Text extraction: 1-3 seconds
- Embedding generation: 2-5 seconds
- Policy matching: 1-2 seconds
- LLM exclusion check: 3-10 seconds
- **Total**: 10-20 seconds per document

### Rate Limits
- **Burst**: 20 requests
- **Rate**: 10 requests/second
- **Daily Quota**: 1000 requests

---

## 🔒 Security

### API Key
- Required for all endpoints except health check
- Sent in `X-Api-Key` header
- Managed through API Gateway usage plan

### S3 Presigned URLs
- Expire after 1 hour
- Only allow PUT operations
- Scoped to specific document path

### CORS
- Enabled for all origins (`*`)
- Allows POST, GET, OPTIONS methods
- Includes necessary headers for frontend access

---

## 🐛 Troubleshooting

### Common Issues

**403 Forbidden**
- Check API key is correct
- Ensure `X-Api-Key` header is included

**500 Internal Server Error**
- Check Lambda logs in CloudWatch
- Verify environment variables are set
- Check S3 bucket permissions

**Timeout**
- First request may take longer (cold start)
- Consider increasing Lambda timeout
- Check if document is too large

### View Logs
```bash
aws logs tail /aws/lambda/DocumentPolicyProcessor --follow --region us-east-1
```

---

## 🎯 Ready for Demo!

✅ All endpoints deployed and tested  
✅ Frontend running on http://localhost:8502  
✅ Backend connected to AWS  
✅ Sample policies loaded in DynamoDB  
✅ Policy embeddings generated  
✅ Mistral AI integration configured  

**Your application is ready for the hackathon demo!**

---

## 📞 Quick Reference Card

```
┌─────────────────────────────────────────────────────────────┐
│  Document Policy Processor - Quick Reference                │
├─────────────────────────────────────────────────────────────┤
│  Frontend:  http://localhost:8502                           │
│  API Base:  https://bmi41mg6uf.execute-api.us-east-1...    │
│  API Key:   9wx9nHe2NV5vSAOyRps9l3c7PpQ19OttaJqHw4mw       │
│  Region:    us-east-1                                       │
├─────────────────────────────────────────────────────────────┤
│  Endpoints:                                                 │
│  • GET  /api/health              (no auth)                  │
│  • POST /api/upload-url          (auth required)            │
│  • POST /api/process-document    (auth required)            │
│  • GET  /api/status/{jobId}      (auth required)            │
│  • GET  /api/results/{jobId}     (auth required)            │
└─────────────────────────────────────────────────────────────┘
```

---

**All systems operational! 🎉**

*Last updated: March 8, 2026*
