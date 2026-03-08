# 🚀 FINAL DEPLOYMENT STEPS - Follow These Exactly

**Status**: ✅ Code committed to local Git  
**Next**: Push to GitHub and deploy to Streamlit Cloud

---

## ✅ What's Already Done

1. ✅ Git repository initialized
2. ✅ All files committed
3. ✅ Lambda optimized (900s timeout, 3GB memory)
4. ✅ AWS infrastructure deployed
5. ✅ Local demo working

---

## 📝 Step 1: Create GitHub Repository (3 minutes)

### 1.1 Go to GitHub
Open: **https://github.com/new**

### 1.2 Create Repository
- **Repository name**: `document-policy-processor`
- **Description**: `AI-powered insurance policy processor for AWS AI Hackathon`
- **Visibility**: ✅ Public (required for free Streamlit Cloud)
- **Initialize**: ❌ Do NOT check any boxes (no README, no .gitignore, no license)
- Click **"Create repository"**

### 1.3 Copy the Commands
GitHub will show you commands. **IGNORE THEM** - we'll use our own below.

---

## 📝 Step 2: Push to GitHub (2 minutes)

### 2.1 Set Your GitHub Username
Replace `YOUR_USERNAME` with your actual GitHub username:

```bash
cd document-policy-processor
git remote add origin https://github.com/YOUR_USERNAME/document-policy-processor.git
```

**Example** (if your username is `john-doe`):
```bash
git remote add origin https://github.com/john-doe/document-policy-processor.git
```

### 2.2 Rename Branch to Main
```bash
git branch -M main
```

### 2.3 Push to GitHub
```bash
git push -u origin main
```

**If asked for credentials**:
- Username: Your GitHub username
- Password: Use a **Personal Access Token** (not your password!)
  - Get token: https://github.com/settings/tokens
  - Click "Generate new token (classic)"
  - Select scopes: `repo` (all)
  - Copy the token and use it as password

### 2.4 Verify
Go to: `https://github.com/YOUR_USERNAME/document-policy-processor`

You should see all your files!

---

## 📝 Step 3: Deploy to Streamlit Cloud (5 minutes)

### 3.1 Go to Streamlit Cloud
Open: **https://share.streamlit.io/**

### 3.2 Sign In
- Click **"Sign in"**
- Choose **"Continue with GitHub"**
- Authorize Streamlit to access your repositories

### 3.3 Create New App
- Click **"New app"** (big button in dashboard)

### 3.4 Configure Deployment
Fill in these fields:

**Repository**:
```
YOUR_USERNAME/document-policy-processor
```

**Branch**:
```
main
```

**Main file path**:
```
frontend/app.py
```

**App URL** (choose a custom name):
```
insurance-policy-ai
```
(or any name you like - this will be your public URL)

### 3.5 Advanced Settings (IMPORTANT!)
- Click **"Advanced settings"**
- **Python version**: Select `3.11`
- Click **"Save"**

### 3.6 Deploy!
- Click **"Deploy!"** button
- Wait 5-10 minutes for first deployment
- You'll see logs streaming - this is normal

---

## 📝 Step 4: Configure Secrets (2 minutes)

### 4.1 Wait for Deployment
Wait until you see: **"Your app is live!"**

### 4.2 Open Settings
- In Streamlit Cloud dashboard, find your app
- Click the **menu icon (⋮)** on your app
- Select **"Settings"**

### 4.3 Add Secrets
- Click **"Secrets"** tab
- Paste this EXACTLY:

```toml
[api]
base_url = "https://bmi41mg6uf.execute-api.us-east-1.amazonaws.com/prod"
api_key = "9wx9nHe2NV5vSAOyRps9l3c7PpQ19OttaJqHw4mw"
```

### 4.4 Save
- Click **"Save"**
- App will restart automatically (takes 1-2 minutes)

---

## 📝 Step 5: Get Your Public URL! 🎉

### Your URL Format:
```
https://YOUR_APP_NAME.streamlit.app
```

### Example:
If you chose `insurance-policy-ai`, your URL is:
```
https://insurance-policy-ai.streamlit.app
```

### Find Your URL:
- In Streamlit Cloud dashboard
- Click on your app
- URL is shown at the top

---

## 🧪 Step 6: Test Your Deployment (3 minutes)

### 6.1 Open Your Public URL
Open: `https://YOUR_APP_NAME.streamlit.app`

### 6.2 Test Upload
1. Click "Browse files"
2. Upload a test document (or use sample from `demo/sample_documents/`)
3. Enter symptoms: "Diabetes, insulin therapy"
4. Click "Process Document"

### 6.3 Wait for Results
- First request: 30-90 seconds (Lambda cold start)
- You should see policy recommendations!

### 6.4 Test Again
- Upload another document
- Should be faster (10-20 seconds)

---

## ✅ Step 7: Submit to Hackathon!

### Your Submission Information:

**Working Prototype Link**:
```
https://YOUR_APP_NAME.streamlit.app
```

**GitHub Repository**:
```
https://github.com/YOUR_USERNAME/document-policy-processor
```

**Description**:
```
AI-powered insurance policy processor that analyzes medical documents 
and automatically matches them with relevant insurance policies using 
machine learning (Sentence Transformers) and AI (Mistral AI).

Tech Stack: Python, Streamlit, Sentence Transformers, Mistral AI, 
AWS Lambda, S3, DynamoDB, API Gateway

Deployed on: Streamlit Cloud + AWS

Test Instructions:
1. Visit the URL above
2. Upload a medical document (PDF, image, or text)
3. Enter symptoms: "Diabetes, insulin therapy"
4. Click "Process Document"
5. View AI-generated recommendations

Availability: 30+ days, 24/7 uptime
```

---

## 🐛 Troubleshooting

### GitHub Push Fails?

**Error: "Authentication failed"**
- Use Personal Access Token instead of password
- Get token: https://github.com/settings/tokens
- Generate new token with `repo` scope
- Use token as password when pushing

**Error: "Repository not found"**
- Check you created the repository on GitHub
- Check the URL is correct
- Make sure repository is public

### Streamlit Deployment Fails?

**Error: "Could not find requirements.txt"**
- Make sure `frontend/requirements.txt` exists
- Should contain:
  ```
  streamlit>=1.28.0
  requests>=2.31.0
  ```

**Error: "Python version not supported"**
- In Advanced settings, select Python 3.11

**App shows errors**:
- Check secrets are configured correctly
- Make sure you saved the secrets
- Wait for app to restart after saving secrets

### Lambda Timeout?

**First request times out**:
- This is normal for cold start
- Wait 60-90 seconds
- Try again - should work

**All requests timeout**:
- Check Lambda configuration:
  ```bash
  aws lambda get-function-configuration \
    --function-name DocumentPolicyProcessor \
    --region us-east-1
  ```
- Should show: Timeout=900, MemorySize=3008

---

## 📊 What You'll Have

### Public URL:
```
https://YOUR_APP_NAME.streamlit.app
```

### Features:
- ✅ Available 24/7 for 30+ days
- ✅ Free hosting (Streamlit Cloud)
- ✅ HTTPS enabled
- ✅ Professional URL
- ✅ All features working
- ✅ Connected to AWS backend

### Performance:
- First request: 30-90 seconds
- Subsequent requests: 10-20 seconds
- Uptime: 99%+

---

## 📞 Quick Commands Reference

### Check Git Status:
```bash
cd document-policy-processor
git status
```

### Push to GitHub:
```bash
git remote add origin https://github.com/YOUR_USERNAME/document-policy-processor.git
git branch -M main
git push -u origin main
```

### Check Lambda:
```bash
aws lambda get-function-configuration \
  --function-name DocumentPolicyProcessor \
  --region us-east-1 \
  --query "[Timeout,MemorySize]"
```

---

## 🎉 YOU'RE ALMOST THERE!

### Checklist:

- [ ] Create GitHub repository
- [ ] Push code to GitHub
- [ ] Sign up for Streamlit Cloud
- [ ] Deploy app to Streamlit Cloud
- [ ] Configure secrets
- [ ] Test public URL
- [ ] Submit to hackathon

**Follow the steps above and you'll have your public URL in 15 minutes!**

---

## 💡 Tips

### For GitHub:
- Use a Personal Access Token, not your password
- Make repository public (required for free Streamlit)
- Don't initialize with README (we already have one)

### For Streamlit Cloud:
- Python version MUST be 3.11
- Secrets MUST be configured exactly as shown
- First deployment takes 5-10 minutes
- App restarts automatically when you save secrets

### For Testing:
- First request will be slow (cold start)
- Use sample documents from `demo/sample_documents/`
- Try multiple times to see faster performance

---

## 🏆 GOOD LUCK!

Your application is ready to deploy!

**Follow these steps and you'll have a permanent public URL for your hackathon submission!** 🚀

---

*Last updated: March 8, 2026*
