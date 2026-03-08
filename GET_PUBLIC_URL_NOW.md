# 🌐 Get Public URL in 2 Minutes!

**For Hackathon Evaluators**

---

## 🚀 FASTEST METHOD: ngrok

### What You Need:
1. Your local demo running (already done! ✅)
2. ngrok (free tool to expose localhost)

---

## 📝 Step-by-Step Instructions

### Step 1: Download ngrok (30 seconds)

1. Go to: **https://ngrok.com/download**
2. Click "Download for Windows"
3. Extract the ZIP file
4. Move `ngrok.exe` to your `document-policy-processor` folder

### Step 2: Verify Local Demo is Running (already done!)

Your local demo should already be running on:
```
http://localhost:8503
```

If not, run:
```cmd
cd document-policy-processor\frontend
streamlit run app_local_demo.py
```

### Step 3: Run ngrok (30 seconds)

Open a NEW terminal/command prompt:

```cmd
cd document-policy-processor
ngrok http 8503
```

### Step 4: Get Your Public URL! (10 seconds)

ngrok will display something like:

```
ngrok

Session Status                online
Account                       Free (Sign up for more)
Version                       3.x.x
Region                        United States (us)
Latency                       -
Web Interface                 http://127.0.0.1:4040
Forwarding                    https://abc123.ngrok-free.app -> http://localhost:8503

Connections                   ttl     opn     rt1     rt5     p50     p90
                              0       0       0.00    0.00    0.00    0.00
```

**COPY THIS URL**: `https://abc123.ngrok-free.app`

### Step 5: Test It!

1. Open the ngrok URL in your browser
2. You should see your app!
3. Test uploading a document
4. Verify everything works

### Step 6: Share with Evaluators!

Give them the ngrok URL:
```
https://abc123.ngrok-free.app
```

---

## ✅ What Evaluators Will See

When they visit your ngrok URL, they'll see:

1. **Clean Interface**: Professional Streamlit UI
2. **Upload Section**: Drag & drop or browse for files
3. **Symptoms Input**: Text area for patient symptoms
4. **Process Button**: Click to analyze
5. **Results Display**: Policy recommendations with:
   - Policy names
   - Confidence scores
   - Reasoning
   - Next steps

---

## 🎯 Sample Test Case for Evaluators

Provide this in your submission:

**Test Instructions**:
```
1. Visit: https://YOUR_NGROK_URL.ngrok-free.app
2. Upload: Any medical document (PDF, image, or text)
   - Or use sample text: "Patient diagnosed with diabetes, requires insulin therapy"
3. Enter Symptoms: "Diabetes, high blood sugar, insulin treatment"
4. Click: "Process Document"
5. Wait: 10-20 seconds
6. View: Policy recommendations with confidence scores
```

---

## ⚠️ Important Notes

### Keep These Running:
1. **Terminal 1**: Streamlit app (`streamlit run app_local_demo.py`)
2. **Terminal 2**: ngrok (`ngrok http 8503`)
3. **Your Computer**: Must stay on during evaluation period

### ngrok Free Tier:
- ✅ HTTPS enabled
- ✅ Unlimited bandwidth
- ✅ 40 connections/minute
- ⚠️ URL changes when you restart
- ⚠️ Session timeout after 2 hours

### If URL Changes:
If you need to restart ngrok, the URL will change. Update your submission with the new URL.

### To Get Stable URL:
1. Sign up for free ngrok account: https://dashboard.ngrok.com/signup
2. Get your auth token
3. Run: `ngrok config add-authtoken YOUR_TOKEN`
4. Now you can use: `ngrok http 8503 --domain=YOUR_STATIC_DOMAIN`

---

## 🔧 Troubleshooting

### ngrok Not Found?
Make sure `ngrok.exe` is in your current directory:
```cmd
cd document-policy-processor
dir ngrok.exe
```

### Port Already in Use?
Check if Streamlit is running on 8503:
```cmd
netstat -ano | findstr :8503
```

### Can't Access URL?
1. Check both terminals are running
2. Try opening the URL in incognito mode
3. Check your firewall settings

### Slow Performance?
This is normal for first request (loading models). Subsequent requests are faster.

---

## 📊 Alternative: Streamlit Cloud (5 minutes)

If you want a permanent URL:

### Quick Deploy to Streamlit Cloud:

1. **Push to GitHub**:
```bash
git init
git add .
git commit -m "Hackathon submission"
git push
```

2. **Deploy**:
   - Go to: https://share.streamlit.io/
   - Sign in with GitHub
   - Click "New app"
   - Select repository: `document-policy-processor`
   - Main file: `frontend/app_local_demo.py`
   - Click "Deploy"

3. **Get URL**:
   - Streamlit gives you: `https://YOUR_APP.streamlit.app`
   - This URL is permanent!

**Pros**:
- ✅ Permanent URL
- ✅ Always online
- ✅ Free forever
- ✅ Professional

**Cons**:
- ⏱️ Takes 5-10 minutes to deploy
- 📝 Requires GitHub account

---

## 🎬 Backup Plan: Demo Video

If live URL is problematic, record a video:

1. **Record**: Use OBS Studio or Windows Game Bar
2. **Show**: Complete workflow (upload → process → results)
3. **Upload**: To YouTube (unlisted)
4. **Share**: YouTube link

This proves your app works without needing live access.

---

## 📞 Quick Reference

### Start Everything:

**Terminal 1** (Streamlit):
```cmd
cd document-policy-processor\frontend
streamlit run app_local_demo.py
```

**Terminal 2** (ngrok):
```cmd
cd document-policy-processor
ngrok http 8503
```

### Your URLs:
- **Local**: http://localhost:8503
- **Public**: https://YOUR_NGROK_URL.ngrok-free.app

### Share This:
```
Working Prototype: https://YOUR_NGROK_URL.ngrok-free.app

Test Instructions:
1. Upload a medical document (PDF, image, or text)
2. Enter patient symptoms
3. Click "Process Document"
4. View AI-generated policy recommendations

Sample symptoms: "Diabetes, insulin therapy, blood sugar management"
```

---

## 🎉 You're Ready!

1. ✅ Download ngrok
2. ✅ Run ngrok
3. ✅ Copy public URL
4. ✅ Share with evaluators
5. ✅ Keep computer on during evaluation

**Your public URL is ready in 2 minutes!** 🚀

---

## 📋 Submission Template

Use this in your hackathon submission:

```
Working Prototype Link: https://YOUR_NGROK_URL.ngrok-free.app

Description:
AI-powered insurance policy processor that analyzes medical documents 
and automatically matches them with relevant insurance policies using 
machine learning and natural language processing.

Tech Stack:
- Frontend: Streamlit
- ML: Sentence Transformers, Mistral AI
- Backend: Python
- Cloud: AWS Lambda, S3, DynamoDB (deployed)

Features:
- Document upload (PDF, images, text)
- AI-powered text extraction
- Semantic policy matching
- LLM-based exclusion checking
- Confidence-scored recommendations

Test Instructions:
1. Visit the URL above
2. Upload a medical document or enter text
3. Describe patient symptoms
4. Click "Process Document"
5. View AI-generated recommendations

Note: First request may take 15-20 seconds (loading ML models).
Subsequent requests are faster (5-10 seconds).
```

---

**Get your public URL now and submit to the hackathon!** 🏆

*Last updated: March 8, 2026*
