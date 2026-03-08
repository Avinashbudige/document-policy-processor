# Frontend Deployment - Quick Start Guide

Choose your deployment method and follow the steps below.

## 🚀 Fastest Option: Streamlit Cloud (5 minutes)

**Perfect for hackathons and demos!**

### Prerequisites
- GitHub account
- Your API Gateway URL

### Steps

1. **Run the setup script:**
   ```bash
   cd frontend
   chmod +x deploy-streamlit-cloud.sh
   ./deploy-streamlit-cloud.sh
   ```

2. **Push to GitHub:**
   ```bash
   git remote add origin https://github.com/YOUR_USERNAME/document-policy-processor.git
   git push -u origin main
   ```

3. **Deploy on Streamlit Cloud:**
   - Go to [share.streamlit.io](https://share.streamlit.io)
   - Click "New app"
   - Select your repository
   - Main file: `frontend/app.py`
   - Add secret: `API_BASE_URL = "your-api-url"`
   - Click "Deploy"

4. **Done!** Your app will be live in 2-3 minutes.

---

## 🖥️ Production Option: AWS EC2 (15 minutes)

**Best for production deployments with custom domains**

### Prerequisites
- AWS account
- EC2 instance running Amazon Linux 2023
- SSH access to your instance

### Steps

1. **SSH into your EC2 instance:**
   ```bash
   ssh -i your-key.pem ec2-user@your-ec2-ip
   ```

2. **Download and run deployment script:**
   ```bash
   curl -O https://raw.githubusercontent.com/YOUR_USERNAME/document-policy-processor/main/frontend/deploy-ec2.sh
   chmod +x deploy-ec2.sh
   ./deploy-ec2.sh
   ```

3. **Follow the prompts:**
   - Enter your GitHub repository URL
   - Enter your API Gateway URL

4. **Access your app:**
   ```
   http://YOUR_EC2_IP:8501
   ```

5. **Optional - Set up Nginx for production:**
   ```bash
   ./setup-nginx.sh
   ```

---

## 🌐 Static Option: S3 + CloudFront (10 minutes)

**Best for simple static deployments**

### Prerequisites
- AWS CLI configured
- Your API Gateway URL

### Steps

1. **Run deployment script:**
   ```bash
   cd frontend
   chmod +x deploy-s3-cloudfront.sh
   ./deploy-s3-cloudfront.sh
   ```

2. **Follow the prompts:**
   - Enter unique bucket name
   - Enter API Gateway URL
   - Choose whether to create CloudFront distribution

3. **Update API Gateway CORS:**
   - Add your S3/CloudFront URL to allowed origins

4. **Access your app:**
   - S3: `http://your-bucket.s3-website-us-east-1.amazonaws.com`
   - CloudFront: `https://d1234567890abc.cloudfront.net`

---

## 🧪 Testing Your Deployment

After deploying, test your application:

```bash
chmod +x test-deployment.sh
./test-deployment.sh
```

Enter your frontend URL when prompted.

### Manual Testing Checklist

- [ ] Frontend loads without errors
- [ ] Can upload a document
- [ ] Can enter symptoms
- [ ] Processing completes successfully
- [ ] Results are displayed
- [ ] No CORS errors in browser console
- [ ] Works on mobile devices

---

## 🔧 Troubleshooting

### "Cannot connect to API"

1. Verify API Gateway URL is correct
2. Check API Gateway CORS settings
3. Ensure API is deployed to correct stage

### "File upload fails"

1. Check S3 bucket permissions
2. Verify presigned URL generation
3. Check file size (must be < 10MB)

### "Processing timeout"

1. Check Lambda function logs
2. Verify Lambda timeout (should be 300s)
3. Check DynamoDB for job status

### More help

See the full [FRONTEND_DEPLOYMENT_GUIDE.md](../FRONTEND_DEPLOYMENT_GUIDE.md) for detailed troubleshooting.

---

## 📋 Deployment Comparison

| Method | Time | Cost | Difficulty | Best For |
|--------|------|------|------------|----------|
| **Streamlit Cloud** | 5 min | Free | ⭐ Easy | Demos, hackathons |
| **AWS EC2** | 15 min | ~$5/mo | ⭐⭐ Medium | Production, custom domains |
| **S3 + CloudFront** | 10 min | ~$1/mo | ⭐⭐ Medium | Static sites, high scale |
| **Docker** | 20 min | Varies | ⭐⭐⭐ Hard | Container orchestration |

---

## 🎯 Recommended for Hackathon

**Use Streamlit Cloud!**

It's:
- ✅ Free
- ✅ Fast (5 minutes)
- ✅ Automatic HTTPS
- ✅ Easy to update
- ✅ No server management

Perfect for getting your demo up quickly!

---

## 📞 Need Help?

1. Check the [FRONTEND_DEPLOYMENT_GUIDE.md](../FRONTEND_DEPLOYMENT_GUIDE.md)
2. Review CloudWatch logs for backend errors
3. Check browser console for frontend errors
4. Verify API Gateway CORS configuration

---

## ✅ After Deployment

1. **Update documentation:**
   - Add frontend URL to README.md
   - Update SUBMISSION.md

2. **Test thoroughly:**
   - Run automated tests
   - Manual end-to-end test
   - Test on different devices

3. **Prepare demo video:**
   - Use deployed frontend
   - Show complete workflow
   - Keep under 3 minutes

Good luck with your hackathon! 🚀
