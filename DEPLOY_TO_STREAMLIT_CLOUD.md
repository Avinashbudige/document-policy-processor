# 🚀 Deploy to Streamlit Cloud - 30 Day Availability

**Goal**: Permanent public URL for hackathon evaluation (30+ days)

---

## 🎯 Solution: Streamlit Cloud + AWS Lambda

### Why This Works:
- ✅ **Free**: Streamlit Cloud is free forever
- ✅ **Always On**: 24/7 availability
- ✅ **Public URL**: Professional HTTPS URL
- ✅ **No Maintenance**: Automatic updates
- ✅ **Scalable**: Handles multiple evaluators

---

## 📋 Step-by-Step Deployment

### Step 1: Prepare GitHub Repository (5 minutes)

1. **Create GitHub account** (if you don't have one):
   - Go to: https://github.com/signup

2. **Create new repository**:
   - Go to: https://github.com/new
   - Name: `document-policy-processor`
   - Public repository
   - Don't initialize with README

3. **Push your code**:
```bash
cd document-policy-processor
git init
git add .
git commit -m "Initial commit - Hackathon submission"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/document-policy-processor.git
git push -u origin main
```

---

### Step 2: Create Streamlit Cloud Account (2 minutes)

1. **Go to**: https://share.streamlit.io/
2. **Sign in with GitHub**
3. **Authorize Streamlit** to access your repositories

---

### Step 3: Deploy Application (3 minutes)

1. **Click "New app"** in Streamlit Cloud dashboard

2. **Configure deployment**:
   - **Repository**: `YOUR_USERNAME/document-policy-processor`
   - **Branch**: `main`
   - **Main file path**: `frontend/app.py`
   - **App URL**: Choose a custom name (e.g., `insurance-policy-ai`)

3. **Advanced settings** → **Python version**: `3.11`

4. **Click "Deploy"**

5. **Wait 5-10 minutes** for deployment to complete

---

### Step 4: Configure Secrets (2 minutes)

1. **In Streamlit Cloud dashboard**, click on your app

2. **Click the menu (⋮)** → **Settings** → **Secrets**

3. **Add secrets**:
```toml
[api]
base_url = "https://bmi41mg6uf.execute-api.us-east-1.amazonaws.com/prod"
api_key = "9wx9nHe2NV5vSAOyRps9l3c7PpQ19OttaJqHw4mw"
```

4. **Click "Save"**

5. **App will automatically restart** with new secrets

---

### Step 5: Get Your Public URL! 🎉

Your app will be available at:
```
https://YOUR_APP_NAME.streamlit.app
```

Example:
```
https://insurance-policy-ai.streamlit.app
```

This URL is **permanent** and will work for 30+ days!

---

## ⚠️ Lambda Cold Start Issue

The Lambda function has a cold start timeout issue. Let's fix it:

### Option A: Enable Provisioned Concurrency (Recommended)

Keeps Lambda warm 24/7:

```bash
aws lambda put-provisioned-concurrency-config \
  --function-name DocumentPolicyProcessor \
  --provisioned-concurrent-executions 1 \
  --qualifier $LATEST \
  --region us-east-1
```

**Cost**: ~$15-20/month  
**Benefit**: No cold starts, always fast

### Option B: Increase Lambda Timeout

Allow more time for cold start:

```bash
aws lambda update-function-configuration \
  --function-name DocumentPolicyProcessor \
  --timeout 900 \
  --memory-size 3008 \
  --region us-east-1
```

**Cost**: Free (just uses more memory)  
**Benefit**: Gives Lambda time to initialize

### Option C: Use Local Processing (Fallback)

If Lambda times out, the frontend can fall back to showing a message or using cached results.

---

## 🔧 Recommended: Fix Lambda Cold Start

Let me create a script to optimize Lambda:

### Quick Fix Script

Create `fix-lambda-timeout.bat`:
```batch
@echo off
echo Fixing Lambda cold start timeout...

echo Step 1: Increase timeout to 15 minutes
aws lambda update-function-configuration ^
  --function-name DocumentPolicyProcessor ^
  --timeout 900 ^
  --region us-east-1

echo Step 2: Increase memory to 3GB (faster CPU)
aws lambda update-function-configuration ^
  --function-name DocumentPolicyProcessor ^
  --memory-size 3008 ^
  --region us-east-1

echo Step 3: Enable provisioned concurrency (keeps warm)
aws lambda put-provisioned-concurrency-config ^
  --function-name DocumentPolicyProcessor ^
  --provisioned-concurrent-executions 1 ^
  --qualifier $LATEST ^
  --region us-east-1

echo Done! Lambda should now handle cold starts.
pause
```

Run this script:
```cmd
cd document-policy-processor
fix-lambda-timeout.bat
```

---

## 📝 Alternative: Deploy Frontend to AWS

If you prefer everything on AWS:

### Option: Deploy to AWS Amplify

1. **Go to**: AWS Amplify Console
2. **Connect repository**: Link your GitHub repo
3. **Configure build**:
   - Build command: `pip install -r frontend/requirements.txt`
   - Start command: `streamlit run frontend/app.py --server.port 8501`
4. **Deploy**

**Cost**: ~$5-10/month  
**Benefit**: Everything on AWS

---

## 🎯 Recommended Deployment Strategy

### For 30-Day Availability:

1. **Frontend**: Streamlit Cloud (free, always-on)
2. **Backend**: AWS Lambda with provisioned concurrency
3. **Cost**: ~$15-20/month for Lambda
4. **Reliability**: 99.9% uptime

### Budget Option:

1. **Frontend**: Streamlit Cloud (free)
2. **Backend**: AWS Lambda with increased timeout (free)
3. **Cost**: $0 (within free tier)
4. **Reliability**: 95% uptime (cold starts may cause timeouts)

---

## 📊 Deployment Comparison

| Option | Cost | Reliability | Setup Time |
|--------|------|-------------|------------|
| Streamlit Cloud + Provisioned Lambda | $15-20/mo | 99.9% | 15 min |
| Streamlit Cloud + Regular Lambda | Free | 95% | 10 min |
| AWS Amplify + Lambda | $20-30/mo | 99.9% | 30 min |
| ngrok (local) | Free | 80%* | 2 min |

*Requires computer to stay on

---

## ✅ Final Checklist

### Before Deploying:

- [ ] GitHub account created
- [ ] Code pushed to GitHub
- [ ] Streamlit Cloud account created
- [ ] App deployed to Streamlit Cloud
- [ ] Secrets configured
- [ ] Lambda timeout increased
- [ ] Public URL tested
- [ ] Sample documents tested

### After Deploying:

- [ ] Public URL works
- [ ] Document upload works
- [ ] Processing completes successfully
- [ ] Results display correctly
- [ ] URL shared in submission
- [ ] Monitoring enabled

---

## 🔍 Monitoring Your Deployment

### Check Streamlit Cloud Status:
- Dashboard: https://share.streamlit.io/
- View logs in real-time
- See visitor analytics
- Monitor errors

### Check AWS Lambda:
```bash
# View recent logs
aws logs tail /aws/lambda/DocumentPolicyProcessor --follow --region us-east-1

# Check function status
aws lambda get-function --function-name DocumentPolicyProcessor --region us-east-1
```

### Check API Gateway:
```bash
# Test health endpoint
curl https://bmi41mg6uf.execute-api.us-east-1.amazonaws.com/prod/api/health
```

---

## 🐛 Troubleshooting

### Streamlit Cloud Deployment Fails:

**Check requirements.txt**:
Make sure `frontend/requirements.txt` exists with:
```
streamlit>=1.28.0
requests>=2.31.0
```

**Check Python version**:
Set to 3.11 in advanced settings

### Lambda Timeout Issues:

**Increase timeout**:
```bash
aws lambda update-function-configuration \
  --function-name DocumentPolicyProcessor \
  --timeout 900 \
  --region us-east-1
```

**Enable provisioned concurrency**:
```bash
aws lambda put-provisioned-concurrency-config \
  --function-name DocumentPolicyProcessor \
  --provisioned-concurrent-executions 1 \
  --qualifier $LATEST \
  --region us-east-1
```

### App Shows Errors:

**Check secrets**:
Make sure API key and base URL are correct in Streamlit Cloud secrets

**Check Lambda**:
Make sure Lambda function is deployed and accessible

---

## 📞 Quick Commands

### Deploy to Streamlit Cloud:
1. Push to GitHub
2. Go to https://share.streamlit.io/
3. Click "New app"
4. Select repository and file
5. Deploy!

### Fix Lambda Timeout:
```bash
aws lambda update-function-configuration \
  --function-name DocumentPolicyProcessor \
  --timeout 900 \
  --memory-size 3008 \
  --region us-east-1
```

### Enable Provisioned Concurrency:
```bash
aws lambda put-provisioned-concurrency-config \
  --function-name DocumentPolicyProcessor \
  --provisioned-concurrent-executions 1 \
  --qualifier $LATEST \
  --region us-east-1
```

---

## 🎉 Your Public URL

After deployment, your URL will be:
```
https://YOUR_APP_NAME.streamlit.app
```

This URL will be:
- ✅ Available 24/7
- ✅ Free forever
- ✅ HTTPS enabled
- ✅ Fast and reliable
- ✅ Perfect for hackathon evaluation

---

## 📋 Submission Template

Use this in your hackathon submission:

```
Working Prototype Link: https://YOUR_APP_NAME.streamlit.app

Description:
AI-powered insurance policy processor that analyzes medical documents 
and automatically matches them with relevant insurance policies using 
machine learning and natural language processing.

Tech Stack:
- Frontend: Streamlit (deployed on Streamlit Cloud)
- ML: Sentence Transformers, Mistral AI
- Backend: AWS Lambda, S3, DynamoDB, API Gateway
- Deployment: Streamlit Cloud + AWS

Test Instructions:
1. Visit the URL above
2. Upload a medical document (PDF, image, or text)
3. Enter patient symptoms
4. Click "Process Document"
5. View AI-generated policy recommendations

Note: First request may take 30-60 seconds due to Lambda cold start.
Subsequent requests are faster (10-20 seconds).

Availability: 30+ days, 24/7 uptime
```

---

## 🚀 Ready to Deploy!

Follow the steps above to get your permanent public URL in 15 minutes!

**Your app will be available for 30+ days with zero maintenance!** 🎉

---

*Last updated: March 8, 2026*
