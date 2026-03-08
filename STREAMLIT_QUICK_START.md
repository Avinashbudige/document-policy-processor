# 🚀 Streamlit Frontend Quick Start

**Get your frontend running in 3 easy steps!**

---

## Method 1: Double-Click to Start (Easiest)

1. **Navigate to the frontend folder**
   ```
   document-policy-processor/frontend/
   ```

2. **Double-click this file:**
   ```
   START_FRONTEND.bat
   ```

3. **Wait for browser to open**
   - The app will automatically open at `http://localhost:8501`
   - If it doesn't open automatically, manually go to that URL

That's it! 🎉

---

## Method 2: Command Line

### Step 1: Open Command Prompt

Press `Win + R`, type `cmd`, press Enter

### Step 2: Navigate to Frontend Directory

```cmd
cd document-policy-processor\frontend
```

### Step 3: Install Dependencies (First Time Only)

```cmd
pip install streamlit requests boto3
```

### Step 4: Run the App

```cmd
streamlit run app.py
```

The app will open in your browser at `http://localhost:8501`

---

## 🎯 Using the Frontend

### 1. Upload a Document

Click "Browse files" and select:
- PDF document
- Image (PNG, JPG)
- Text file (TXT)

**Sample documents available in:**
```
document-policy-processor/demo/sample_documents/
```

### 2. Describe Symptoms

Enter patient symptoms or medical condition:
```
Example: "Patient diagnosed with Type 2 Diabetes requiring insulin therapy. 
Experiencing high blood sugar levels and increased thirst."
```

### 3. Process Document

Click "🔍 Process Document" button

### 4. View Results

- See matched policies
- View recommendations
- Check confidence scores
- Download results as JSON

---

## 📁 Sample Documents for Testing

Located in `demo/sample_documents/`:

1. **sample_hospital_bill.txt**
   - Hospital admission for diabetes treatment
   - Use with symptoms: "Diagnosed with diabetes, requiring hospitalization"

2. **sample_medical_report.txt**
   - Medical examination report
   - Use with symptoms: "Routine health checkup, preventive care"

3. **sample_prescription.txt**
   - Prescription for diabetes medication
   - Use with symptoms: "Type 2 diabetes, requiring insulin therapy"

---

## 🔧 Troubleshooting

### Issue: "Module not found: streamlit"

**Solution:**
```cmd
pip install streamlit requests boto3
```

### Issue: "Cannot connect to API"

**Solution:**
1. Check if secrets file exists: `frontend/.streamlit/secrets.toml`
2. Verify API URL is correct
3. Test API health in sidebar: Click "🏥 Check API Health"

### Issue: "Port 8501 already in use"

**Solution:**
```cmd
# Stop existing Streamlit process
taskkill /F /IM streamlit.exe

# Or use a different port
streamlit run app.py --server.port 8502
```

### Issue: Browser doesn't open automatically

**Solution:**
Manually open: `http://localhost:8501`

### Issue: "Endpoint request timed out"

**Cause:** Lambda cold start (first request takes 30-60 seconds)

**Solution:** 
- Wait and try again
- Subsequent requests will be faster

---

## 🎨 Features

### Main Interface
- ✅ Document upload (PDF, images, text)
- ✅ Symptom description input
- ✅ Real-time processing status
- ✅ Progress bar with updates

### Results Display
- ✅ Policy recommendations with confidence scores
- ✅ Priority-based sorting (High/Medium/Low)
- ✅ Detailed reasoning for each recommendation
- ✅ Next steps guidance
- ✅ Download results as JSON

### Sidebar
- ✅ About section
- ✅ Technical details
- ✅ API health check
- ✅ Support information

---

## 🎥 Demo Flow (For Presentation)

### 1. Start the App
```cmd
cd document-policy-processor\frontend
streamlit run app.py
```

### 2. Show the Interface
- Point out the clean, professional design
- Explain the upload and symptom input

### 3. Upload Sample Document
- Use `demo/sample_documents/sample_hospital_bill.txt`
- Enter symptoms: "Diagnosed with Type 2 Diabetes requiring insulin therapy"

### 4. Process and Show Results
- Watch the progress bar
- Explain the processing steps
- Show the matched policies
- Highlight confidence scores
- Explain the recommendations

### 5. Show Technical Details
- Click sidebar to show AWS services used
- Explain the AI technologies
- Run API health check

### 6. Download Results
- Click "Download Results as JSON"
- Show the structured output

---

## 📊 What Happens Behind the Scenes

When you click "Process Document":

1. **Upload** → Document uploaded to S3
2. **Extract** → AWS Textract extracts text
3. **Embed** → Generate embeddings using sentence-transformers
4. **Match** → Find similar policies in DynamoDB
5. **Check** → LLM validates exclusions (Mistral AI)
6. **Recommend** → Generate recommendations
7. **Display** → Show results in UI

---

## 🔑 API Configuration

Your API credentials are stored in:
```
frontend/.streamlit/secrets.toml
```

**Current Configuration:**
```toml
[api]
base_url = "https://bmi41mg6uf.execute-api.us-east-1.amazonaws.com/prod"
api_key = "9wx9nHe2NV5vSAOyRps9l3c7PpQ19OttaJqHw4mw"
```

**Don't share these credentials publicly!**

---

## 🎬 Recording Your Demo

### Before Recording:
1. ✅ Test the app works
2. ✅ Prepare sample documents
3. ✅ Write down symptom descriptions
4. ✅ Close unnecessary browser tabs
5. ✅ Set browser zoom to 100%

### During Recording:
1. Show the homepage
2. Explain the purpose
3. Upload a document
4. Enter symptoms
5. Click process
6. Explain the results
7. Show confidence scores
8. Download results

### Tips:
- Speak clearly and slowly
- Explain what you're doing
- Highlight key features
- Show the AWS architecture
- Mention AI technologies used

---

## 🚀 Ready to Go!

Your Streamlit frontend is configured and ready to use!

**Quick Start:**
```cmd
cd document-policy-processor\frontend
streamlit run app.py
```

Or just double-click: `START_FRONTEND.bat`

**Good luck with your demo! 🎉**

---

## 📞 Need Help?

- Check `HOW_TO_ACCESS.md` for more access methods
- See `AWS_DEPLOYMENT_INFO.md` for API details
- Review `DEPLOYMENT_COMPLETE.md` for full deployment info

---

*Last updated: March 8, 2026*
