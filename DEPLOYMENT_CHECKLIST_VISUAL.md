# AWS Deployment Checklist

**Visual step-by-step checklist for deploying Document Policy Processor**

---

## 🎯 Pre-Deployment

- [ ] AWS account created
- [ ] AWS CLI installed
- [ ] AWS CLI configured (`aws configure`)
- [ ] OpenAI API key obtained
- [ ] All smoke tests passed (`quick-smoke-test.bat`)

---

## 📦 Phase 1: Infrastructure Setup

### S3 Buckets
- [ ] Run `infrastructure/deploy-s3.bat`
- [ ] Bucket created successfully
- [ ] CORS configured
- [ ] **Save bucket name**: `_______________________________`

### DynamoDB Tables
- [ ] Run `infrastructure/deploy-dynamodb.bat`
- [ ] Policies table created
- [ ] ProcessingJobs table created
- [ ] Sample data added

### IAM Roles
- [ ] Run `infrastructure/deploy-iam.bat`
- [ ] Lambda execution role created
- [ ] Policies attached
- [ ] **Save role ARN**: `_______________________________`

### Policy Embeddings
- [ ] Run `infrastructure/deploy-embeddings.bat`
- [ ] Embeddings generated
- [ ] Uploaded to S3

---

## ⚡ Phase 2: Lambda Deployment

### Package Function
- [ ] Run `py package-lambda.py`
- [ ] Package created: `lambda-function.zip`
- [ ] Size < 50 MB (or use Docker if larger)

### Deploy Function
- [ ] Run `deploy-lambda.bat`
- [ ] Function name: `DocumentPolicyProcessor`
- [ ] Role ARN entered
- [ ] Environment variables configured:
  - [ ] S3_BUCKET_NAME
  - [ ] DYNAMODB_TABLE_POLICIES
  - [ ] DYNAMODB_TABLE_JOBS
  - [ ] OPENAI_API_KEY
  - [ ] AWS_REGION
- [ ] **Save function ARN**: `_______________________________`

### Test Lambda
- [ ] Run `verify-lambda-deployment.bat`
- [ ] Test passed
- [ ] Response received

---

## 🌐 Phase 3: API Gateway

### Create API
- [ ] Run `deploy-api-gateway.bat`
- [ ] API name: `DocumentPolicyProcessorAPI`
- [ ] Lambda integration configured
- [ ] **Save API URL**: `_______________________________`

### Create API Key
- [ ] API key created
- [ ] **Save API key**: `_______________________________`

### Configure Endpoints
- [ ] POST /api/process-document
- [ ] GET /api/status/{jobId}
- [ ] GET /api/results/{jobId}
- [ ] GET /api/health
- [ ] CORS enabled

### Test API
- [ ] Run `test-api-gateway.bat`
- [ ] Health endpoint works
- [ ] Status endpoint works
- [ ] Authentication works

---

## 📊 Phase 4: CloudWatch Monitoring

### Setup Monitoring
- [ ] Run `setup-cloudwatch-monitoring.bat`
- [ ] Log group created
- [ ] Dashboard created
- [ ] Alarms configured

### Verify Monitoring
- [ ] Run `verify-cloudwatch-monitoring.bat`
- [ ] Logs visible in CloudWatch
- [ ] Metrics being collected
- [ ] Dashboard accessible

---

## 🎨 Phase 5: Frontend Configuration

### Update Configuration
- [ ] Open `frontend/app.py`
- [ ] Update `API_BASE_URL` with your API URL
- [ ] Update `API_KEY` with your API key
- [ ] Save file

### Test Frontend Locally
- [ ] Run `cd frontend`
- [ ] Run `streamlit run app.py`
- [ ] Frontend opens in browser
- [ ] Can upload document
- [ ] Can enter symptoms
- [ ] Can process document
- [ ] Results display correctly

---

## ✅ Phase 6: End-to-End Testing

### Test Complete Flow
- [ ] Upload test document via frontend
- [ ] Enter test symptoms
- [ ] Click "Process Document"
- [ ] Processing completes
- [ ] Recommendations displayed
- [ ] Confidence scores shown
- [ ] Next steps provided

### Test Different Scenarios
- [ ] Test with PDF document
- [ ] Test with image document
- [ ] Test with text document
- [ ] Test with different symptoms
- [ ] Test error handling (invalid file)

### Verify Backend
- [ ] Check CloudWatch logs
- [ ] Verify DynamoDB entries
- [ ] Check S3 uploads
- [ ] Monitor Lambda metrics

---

## 🎥 Phase 7: Demo Video Preparation

### Prepare Demo Environment
- [ ] Frontend running smoothly
- [ ] Sample documents ready
- [ ] Test symptoms prepared
- [ ] Browser zoom set to 125%
- [ ] Notifications disabled

### Record Demo
- [ ] Follow `demo/VIDEO_CREATION_WALKTHROUGH.md`
- [ ] Use `demo/COMPLETE_3MIN_SCRIPT.md`
- [ ] Record introduction (0:00-0:20)
- [ ] Record upload demo (0:20-0:50)
- [ ] Record processing (0:50-1:20)
- [ ] Record results (1:20-2:20)
- [ ] Record AWS services (2:20-2:50)
- [ ] Record conclusion (2:50-3:00)

### Edit and Upload
- [ ] Edit video
- [ ] Add title slide
- [ ] Add closing slide
- [ ] Export as MP4 1080p
- [ ] Upload to YouTube (unlisted)
- [ ] Test video link
- [ ] **Save video URL**: `_______________________________`

---

## 📝 Phase 8: Documentation

### Update README
- [ ] Add API URL
- [ ] Add demo video link
- [ ] Add screenshots
- [ ] Add setup instructions
- [ ] Add usage instructions

### Create Submission Document
- [ ] Create `SUBMISSION.md`
- [ ] Add GitHub repository URL
- [ ] Add working prototype URL
- [ ] Add demo video URL
- [ ] Add project summary
- [ ] Add submission timestamp

---

## 🚀 Phase 9: Final Validation

### Verify All Deliverables
- [ ] GitHub repository is public
- [ ] README is complete
- [ ] Working prototype URL is functional
- [ ] Test prototype in incognito mode
- [ ] Demo video link is accessible
- [ ] Demo video duration ≤ 3 minutes
- [ ] All documentation sections complete

### Test from Fresh Browser
- [ ] Open incognito/private window
- [ ] Navigate to prototype URL
- [ ] Upload document
- [ ] Process successfully
- [ ] View results

### Mobile Testing (Optional)
- [ ] Test on mobile device
- [ ] Frontend is responsive
- [ ] Can upload documents
- [ ] Can view results

---

## 🏆 Phase 10: Submission

### Final Checks
- [ ] All deliverables ready
- [ ] All links working
- [ ] All tests passing
- [ ] Documentation complete
- [ ] Demo video polished

### Submit to Hackathon
- [ ] Review submission requirements
- [ ] Submit GitHub repository URL
- [ ] Submit working prototype URL
- [ ] Submit demo video URL
- [ ] Submit project documentation
- [ ] Verify submission received
- [ ] Keep prototype running until evaluation

---

## 📊 Deployment Summary

**Fill in your deployment details**:

```
AWS Account ID: _______________________________
AWS Region: us-east-1

S3 Bucket: _______________________________
Lambda Function: DocumentPolicyProcessor
Lambda ARN: _______________________________
API Gateway ID: _______________________________
API URL: _______________________________
API Key: _______________________________

Frontend URL (local): http://localhost:8501
Demo Video URL: _______________________________
GitHub Repository: _______________________________

Deployment Date: _______________________________
Submission Date: _______________________________
```

---

## 🆘 Troubleshooting Checklist

If something doesn't work:

- [ ] Check AWS CLI is configured: `aws sts get-caller-identity`
- [ ] Check Lambda logs: `aws logs tail /aws/lambda/DocumentPolicyProcessor --follow`
- [ ] Check API Gateway logs in CloudWatch
- [ ] Verify environment variables in Lambda
- [ ] Test Lambda directly: `aws lambda invoke ...`
- [ ] Check S3 bucket permissions
- [ ] Verify DynamoDB tables exist
- [ ] Check OpenAI API key is valid
- [ ] Verify IAM role has correct permissions

---

## ✅ Success Criteria

Your deployment is successful when:

- ✅ All checkboxes above are checked
- ✅ Frontend can process documents end-to-end
- ✅ API returns valid recommendations
- ✅ CloudWatch shows logs and metrics
- ✅ Demo video is recorded and uploaded
- ✅ All documentation is complete
- ✅ Ready for hackathon submission

---

## 🎉 Congratulations!

You've successfully deployed your Document Policy Processor to AWS!

**Next Steps**:
1. Record your demo video
2. Update all documentation
3. Submit to hackathon
4. Win! 🏆

---

**Estimated Time**:
- Infrastructure: 30 minutes
- Lambda: 20 minutes
- API Gateway: 15 minutes
- CloudWatch: 10 minutes
- Frontend: 15 minutes
- Testing: 30 minutes
- Demo Video: 2-4 hours
- Documentation: 1 hour

**Total**: 5-7 hours for complete deployment and submission

---

**Good luck! 🚀**
