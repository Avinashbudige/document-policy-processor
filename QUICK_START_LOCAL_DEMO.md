# Quick Start - Local Demo

**Ready to record your demo video in 3 steps!**

---

## 🚀 Step 1: Start the Demo (2 minutes)

Open Command Prompt in the `document-policy-processor` folder:

```cmd
run-local-demo.bat
```

**What happens:**
- Checks Python installation ✅
- Installs dependencies (if needed) ✅
- Starts Streamlit server ✅
- Opens browser to http://localhost:8501 ✅

**Expected output:**
```
========================================
Demo will open in your browser at:
http://localhost:8501
========================================
```

---

## 🎬 Step 2: Test the Demo (5 minutes)

### Quick Test Flow:

1. **Upload a document**
   - Use `demo/sample_documents/sample_hospital_bill.txt`
   - Or any PDF, image, or text file

2. **Enter symptoms**
   ```
   I underwent emergency surgery for appendicitis and was hospitalized for 3 days. 
   I need to know which insurance policies cover this procedure.
   ```

3. **Click "Process Document"**
   - Wait 2-3 seconds
   - See processing steps

4. **View results**
   - See 3 policy recommendations
   - Check confidence scores
   - Expand details to see reasoning

### Expected Results:

✅ **Comprehensive Health Insurance**
- Confidence: 85%
- Action: CLAIM
- Priority: High

⚠️ **Critical Illness Coverage**
- Confidence: 65%
- Action: REVIEW
- Priority: Medium

⚠️ **Accident Protection Plan**
- Confidence: 45%
- Action: REVIEW
- Priority: Low

---

## 📹 Step 3: Record Your Video (Follow the Script)

Use the script in `demo/COMPLETE_3MIN_SCRIPT.md`

### Key Points to Show:

1. **Introduction** (0:00-0:20)
   - "AI-powered insurance policy matching"
   - "Built on AWS services"

2. **Upload Demo** (0:20-0:40)
   - Show file upload
   - Enter symptoms
   - Click process

3. **Processing** (0:40-1:00)
   - Show AI at work
   - Mention AWS services

4. **Results** (1:00-2:30)
   - Highlight confidence scores
   - Show action recommendations
   - Expand details
   - Explain reasoning

5. **Architecture** (2:30-2:50)
   - Mention AWS services
   - Show scalability

6. **Conclusion** (2:50-3:00)
   - Recap benefits
   - Call to action

---

## 🛠️ Troubleshooting

### Demo won't start?
```cmd
cd document-policy-processor
test-local-demo.bat
```
This will check what's missing.

### Port already in use?
```cmd
cd frontend
streamlit run app_local_demo.py --server.port 8502
```

### Module not found?
```cmd
pip install streamlit requests sentence-transformers torch
```

---

## 📊 Sample Data

### Sample Documents (in `demo/sample_documents/`):

1. **sample_hospital_bill.txt**
   - Symptoms: "Emergency surgery for appendicitis"
   - Best match: Comprehensive Health Insurance

2. **sample_medical_report.txt**
   - Symptoms: "Heart condition requiring treatment"
   - Best match: Critical Illness Coverage

3. **sample_prescription.txt**
   - Symptoms: "Accident-related injuries"
   - Best match: Accident Protection Plan

### Sample Symptoms:

**For hospital bills:**
```
I was hospitalized for 3 days due to severe abdominal pain. 
Doctors performed emergency surgery for appendicitis. 
I need to file an insurance claim for the hospital bills.
```

**For critical illness:**
```
I was diagnosed with a heart condition that requires ongoing treatment. 
My doctor recommended cardiac surgery. 
I want to know which policies cover this condition.
```

**For accidents:**
```
I was injured in a car accident and required emergency treatment. 
I have fractures and need physical therapy. 
Which insurance policies cover accident-related injuries?
```

---

## ✅ Pre-Recording Checklist

- [ ] Demo running at http://localhost:8501
- [ ] Sample documents ready
- [ ] Symptoms prepared
- [ ] Recording software ready (OBS Studio / Loom)
- [ ] Microphone tested
- [ ] Browser clean (close extra tabs)
- [ ] Notifications disabled
- [ ] Script reviewed (`demo/COMPLETE_3MIN_SCRIPT.md`)

---

## 🎯 What to Emphasize

### 1. AI-Powered Intelligence
"Uses sentence transformers for semantic understanding"

### 2. AWS Cloud Architecture
"Built on AWS Lambda, S3, DynamoDB, Textract, and CloudWatch"

### 3. Clear Recommendations
"Provides confidence scores and actionable next steps"

### 4. Fast Processing
"Processes documents in seconds"

### 5. Scalable Design
"Ready for production deployment on AWS"

---

## 📝 After Recording

1. **Stop the demo**: Press Ctrl+C in Command Prompt

2. **Edit video**: Follow `demo/EDITING_CHECKLIST.md`

3. **Upload to YouTube**: Follow `demo/UPLOAD_INSTRUCTIONS.md`

4. **Update README**: Add video link

5. **Test submission**: Verify all links work

---

## 🎬 Recording Tips

### Do:
✅ Speak clearly and confidently
✅ Show the complete workflow
✅ Highlight key features
✅ Mention AWS services
✅ Keep under 3 minutes

### Don't:
❌ Rush through steps
❌ Skip error handling
❌ Forget to show results
❌ Ignore the architecture
❌ Go over 3 minutes

---

## 💡 Pro Tips

1. **Practice 2-3 times** before recording
2. **Use a script** but sound natural
3. **Show, don't just tell** - demonstrate features
4. **Highlight AWS** - judges care about cloud architecture
5. **Be enthusiastic** - show you're excited about the project

---

## 📞 Need Help?

### Common Issues:

**Q: Demo is slow?**
A: First run downloads AI models (~100MB). Subsequent runs are fast.

**Q: No recommendations shown?**
A: Make sure symptoms are detailed (at least 10 characters).

**Q: Want to customize policies?**
A: Edit `SAMPLE_POLICIES` in `frontend/app_local_demo.py`.

**Q: Recording quality poor?**
A: Use OBS Studio with 1080p, 30fps settings.

---

## 🚀 You're Ready!

Everything is set up. Just run:

```cmd
run-local-demo.bat
```

Then follow the script in `demo/COMPLETE_3MIN_SCRIPT.md` and record your video!

**Good luck with your demo!** 🎉

---

**Time Estimate:**
- Start demo: 2 minutes
- Test: 5 minutes
- Practice: 15 minutes
- Record: 30-60 minutes (multiple takes)
- **Total**: ~1 hour to first recording

**You've got this!** 💪
