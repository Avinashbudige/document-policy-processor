# 🌐 Public Deployment Options for Hackathon

**Requirement**: Live URL for evaluators to test

---

## 🎯 Recommended Solution: Streamlit Cloud + AWS Lambda

### Option 1: Streamlit Cloud (FASTEST - 5 minutes)

Deploy your frontend to Streamlit Cloud for free public access.

#### Steps:

1. **Push code to GitHub** (if not already):
```bash
cd document-policy-processor
git init
git add .
git commit -m "Hackathon submission"
git remote add origin https://github.com/YOUR_USERNAME/document-policy-processor.git
git push -u origin main
```

2. **Deploy to Streamlit Cloud**:
   - Go to https://share.streamlit.io/
   - Sign in with GitHub
   - Click "New app"
   - Select your repository
   - Main file: `frontend/app.py`
   - Click "Deploy"

3. **Configure Secrets**:
   - In Streamlit Cloud dashboard, go to app settings
   - Add secrets:
```toml
[api]
base_url = "https://bmi41mg6uf.execute-api.us-east-1.amazonaws.com/prod"
api_key = "9wx9nHe2NV5vSAOyRps9l3c7PpQ19OttaJqHw4mw"
```

4. **Get Public URL**:
   - Streamlit will give you a URL like: `https://YOUR_APP.streamlit.app`
   - Share this URL with evaluators!

**Pros**:
- ✅ Free
- ✅ Public URL in 5 minutes
- ✅ HTTPS enabled
- ✅ Easy to update
- ✅ No server management

**Cons**:
- ⚠️ Still has Lambda cold start issue (need to fix)

---

### Option 2: Fix Lambda + Streamlit Cloud (BEST)

Fix the Lambda cold start, then deploy frontend to Streamlit Cloud.

#### Fix Lambda Cold Start:

The issue is Lambda initialization timeout. We need to reduce import time.

**Quick Fix**: Increase Lambda timeout and use smaller model

1. **Update Lambda timeout**:
```bash
aws lambda update-function-configuration \
  --function-name DocumentPolicyProcessor \
  --timeout 900 \
  --region us-east-1
```

2. **Update Lambda memory** (more memory = faster CPU):
```bash
aws lambda update-function-configuration \
  --function-name DocumentPolicyProcessor \
  --memory-size 3008 \
  --region us-east-1
```

3. **Enable Provisioned Concurrency** (keeps Lambda warm):
```bash
aws lambda put-provisioned-concurrency-config \
  --function-name DocumentPolicyProcessor \
  --provisioned-concurrent-executions 1 \
  --qualifier $LATEST \
  --region us-east-1
```

**Cost**: ~$15-20/month for provisioned concurrency

---

### Option 3: Deploy Frontend to EC2 (Alternative)

Deploy Streamlit app on AWS EC2 for full control.

#### Steps:

1. **Launch EC2 Instance**:
   - t2.micro (free tier)
   - Ubuntu 22.04
   - Open port 8501

2. **Install dependencies**:
```bash
sudo apt update
sudo apt install python3-pip
pip3 install streamlit requests
```

3. **Upload code and run**:
```bash
cd frontend
streamlit run app.py --server.port 8501 --server.address 0.0.0.0
```

4. **Get Public URL**:
   - Use EC2 public IP: `http://YOUR_EC2_IP:8501`

**Pros**:
- ✅ Full control
- ✅ Can run 24/7

**Cons**:
- ❌ Need to manage server
- ❌ HTTP only (not HTTPS)
- ❌ Costs money after free tier

---

### Option 4: Use Local Demo with ngrok (QUICK HACK)

Expose your local demo to the internet using ngrok.

#### Steps:

1. **Download ngrok**: https://ngrok.com/download

2. **Run your local demo**:
```cmd
cd document-policy-processor\frontend
streamlit run app_local_demo.py
```

3. **Expose with ngrok**:
```cmd
ngrok http 8503
```

4. **Get Public URL**:
   - ngrok will give you a URL like: `https://abc123.ngrok.io`
   - Share this URL with evaluators!

**Pros**:
- ✅ Instant (2 minutes)
- ✅ HTTPS enabled
- ✅ No AWS issues
- ✅ Free

**Cons**:
- ❌ Your computer must stay on
- ❌ URL changes each time
- ❌ Limited to 40 connections/minute (free tier)

---

## 🚀 FASTEST PATH TO LIVE URL (5 minutes)

### Use ngrok with Local Demo

This is the absolute fastest way to get a live URL:

1. **Start local demo**:
```cmd
cd document-policy-processor\frontend
streamlit run app_local_demo.py
```

2. **Download and run ngrok**:
   - Download: https://ngrok.com/download
   - Extract ngrok.exe
   - Run: `ngrok http 8503`

3. **Copy the HTTPS URL**:
   - ngrok shows: `Forwarding https://abc123.ngrok-free.app -> http://localhost:8503`
   - Copy the HTTPS URL

4. **Share with evaluators**:
   - Give them the ngrok URL
   - They can access your app from anywhere!

**This works immediately and requires no AWS fixes!**

---

## 📋 Comparison Table

| Option | Time | Cost | Reliability | Best For |
|--------|------|------|-------------|----------|
| ngrok + Local | 2 min | Free | Medium* | Quick demo |
| Streamlit Cloud | 5 min | Free | High | Public deployment |
| EC2 | 30 min | $5-10/mo | High | Full control |
| Lambda Fix | 1 hour | $15-20/mo | High | Production |

*Requires your computer to stay on

---

## 🎯 My Recommendation

### For Hackathon Evaluation:

**Use ngrok with local demo** because:
1. ✅ Works in 2 minutes
2. ✅ No AWS cold start issues
3. ✅ All features work perfectly
4. ✅ Free
5. ✅ HTTPS enabled
6. ✅ Can demo immediately

### For Long-term:

**Deploy to Streamlit Cloud** because:
1. ✅ Free forever
2. ✅ Always online
3. ✅ Professional URL
4. ✅ Easy to update
5. ✅ No server management

---

## 📝 Step-by-Step: ngrok Setup

### 1. Download ngrok
- Go to: https://ngrok.com/download
- Download for Windows
- Extract ngrok.exe to a folder

### 2. Start Local Demo
```cmd
cd document-policy-processor\frontend
streamlit run app_local_demo.py
```

Wait for: `Local URL: http://localhost:8503`

### 3. Run ngrok
Open new terminal:
```cmd
cd path\to\ngrok
ngrok http 8503
```

### 4. Get Public URL
ngrok will show:
```
Forwarding  https://abc123.ngrok-free.app -> http://localhost:8503
```

Copy the HTTPS URL!

### 5. Test
Open the ngrok URL in your browser - it should show your app!

### 6. Share
Give the ngrok URL to evaluators:
```
https://abc123.ngrok-free.app
```

---

## ⚠️ Important Notes

### ngrok Free Tier Limits:
- 40 connections/minute
- URL changes when you restart
- Session timeout after 2 hours (need to restart)

### To Keep URL Stable:
- Sign up for ngrok account (free)
- Get auth token
- Run: `ngrok config add-authtoken YOUR_TOKEN`
- Get static domain (paid) or use random URL (free)

### During Evaluation:
- Keep your computer on
- Keep both terminals running (Streamlit + ngrok)
- Monitor for any issues
- Have backup plan (local demo video)

---

## 🎬 Alternative: Record Demo Video

If live URL is problematic, record a demo video:

1. **Record screen** while using local demo
2. **Show all features** working
3. **Upload to YouTube** (unlisted)
4. **Share YouTube link**

This proves the app works without needing live access.

---

## 📞 Quick Commands

### Start Local Demo
```cmd
cd document-policy-processor\frontend
streamlit run app_local_demo.py
```

### Start ngrok
```cmd
ngrok http 8503
```

### Check if Running
Open: http://localhost:8503 (local)
Open: https://YOUR_NGROK_URL (public)

---

## 🎉 Ready to Deploy!

Choose your path:
1. **Fastest**: ngrok (2 minutes)
2. **Best**: Streamlit Cloud (5 minutes)
3. **Alternative**: Record video

**I recommend starting with ngrok right now to get a live URL immediately!**

---

*Last updated: March 8, 2026*
