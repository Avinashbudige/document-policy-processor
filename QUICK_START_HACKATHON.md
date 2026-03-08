# 🚀 Quick Start - Hackathon Demo

**Everything is ready! Just follow these simple steps.**

---

## ✅ What's Already Done

- ✅ AWS Lambda deployed with all endpoints
- ✅ API Gateway configured and tested
- ✅ S3 bucket ready for uploads
- ✅ DynamoDB with 3 sample policies
- ✅ Policy embeddings generated
- ✅ Mistral AI configured
- ✅ Frontend running and connected

---

## 🎯 Access Your Application

### Open the Frontend
**Click this link**: http://localhost:8502

Or open your browser and go to:
- Local: `http://localhost:8502`
- Network: `http://192.168.1.9:8502`

---

## 📝 How to Use

### Step 1: Upload Document
1. Click "Browse files" or drag & drop
2. Supported formats: PDF, PNG, JPG, JPEG, TXT
3. Example: Medical report, hospital bill, prescription

### Step 2: Enter Symptoms
Type patient symptoms in the text area:
- Example: "Diabetes, high blood sugar, frequent urination"
- Example: "Chest pain, shortness of breath, fatigue"
- Example: "Fever, cough, body aches"

### Step 3: Process
Click "Process Document" button

### Step 4: View Results
See policy recommendations with:
- Policy name and ID
- Claim/Reject decision
- Confidence score
- Reasoning
- Next steps

---

## 🧪 Test with Sample Data

### Sample Documents
Located in: `demo/sample_documents/`

1. **sample_hospital_bill.txt**
   - Symptoms: "Diabetes treatment, insulin therapy"
   
2. **sample_medical_report.txt**
   - Symptoms: "Chest pain, cardiac evaluation"
   
3. **sample_prescription.txt**
   - Symptoms: "High blood pressure, hypertension"

---

## 🔌 Backend Endpoints (For Reference)

### Base URL
```
https://bmi41mg6uf.execute-api.us-east-1.amazonaws.com/prod
```

### API Key
```
9wx9nHe2NV5vSAOyRps9l3c7PpQ19OttaJqHw4mw
```

### Available Endpoints
- `GET /api/health` - Health check
- `POST /api/upload-url` - Get upload URL
- `POST /api/process-document` - Process document
- `GET /api/status/{jobId}` - Check status
- `GET /api/results/{jobId}` - Get results

**Note**: Frontend handles all API calls automatically!

---

## 📊 Sample Policies in System

### 1. Basic Health Insurance (POL-001)
- Coverage: Hospitalization, surgery, diagnostics
- Exclusions: Pre-existing conditions, cosmetic procedures

### 2. Comprehensive Health Plan (POL-002)
- Coverage: All medical expenses, preventive care
- Exclusions: Experimental treatments, alternative medicine

### 3. Critical Illness Cover (POL-003)
- Coverage: Cancer, heart attack, stroke, organ transplant
- Exclusions: Self-inflicted injuries, substance abuse

---

## ⚡ Performance Tips

### First Request
- May take 30-60 seconds (Lambda cold start)
- Loading ML models takes time
- Be patient!

### Subsequent Requests
- Much faster (5-20 seconds)
- Lambda stays warm
- Models already loaded

---

## 🎬 Demo Script

### 1. Introduction (30 seconds)
"This is an AI-powered insurance policy processor that analyzes medical documents and matches them with relevant policies."

### 2. Upload Document (30 seconds)
- Show file upload interface
- Upload sample hospital bill
- Enter symptoms

### 3. Processing (1 minute)
- Click "Process Document"
- Show processing indicator
- Explain what's happening:
  - Text extraction from document
  - Embedding generation
  - Policy matching with AI
  - Exclusion checking with LLM
  - Recommendation generation

### 4. Results (1 minute)
- Show policy recommendations
- Highlight confidence scores
- Explain reasoning
- Show next steps

### 5. Architecture (30 seconds)
- Mention AWS services: Lambda, S3, DynamoDB, API Gateway
- Mention AI: Sentence Transformers, Mistral AI
- Mention scalability and serverless

**Total: 3-4 minutes**

---

## 🐛 Troubleshooting

### Frontend Not Loading?
```cmd
cd document-policy-processor\frontend
streamlit run app.py
```

### API Errors?
Check Lambda logs:
```bash
aws logs tail /aws/lambda/DocumentPolicyProcessor --follow --region us-east-1
```

### Slow Processing?
- First request is always slow (cold start)
- Wait 30-60 seconds
- Subsequent requests are faster

---

## 📞 Quick Reference

```
Frontend:  http://localhost:8502
API Base:  https://bmi41mg6uf.execute-api.us-east-1.amazonaws.com/prod
API Key:   9wx9nHe2NV5vSAOyRps9l3c7PpQ19OttaJqHw4mw
Region:    us-east-1
```

---

## 🎉 You're All Set!

**Just open http://localhost:8502 and start your demo!**

Good luck with your hackathon! 🚀

---

*Last updated: March 8, 2026*
