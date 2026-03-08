# Quick Start Guide

Get the Document Policy Processor frontend up and running in 5 minutes!

## Prerequisites

- Python 3.9+ installed
- Backend API deployed and accessible (API Gateway URL)

## Quick Setup

### Linux/Mac

```bash
# 1. Navigate to frontend directory
cd frontend

# 2. Run deployment script with your API Gateway URL
chmod +x deploy.sh
./deploy.sh https://your-api-gateway-url.amazonaws.com/prod

# 3. Start the application
streamlit run app.py
```

### Windows

```cmd
# 1. Navigate to frontend directory
cd frontend

# 2. Run deployment script with your API Gateway URL
deploy.bat https://your-api-gateway-url.amazonaws.com/prod

# 3. Start the application
streamlit run app.py
```

## Manual Setup

If you prefer to set up manually:

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Create secrets file
mkdir -p .streamlit
cat > .streamlit/secrets.toml <<EOF
API_BASE_URL = "https://your-api-gateway-url.amazonaws.com/prod"
EOF

# 3. Run the app
streamlit run app.py
```

## Testing the Application

1. Open your browser to `http://localhost:8501`
2. Click "Browse files" and upload a sample document
3. Enter a symptom description (e.g., "I have been experiencing severe headaches")
4. Click "Process Document"
5. View the recommendations!

## Sample Test Data

For testing, you can use:

**Sample Symptoms:**
```
I have been experiencing severe headaches and dizziness for the past two weeks. 
The headaches occur daily and last for several hours. I also have occasional 
nausea and sensitivity to light.
```

**Sample Documents:**
- Any PDF document with text
- Any image with readable text
- Any .txt file with content

## Troubleshooting

### "Cannot connect to API"

Check that:
1. Your API Gateway URL is correct in `.streamlit/secrets.toml`
2. The backend API is deployed and running
3. CORS is enabled on the API Gateway

### "Module not found"

Run: `pip install -r requirements.txt`

### "Port already in use"

Run: `streamlit run app.py --server.port 8502`

## Next Steps

- Deploy to Streamlit Cloud for public access
- Customize the UI in `app.py`
- Add more features as needed

## Getting Your API Gateway URL

If you don't have your API Gateway URL yet:

1. Go to AWS Console → API Gateway
2. Select your API
3. Click "Stages" → "prod"
4. Copy the "Invoke URL"

The URL should look like:
```
https://abc123xyz.execute-api.us-east-1.amazonaws.com/prod
```

## Support

For issues or questions, check:
- `README.md` for detailed documentation
- Backend logs in CloudWatch
- API Gateway logs for connection issues
