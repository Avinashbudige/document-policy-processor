# Frontend Deployment Checklist

Use this checklist to ensure your frontend deployment is complete and working correctly.

## Pre-Deployment

### Backend Verification
- [x] Backend API is deployed and accessible
- [x] API Gateway URL is available
- [x] Lambda function is working correctly
- [x] S3 bucket for uploads is configured
- [x] DynamoDB tables are created and populated
- [x] Test backend with curl or Postman
- [x] CloudWatch monitoring configured (Task 11.3)

### Configuration
- [ ] API Gateway URL is documented
- [ ] CORS is configured on API Gateway (initially allow `*` for testing)
- [ ] Environment variables are prepared
- [ ] Secrets are ready (API keys, URLs)

### Code Preparation
- [ ] Frontend code is committed to Git
- [ ] All dependencies are in requirements.txt
- [ ] Configuration files are ready (.streamlit/secrets.toml.example)
- [ ] README.md is updated

---

## Deployment (Choose One)

### Option A: Streamlit Cloud
- [ ] GitHub repository is public or accessible
- [ ] Pushed latest code to GitHub
- [ ] Created Streamlit Cloud account
- [ ] Connected GitHub to Streamlit Cloud
- [ ] Created new app on Streamlit Cloud
- [ ] Set main file path: `frontend/app.py`
- [ ] Added API_BASE_URL to secrets
- [ ] Clicked "Deploy"
- [ ] Deployment completed successfully
- [ ] Noted Streamlit Cloud URL

### Option B: AWS EC2
- [ ] Launched EC2 instance (t2.micro or larger)
- [ ] Configured security group (ports 22, 80, 443, 8501)
- [ ] SSH access is working
- [ ] Ran deploy-ec2.sh script
- [ ] Streamlit service is running
- [ ] Can access via http://EC2_IP:8501
- [ ] (Optional) Set up Nginx reverse proxy
- [ ] (Optional) Configured SSL with Let's Encrypt
- [ ] (Optional) Set up custom domain

### Option C: S3 + CloudFront
- [ ] AWS CLI is configured
- [ ] Updated index.html with API URL
- [ ] Ran deploy-s3-cloudfront.sh script
- [ ] S3 bucket created and configured
- [ ] Files uploaded to S3
- [ ] S3 website URL is accessible
- [ ] (Optional) CloudFront distribution created
- [ ] (Optional) CloudFront deployment completed
- [ ] (Optional) Custom domain configured

### Option D: Docker
- [ ] Docker is installed
- [ ] Created Dockerfile
- [ ] Built Docker image successfully
- [ ] Tested container locally
- [ ] (Optional) Pushed to ECR
- [ ] (Optional) Deployed to ECS/EKS

---

## Post-Deployment Configuration

### CORS Update
- [ ] Added frontend URL to API Gateway CORS allowed origins
- [ ] Tested CORS with browser developer tools
- [ ] No CORS errors in console

### DNS (if using custom domain)
- [ ] Domain is registered
- [ ] DNS A record or CNAME created
- [ ] DNS propagation completed (check with `nslookup`)
- [ ] Domain resolves to correct IP/URL

### SSL/HTTPS (if applicable)
- [ ] SSL certificate obtained
- [ ] Certificate is valid and trusted
- [ ] HTTPS is working
- [ ] HTTP redirects to HTTPS
- [ ] No mixed content warnings

---

## Testing

### Automated Tests
- [ ] Ran test-deployment.sh script
- [ ] All automated tests passed
- [ ] No errors in test output

### Manual Functional Tests
- [ ] Frontend loads without errors
- [ ] Page displays correctly
- [ ] All UI elements are visible
- [ ] Can click all buttons
- [ ] Forms are functional

### Document Upload Test
- [ ] Can select a file
- [ ] Can upload PDF file
- [ ] Can upload PNG/JPG file
- [ ] Can upload TXT file
- [ ] File size validation works (reject > 10MB)
- [ ] File type validation works (reject unsupported types)

### Processing Test
- [ ] Can enter symptom description
- [ ] Can submit form
- [ ] Processing starts successfully
- [ ] Progress indicator shows
- [ ] Processing completes within reasonable time (< 2 minutes)
- [ ] No timeout errors

### Results Display Test
- [ ] Results are displayed correctly
- [ ] Recommendations are shown
- [ ] Confidence scores are visible
- [ ] Reasoning is displayed
- [ ] Next steps are shown
- [ ] Can expand/collapse details
- [ ] Can download results (if applicable)

### Error Handling Test
- [ ] Empty file upload shows error
- [ ] Empty symptoms shows error
- [ ] Invalid file type shows error
- [ ] Large file shows error
- [ ] Network errors are handled gracefully
- [ ] API errors are displayed clearly

### Browser Compatibility
- [ ] Works in Chrome
- [ ] Works in Firefox
- [ ] Works in Safari
- [ ] Works in Edge
- [ ] No console errors in any browser

### Mobile Responsiveness
- [ ] Tested on mobile device or emulator
- [ ] Layout adapts to small screens
- [ ] All buttons are tappable
- [ ] Text is readable
- [ ] Forms are usable
- [ ] No horizontal scrolling

### Performance
- [ ] Page loads in < 3 seconds
- [ ] Processing completes in < 2 minutes
- [ ] No memory leaks (check with long session)
- [ ] No performance degradation over time

### Security
- [ ] HTTPS is enabled (production)
- [ ] No sensitive data in URLs
- [ ] No API keys exposed in frontend code
- [ ] CORS is properly configured (not `*` in production)
- [ ] No XSS vulnerabilities
- [ ] No SQL injection vulnerabilities (if applicable)

---

## Documentation

### Code Documentation
- [ ] README.md is updated with deployment URL
- [ ] API documentation is complete
- [ ] Configuration instructions are clear
- [ ] Troubleshooting guide is available

### Deployment Documentation
- [ ] Deployment method is documented
- [ ] Configuration steps are documented
- [ ] Environment variables are documented
- [ ] Secrets management is documented

### User Documentation
- [ ] Usage instructions are clear
- [ ] Screenshots are included
- [ ] Demo video link is added (if available)
- [ ] FAQ is available

---

## Monitoring & Maintenance

### Logging
- [ ] Application logs are accessible
- [ ] Error logs are being captured
- [ ] Log retention is configured
- [ ] Can view logs easily

### Monitoring
- [x] CloudWatch dashboard created
- [x] CloudWatch alarms configured
- [x] Log groups set up with retention
- [x] Custom metrics configured
- [ ] Uptime monitoring is set up (optional)
- [ ] Error rate monitoring is set up (optional)
- [ ] Performance monitoring is set up (optional)
- [ ] Alerts are configured (optional)

### Backup
- [ ] Configuration is backed up
- [ ] Deployment scripts are in version control
- [ ] Secrets are securely stored
- [ ] Recovery procedure is documented

---

## Submission Preparation

### URLs
- [ ] Frontend URL is documented
- [ ] Frontend URL is publicly accessible
- [ ] Frontend URL is added to SUBMISSION.md
- [ ] Frontend URL is added to README.md

### Demo Preparation
- [ ] Frontend is stable for demo
- [ ] Test data is prepared
- [ ] Demo script is ready
- [ ] Backup plan if deployment fails

### Final Verification
- [ ] Tested complete workflow end-to-end
- [ ] Verified with fresh browser (no cache)
- [ ] Tested from different network
- [ ] Tested on different device
- [ ] No critical bugs remaining

---

## Hackathon Specific

### Submission Requirements
- [ ] Working prototype URL is available
- [ ] URL is publicly accessible (no authentication required)
- [ ] URL will remain active until after evaluation
- [ ] URL is included in submission form

### Demo Video
- [ ] Recorded demo using deployed frontend
- [ ] Demo shows complete workflow
- [ ] Demo is under 3 minutes
- [ ] Demo video is uploaded and accessible

### Presentation
- [ ] Can demonstrate live during presentation
- [ ] Have backup screenshots/video if live demo fails
- [ ] Know how to explain the deployment architecture
- [ ] Can answer questions about scalability

---

## Sign-Off

### Deployment Team
- [ ] Developer sign-off: _________________ Date: _______
- [ ] Tester sign-off: _________________ Date: _______
- [ ] Reviewer sign-off: _________________ Date: _______

### Deployment Information
- **Deployment Date:** _______________________
- **Deployment Method:** _______________________
- **Frontend URL:** _______________________
- **Backend API URL:** _______________________
- **Deployed By:** _______________________

### Notes
```
Add any additional notes, issues, or observations here:




```

---

## Quick Reference

### Important URLs
- Frontend: _______________________
- Backend API: _______________________
- GitHub Repo: _______________________
- Demo Video: _______________________

### Important Commands
```bash
# Check service status (EC2)
sudo systemctl status streamlit
sudo systemctl status nginx

# View logs (EC2)
sudo journalctl -u streamlit -f
sudo tail -f /var/log/nginx/error.log

# Restart services (EC2)
sudo systemctl restart streamlit
sudo systemctl restart nginx

# Invalidate CloudFront cache (S3+CloudFront)
aws cloudfront create-invalidation --distribution-id YOUR_ID --paths "/*"

# Update S3 files (S3+CloudFront)
aws s3 cp index.html s3://YOUR_BUCKET/ --content-type "text/html"
```

### Emergency Contacts
- AWS Support: _______________________
- Team Lead: _______________________
- Backup Contact: _______________________

---

## Status

**Overall Deployment Status:** [ ] Not Started [ ] In Progress [ ] Complete [ ] Failed

**Ready for Submission:** [ ] Yes [ ] No

**Issues/Blockers:**
```
List any outstanding issues or blockers:




```

---

**Last Updated:** _______________________
**Updated By:** _______________________
