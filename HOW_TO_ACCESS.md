# How to Access Your Deployed Application

**Quick Links**: All your access points in one place!

---

## 🚀 Quick Start

### Option 1: Run Local Frontend (Easiest)

```bash
# Navigate to frontend directory
cd document-policy-processor/frontend

# Install dependencies (if not already installed)
pip install streamlit requests boto3

# Run the app
streamlit run app.py
```

The app will open in your browser at `http://localhost:8501`

**What you can do:**
- Upload medical documents
- Enter patient symptoms
- Get policy recommendations
- View matched policies

---

## 🌐 Direct API Access

### Your API Endpoint
```
Base URL: https://bmi41mg6uf.execute-api.us-east-1.amazonaws.com/prod
API Key:  9wx9nHe2NV5vSAOyRps9l3c7PpQ19OttaJqHw4mw
```

### Test Health Endpoint

**Windows (PowerShell):**
```powershell
curl -X GET "https://bmi41mg6uf.execute-api.us-east-1.amazonaws.com/prod/api/health"
```

**Windows (CMD):**
```cmd
curl -X GET "https://bmi41mg6uf.execute-api.us-east-1.amazonaws.com/prod/api/health"
```

**Expected Response:**
```json
{
  "statusCode": 200,
  "body": {
    "status": "healthy",
    "message": "Document Policy Processor API is running"
  }
}
```

### Test with API Key

```bash
curl -X GET "https://bmi41mg6uf.execute-api.us-east-1.amazonaws.com/prod/api/health" \
  -H "X-Api-Key: 9wx9nHe2NV5vSAOyRps9l3c7PpQ19OttaJqHw4mw"
```

---

## 🖥️ AWS Console Access

### 1. Lambda Function
**URL**: https://console.aws.amazon.com/lambda/home?region=us-east-1#/functions/DocumentPolicyProcessor

**What you can do:**
- View function code
- Check logs
- Test function manually
- Update environment variables
- Monitor performance

**Quick Test:**
1. Click "Test" tab
2. Create new test event
3. Use this JSON:
```json
{
  "httpMethod": "GET",
  "path": "/api/health",
  "headers": {}
}
```
4. Click "Test"

### 2. API Gateway
**URL**: https://console.aws.amazon.com/apigateway/home?region=us-east-1#/apis/bmi41mg6uf

**What you can do:**
- View all endpoints
- Test API calls
- Check usage statistics
- View API keys
- Monitor throttling

**Quick Test:**
1. Click "Resources"
2. Select GET method under /api/health
3. Click "Test" (lightning bolt icon)
4. Click "Test" button

### 3. S3 Bucket
**URL**: https://s3.console.aws.amazon.com/s3/buckets/document-policy-processor-uploads

**What you can do:**
- Upload test documents
- View embeddings
- Check processing results
- Download files

**Folders:**
- `documents/` - Uploaded medical documents
- `embeddings/` - Pre-computed policy embeddings
- `results/` - Processing results

### 4. DynamoDB Tables
**URL**: https://console.aws.amazon.com/dynamodbv2/home?region=us-east-1#tables

**Tables:**
- **Policies** - View insurance policies
- **ProcessingJobs** - Track document processing

**Quick View:**
1. Click on "Policies" table
2. Click "Explore table items"
3. See the 3 sample policies

### 5. CloudWatch Logs
**URL**: https://console.aws.amazon.com/cloudwatch/home?region=us-east-1#logsV2:log-groups

**Log Groups:**
- `/aws/lambda/DocumentPolicyProcessor` - Lambda execution logs

**View Logs:**
1. Click on log group
2. Click on latest log stream
3. See real-time logs

---

## 📱 Using Postman or Insomnia

### Import Collection

**Base URL**: `https://bmi41mg6uf.execute-api.us-east-1.amazonaws.com/prod`

**Headers:**
```
X-Api-Key: 9wx9nHe2NV5vSAOyRps9l3c7PpQ19OttaJqHw4mw
Content-Type: application/json
```

### Example Requests

#### 1. Health Check
```
GET /api/health
```

#### 2. Process Document (when implemented)
```
POST /api/process-document
Body:
{
  "document_text": "Patient diagnosed with Type 2 Diabetes...",
  "symptoms": "High blood sugar, frequent urination"
}
```

---

## 💻 Using Python

### Quick Script

```python
import requests

# Configuration
API_BASE_URL = "https://bmi41mg6uf.execute-api.us-east-1.amazonaws.com/prod"
API_KEY = "9wx9nHe2NV5vSAOyRps9l3c7PpQ19OttaJqHw4mw"

# Headers
headers = {
    "X-Api-Key": API_KEY,
    "Content-Type": "application/json"
}

# Test health endpoint
response = requests.get(f"{API_BASE_URL}/api/health", headers=headers)
print(f"Status: {response.status_code}")
print(f"Response: {response.json()}")

# Process document (example)
data = {
    "document_text": "Patient diagnosed with Type 2 Diabetes requiring insulin therapy",
    "symptoms": "High blood sugar levels, increased thirst"
}

response = requests.post(
    f"{API_BASE_URL}/api/process-document",
    headers=headers,
    json=data
)
print(f"Result: {response.json()}")
```

Save as `test_api.py` and run:
```bash
python test_api.py
```

---

## 🎥 For Demo/Presentation

### Best Way to Show Your Project

1. **Run Local Frontend**
   ```bash
   cd document-policy-processor/frontend
   streamlit run app.py
   ```

2. **Open in Browser**
   - Automatically opens at `http://localhost:8501`
   - Clean, professional interface
   - Easy to demonstrate

3. **Demo Flow**
   - Upload a sample medical document
   - Enter patient symptoms
   - Click "Process Document"
   - Show policy recommendations
   - Explain the matching logic

### Sample Documents for Demo

Located in `demo/sample_documents/`:
- `sample_hospital_bill.txt`
- `sample_medical_report.txt`
- `sample_prescription.txt`

---

## 🔍 Monitoring & Debugging

### View Real-Time Logs

**PowerShell:**
```powershell
aws logs tail /aws/lambda/DocumentPolicyProcessor --follow --region us-east-1
```

**CMD:**
```cmd
aws logs tail /aws/lambda/DocumentPolicyProcessor --follow --region us-east-1
```

### Check Lambda Status

```bash
aws lambda get-function --function-name DocumentPolicyProcessor --region us-east-1
```

### View API Gateway Usage

```bash
aws apigateway get-usage --usage-plan-id 4v3e6n --start-date 2026-03-01 --end-date 2026-03-31 --region us-east-1
```

---

## 🚨 Troubleshooting

### Issue: "Endpoint request timed out"

**Cause**: Lambda cold start (first request takes 30-60 seconds)

**Solution**: 
- Wait and try again
- Subsequent requests will be faster
- Or increase API Gateway timeout

### Issue: "Forbidden" or "Missing Authentication Token"

**Cause**: Missing or incorrect API key

**Solution**:
```bash
# Add header
-H "X-Api-Key: 9wx9nHe2NV5vSAOyRps9l3c7PpQ19OttaJqHw4mw"
```

### Issue: Frontend won't connect

**Cause**: API credentials not configured

**Solution**:
- Check `frontend/.streamlit/secrets.toml` exists
- Verify API URL and key are correct
- Restart Streamlit

### Issue: Lambda function errors

**Cause**: Missing Mistral AI code update

**Solution**:
- See `MISTRAL_AI_SETUP.md` for code updates
- Or use OpenAI API key instead

---

## 📊 Usage Limits

Your current API limits:
- **Rate**: 10 requests/second
- **Burst**: 20 requests
- **Daily Quota**: 1000 requests

To increase limits:
```bash
aws apigateway update-usage-plan \
  --usage-plan-id 4v3e6n \
  --patch-operations op=replace,path=/throttle/rateLimit,value=100 \
  --region us-east-1
```

---

## 🎯 Quick Access Checklist

- [ ] Test API health endpoint
- [ ] Access AWS Lambda console
- [ ] View CloudWatch logs
- [ ] Check DynamoDB tables
- [ ] Browse S3 bucket
- [ ] Run local frontend
- [ ] Test with sample documents
- [ ] Monitor API usage
- [ ] Record demo video

---

## 🔗 All Your Links

| Resource | URL |
|----------|-----|
| **API Endpoint** | https://bmi41mg6uf.execute-api.us-east-1.amazonaws.com/prod |
| **Lambda Console** | https://console.aws.amazon.com/lambda/home?region=us-east-1#/functions/DocumentPolicyProcessor |
| **API Gateway Console** | https://console.aws.amazon.com/apigateway/home?region=us-east-1#/apis/bmi41mg6uf |
| **S3 Console** | https://s3.console.aws.amazon.com/s3/buckets/document-policy-processor-uploads |
| **DynamoDB Console** | https://console.aws.amazon.com/dynamodbv2/home?region=us-east-1#tables |
| **CloudWatch Console** | https://console.aws.amazon.com/cloudwatch/home?region=us-east-1 |

---

## 🎬 Ready to Demo!

Your application is fully deployed and accessible. For the best demo experience:

1. Run the local frontend: `streamlit run app.py`
2. Use sample documents from `demo/sample_documents/`
3. Show the policy matching in action
4. Explain the AWS architecture

**Good luck with your hackathon! 🚀**

---

*Need help? Check `AWS_DEPLOYMENT_INFO.md` for detailed information.*
