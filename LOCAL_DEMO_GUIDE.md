# Local Demo Guide

**Quick Start for Hackathon Demo Video Recording**

This guide helps you run the Document Policy Processor locally for demo purposes without needing full AWS deployment.

---

## 🚀 Quick Start (5 Minutes)

### Step 1: Run the Demo

Open Command Prompt in the `document-policy-processor` folder and run:

```cmd
run-local-demo.bat
```

This will:
1. Check Python installation
2. Install required packages (streamlit, requests)
3. Start the local demo server
4. Open your browser to http://localhost:8501

### Step 2: Test the Application

1. **Upload a document** (any PDF, image, or text file)
2. **Enter symptoms** (e.g., "Severe headaches and dizziness for two weeks")
3. **Click "Process Document"**
4. **View recommendations** with confidence scores and next steps

### Step 3: Record Your Demo Video

Follow the script in `demo/COMPLETE_3MIN_SCRIPT.md` while the app is running.

---

## 📋 What's Different in Local Demo Mode?

### Local Demo Version:
- ✅ Runs entirely on your computer
- ✅ No AWS credentials needed
- ✅ Uses local Python modules for processing
- ✅ Simulates text extraction (no Textract API calls)
- ✅ Uses 3 sample policies for matching
- ✅ Perfect for demo video recording

### Production Version (AWS):
- Uses AWS Textract for OCR
- Stores documents in S3
- Queries DynamoDB for policies
- Runs on Lambda functions
- Accessible via API Gateway

---

## 🎬 Demo Video Tips

### Before Recording:

1. **Test the flow** 2-3 times to get comfortable
2. **Prepare sample documents** (use files from `demo/sample_documents/`)
3. **Have symptoms ready** (see `demo/SAMPLE_DATA.md`)
4. **Close unnecessary browser tabs**
5. **Set browser zoom to 100%**

### During Recording:

1. **Show the upload interface** clearly
2. **Explain what you're uploading** (e.g., "medical report")
3. **Read the symptoms** you're entering
4. **Wait for processing** (shows AI at work)
5. **Highlight key results**:
   - Confidence scores
   - Action recommendations
   - Reasoning
   - Next steps

### Sample Narration:

> "Let me show you how this works. I'll upload a medical report and describe my symptoms. The AI extracts text from the document, matches it against our policy database using semantic similarity, and provides clear recommendations. As you can see, it found 3 matching policies with confidence scores, tells me which actions to take, and explains the reasoning behind each recommendation."

---

## 🔧 Troubleshooting

### Issue: "Python not found"
**Solution**: Install Python 3.8+ from python.org

### Issue: "Module not found" errors
**Solution**: Install dependencies manually:
```cmd
cd frontend
pip install streamlit requests
cd ..
pip install -r requirements.txt
```

### Issue: Browser doesn't open automatically
**Solution**: Manually open http://localhost:8501

### Issue: "Port 8501 already in use"
**Solution**: 
1. Close any running Streamlit apps
2. Or use a different port:
```cmd
streamlit run frontend/app_local_demo.py --server.port 8502
```

### Issue: Processing fails
**Solution**: Check that you have all dependencies:
```cmd
pip install sentence-transformers torch numpy
```

---

## 📁 Sample Documents for Demo

Use these files from `demo/sample_documents/`:

1. **sample_hospital_bill.txt**
   - Symptoms: "Underwent emergency surgery for appendicitis"
   - Expected: Matches Comprehensive Health Insurance

2. **sample_medical_report.txt**
   - Symptoms: "Diagnosed with heart condition requiring treatment"
   - Expected: Matches Critical Illness Coverage

3. **sample_prescription.txt**
   - Symptoms: "Recovering from accident-related injuries"
   - Expected: Matches Accident Protection Plan

---

## 🎯 Demo Flow Checklist

- [ ] Start local demo server
- [ ] Browser opens to http://localhost:8501
- [ ] Upload sample document
- [ ] Enter symptom description
- [ ] Click "Process Document"
- [ ] Wait for processing (2-3 seconds)
- [ ] View results with recommendations
- [ ] Expand details to show reasoning
- [ ] Download results as JSON (optional)
- [ ] Process another document (optional)

---

## 💡 Key Features to Highlight

### 1. AI-Powered Text Extraction
"The system can process PDFs, images, and text files"

### 2. Semantic Policy Matching
"Uses sentence transformers to understand meaning, not just keywords"

### 3. Confidence Scoring
"Each recommendation includes a confidence score so you know how reliable it is"

### 4. Clear Actions
"Tells you exactly what to do: claim, review, or exclude"

### 5. Detailed Reasoning
"Explains why each policy matches your situation"

### 6. Next Steps
"Provides actionable next steps for each recommendation"

### 7. AWS-Ready Architecture
"Built on AWS services for scalability and reliability"

---

## 🏗️ Architecture to Mention

Even though running locally, emphasize the AWS architecture:

**AWS Services Used:**
- **Lambda**: Serverless compute for processing
- **API Gateway**: RESTful API endpoints
- **S3**: Document storage with versioning
- **DynamoDB**: Policy database with fast queries
- **Textract**: OCR for document text extraction
- **CloudWatch**: Monitoring and logging

**AI Technologies:**
- **Sentence Transformers**: Semantic embeddings
- **OpenAI GPT-3.5**: Exclusion checking
- **Cosine Similarity**: Policy matching

---

## 📊 Sample Results to Show

### High Confidence Match (80%+):
- ✅ Action: CLAIM
- 🔴 Priority: High
- Shows clear policy match

### Medium Confidence Match (60-80%):
- ⚠️ Action: REVIEW
- 🟡 Priority: Medium
- Suggests further review

### Low Confidence Match (<60%):
- ⚠️ Action: REVIEW
- 🟢 Priority: Low
- May not be applicable

---

## 🎥 Recording Setup

### Recommended Tools:
- **OBS Studio** (free, professional)
- **Windows Game Bar** (built-in, simple)
- **Loom** (easy, cloud-based)

### Settings:
- **Resolution**: 1920x1080 (1080p)
- **Frame Rate**: 30 fps
- **Audio**: Clear microphone
- **Duration**: Under 3 minutes

### Screen Layout:
- **Browser**: Full screen or maximized
- **Close**: Unnecessary tabs and windows
- **Zoom**: 100% (or 110% for better visibility)

---

## ✅ Pre-Recording Checklist

- [ ] Local demo running at http://localhost:8501
- [ ] Sample documents ready
- [ ] Symptom descriptions prepared
- [ ] Recording software tested
- [ ] Microphone working
- [ ] Script reviewed (demo/COMPLETE_3MIN_SCRIPT.md)
- [ ] Browser clean (no distracting tabs)
- [ ] Notifications disabled
- [ ] Good lighting (if showing face)
- [ ] Quiet environment

---

## 🚀 After Recording

1. **Stop the demo**: Press Ctrl+C in Command Prompt
2. **Edit video**: Follow `demo/EDITING_CHECKLIST.md`
3. **Upload to YouTube**: Follow `demo/UPLOAD_INSTRUCTIONS.md`
4. **Update README**: Add video link
5. **Test video link**: Verify it's accessible

---

## 📞 Need Help?

### Common Questions:

**Q: Do I need AWS credentials?**
A: No, local demo runs without AWS.

**Q: Will this work for the hackathon?**
A: Yes! Judges care about functionality, not deployment location.

**Q: Can I show this is AWS-ready?**
A: Yes! Mention the AWS infrastructure you've set up (S3, DynamoDB).

**Q: How long does processing take?**
A: 2-3 seconds in local demo mode.

**Q: Can I customize the sample policies?**
A: Yes, edit the `SAMPLE_POLICIES` list in `frontend/app_local_demo.py`.

---

## 🎯 Success Criteria

Your demo is ready when:
- ✅ App starts without errors
- ✅ You can upload documents
- ✅ Processing completes successfully
- ✅ Results display with recommendations
- ✅ You can explain the workflow confidently
- ✅ Recording quality is good

---

## 📝 Next Steps

1. **Run local demo**: `run-local-demo.bat`
2. **Test thoroughly**: Try different documents and symptoms
3. **Practice narration**: Use the script in `demo/COMPLETE_3MIN_SCRIPT.md`
4. **Record video**: Follow `demo/VIDEO_CREATION_WALKTHROUGH.md`
5. **Edit and upload**: Follow `demo/EDITING_CHECKLIST.md`
6. **Update documentation**: Add video link to README
7. **Submit to hackathon**: Include all deliverables

---

**Remember**: The goal is to demonstrate a working prototype. Local demo is perfect for this! 🚀

---

**Time Estimate:**
- Setup: 5 minutes
- Testing: 10 minutes
- Recording: 30-60 minutes (multiple takes)
- Editing: 30-60 minutes
- Upload: 15 minutes
- **Total**: 2-3 hours

**You've got this!** 💪
