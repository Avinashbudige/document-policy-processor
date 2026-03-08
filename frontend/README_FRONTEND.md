# 🎯 Streamlit Frontend - Complete Guide

**Your Document Policy Processor is ready to use!**

---

## 🚀 Quick Start (3 Steps)

### Step 1: Open Command Prompt
```cmd
# Press Win + R, type "cmd", press Enter
```

### Step 2: Navigate to Frontend
```cmd
cd document-policy-processor\frontend
```

### Step 3: Run the App
```cmd
streamlit run app.py
```

**That's it!** The app opens at `http://localhost:8501`

---

## 🎬 Even Easier: One-Click Start

**Just double-click this file:**
```
START_FRONTEND.bat
```

It will:
- ✅ Check Python installation
- ✅ Install required packages
- ✅ Create configuration files
- ✅ Start the Streamlit app
- ✅ Open your browser automatically

---

## 📋 What You Need

### Already Installed ✅
- Python 3.12.2
- AWS CLI configured
- API deployed and running

### Will Be Installed Automatically
- Streamlit (web framework)
- Requests (HTTP library)
- Boto3 (AWS SDK)

---

## 🎨 App Features

### Upload Section
- **Supported Formats**: PDF, PNG, JPG, TXT
- **Max File Size**: 10 MB
- **Upload Method**: Direct to S3 via presigned URL

### Symptom Input
- **Text Area**: Multi-line input
- **Minimum Length**: 10 characters
- **Example Provided**: Yes

### Processing
- **Real-time Progress**: Progress bar with status
- **Polling Interval**: 5 seconds
- **Max Wait Time**: 5 minutes
- **Status Updates**: Live feedback

### Results Display
- **Recommendations**: Sorted by priority
- **Confidence Scores**: Visual indicators
- **Detailed Reasoning**: Expandable sections
- **Next Steps**: Action items
- **Download**: JSON export

---

## 📁 Test with Sample Documents

### Location
```
document-policy-processor/demo/sample_documents/
```

### Available Samples

#### 1. Hospital Bill
**File**: `sample_hospital_bill.txt`

**Symptoms to use**:
```
Patient admitted for diabetes treatment. Experiencing high blood sugar 
levels requiring insulin therapy and monitoring.
```

**Expected Result**: Matches with Diabetes Care Plan policy

#### 2. Medical Report
**File**: `sample_medical_report.txt`

**Symptoms to use**:
```
Routine health checkup. No specific symptoms. Preventive care and 
general wellness examination.
```

**Expected Result**: Matches with Comprehensive Health Plus policy

#### 3. Prescription
**File**: `sample_prescription.txt`

**Symptoms to use**:
```
Type 2 Diabetes diagnosis. Prescribed insulin and blood sugar monitoring 
supplies. Requires ongoing medication management.
```

**Expected Result**: Matches with Diabetes Care Plan policy

---

## 🔧 Configuration

### API Credentials
Located in: `frontend/.streamlit/secrets.toml`

```toml
[api]
base_url = "https://bmi41mg6uf.execute-api.us-east-1.amazonaws.com/prod"
api_key = "9wx9nHe2NV5vSAOyRps9l3c7PpQ19OttaJqHw4mw"

[aws]
region = "us-east-1"
s3_bucket = "document-policy-processor-uploads"

[mistral]
api_key = "bzXoA00s7QBkSXuCEakYp0aY26TsjA8Vof"
model = "mistral-small-latest"
```

**⚠️ Keep these credentials private!**

---

## 🎯 Demo Workflow

### For Hackathon Presentation

#### 1. Introduction (30 seconds)
```
"This is the Document Policy Processor - an AI-powered system that 
analyzes medical documents and matches them with insurance policies."
```

#### 2. Show Interface (30 seconds)
- Point out the clean design
- Explain the two inputs: document + symptoms
- Mention AWS backend

#### 3. Upload Document (1 minute)
- Select `sample_hospital_bill.txt`
- Show file upload
- Enter symptoms
- Click "Process Document"

#### 4. Show Processing (30 seconds)
- Point out progress bar
- Explain what's happening:
  - Document uploaded to S3
  - Text extracted with Textract
  - Embeddings generated
  - Policies matched
  - LLM validates exclusions

#### 5. Show Results (1 minute)
- Highlight matched policies
- Explain confidence scores
- Show detailed reasoning
- Point out next steps
- Download results

#### 6. Technical Details (30 seconds)
- Open sidebar
- Show AWS services used
- Mention AI technologies
- Run health check

**Total Time**: ~3-4 minutes

---

## 🐛 Troubleshooting

### Problem: "streamlit: command not found"

**Solution**:
```cmd
pip install streamlit
```

### Problem: "Cannot connect to API"

**Check**:
1. Is the API URL correct in secrets.toml?
2. Is the API key correct?
3. Click "Check API Health" in sidebar

**Test API manually**:
```cmd
curl https://bmi41mg6uf.execute-api.us-east-1.amazonaws.com/prod/api/health
```

### Problem: "Endpoint request timed out"

**Cause**: Lambda cold start (first request)

**Solution**: 
- Wait 30-60 seconds
- Try again
- Subsequent requests will be faster

### Problem: "Port 8501 already in use"

**Solution**:
```cmd
# Kill existing process
taskkill /F /IM streamlit.exe

# Or use different port
streamlit run app.py --server.port 8502
```

### Problem: "File upload fails"

**Check**:
1. File size < 10 MB
2. File format is supported (PDF, PNG, JPG, TXT)
3. S3 bucket is accessible

### Problem: "No recommendations found"

**Possible Reasons**:
1. Document doesn't match any policies
2. Symptoms too vague
3. Document text extraction failed

**Solution**:
- Try different document
- Provide more detailed symptoms
- Check CloudWatch logs

---

## 📊 Understanding Results

### Confidence Scores

- **80-100%**: High Confidence (Green)
  - Policy definitely applies
  - Action: Proceed with claim

- **60-79%**: Medium Confidence (Yellow)
  - Policy likely applies
  - Action: Review details

- **0-59%**: Low Confidence (Red)
  - Policy may not apply
  - Action: Consult with expert

### Priority Levels

- **Priority 1** (High): Immediate action needed
- **Priority 2** (Medium): Review recommended
- **Priority 3** (Low): Optional consideration

### Actions

- **CLAIM**: Submit claim for this policy
- **REVIEW**: Review policy details carefully
- **EXCLUDE**: Policy doesn't apply

---

## 🎥 Recording Tips

### Before Recording

1. **Test Everything**
   - Run the app
   - Test with sample documents
   - Verify results appear correctly

2. **Prepare Environment**
   - Close unnecessary applications
   - Clear browser cache
   - Set zoom to 100%
   - Use incognito/private mode

3. **Prepare Script**
   - Write down what to say
   - Practice timing
   - Prepare sample data

### During Recording

1. **Screen Setup**
   - Full screen browser
   - Hide bookmarks bar
   - Close extra tabs

2. **Speaking**
   - Speak clearly and slowly
   - Explain each step
   - Highlight key features

3. **Demo Flow**
   - Show homepage
   - Upload document
   - Enter symptoms
   - Process
   - Show results
   - Explain recommendations

### After Recording

1. **Edit**
   - Trim unnecessary parts
   - Add title slide
   - Add captions if needed

2. **Export**
   - 1080p resolution
   - MP4 format
   - Under 100 MB if possible

---

## 🔗 Related Documentation

- **`STREAMLIT_QUICK_START.md`** - Quick start guide
- **`HOW_TO_ACCESS.md`** - All access methods
- **`AWS_DEPLOYMENT_INFO.md`** - API details
- **`DEPLOYMENT_COMPLETE.md`** - Deployment summary
- **`demo/VIDEO_CREATION_WALKTHROUGH.md`** - Video guide

---

## 🎉 You're Ready!

Your Streamlit frontend is fully configured and ready to use!

**Start the app now:**
```cmd
cd document-policy-processor\frontend
streamlit run app.py
```

Or double-click: **`START_FRONTEND.bat`**

**Good luck with your hackathon presentation! 🚀**

---

*Questions? Check the documentation files or AWS Console for logs.*
