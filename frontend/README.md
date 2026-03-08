# Document Policy Processor - Frontend

This is the Streamlit-based frontend application for the Document Policy Processor. It provides a user-friendly interface for uploading documents and viewing policy recommendations.

## Features

- **Document Upload**: Upload PDF, PNG, JPG, or TXT files
- **Symptom Input**: Describe your medical condition or symptoms
- **Real-time Processing**: Watch as your document is processed through the AI pipeline
- **Clear Recommendations**: View policy matches with confidence scores and actionable next steps
- **Detailed Results**: Expand recommendations to see reasoning and detailed guidance

## Prerequisites

- Python 3.9 or higher
- Access to the deployed backend API (API Gateway URL)

## Installation

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Configure API endpoint:
```bash
# Create secrets file
mkdir -p .streamlit
cp .streamlit/secrets.toml.example .streamlit/secrets.toml

# Edit secrets.toml and update API_BASE_URL with your API Gateway URL
```

## Running Locally

```bash
streamlit run app.py
```

The application will open in your browser at `http://localhost:8501`

## Deployment Options

### Option 1: Streamlit Cloud (Recommended)

1. Push your code to GitHub
2. Go to [share.streamlit.io](https://share.streamlit.io)
3. Connect your GitHub repository
4. Add your API_BASE_URL in the Secrets section
5. Deploy!

### Option 2: AWS EC2

1. Launch an EC2 instance (t2.micro is sufficient)
2. Install Python and dependencies
3. Configure secrets.toml with your API Gateway URL
4. Run with: `streamlit run app.py --server.port 80 --server.address 0.0.0.0`
5. Configure security group to allow HTTP traffic

### Option 3: Docker

```bash
# Build image
docker build -t document-policy-processor-frontend .

# Run container
docker run -p 8501:8501 \
  -e API_BASE_URL="https://your-api-gateway-url.amazonaws.com" \
  document-policy-processor-frontend
```

## Configuration

### Environment Variables

- `API_BASE_URL`: The base URL of your API Gateway endpoint (required)

### Streamlit Secrets

Create `.streamlit/secrets.toml`:

```toml
API_BASE_URL = "https://your-api-gateway-id.execute-api.us-east-1.amazonaws.com/prod"
```

## Usage

1. **Upload Document**: Click "Browse files" and select your insurance document
2. **Describe Symptoms**: Enter a detailed description of your medical condition
3. **Process**: Click "Process Document" to start the AI analysis
4. **View Results**: Review the policy recommendations and confidence scores
5. **Download**: Optionally download results as JSON for your records

## API Integration

The frontend communicates with the backend through these endpoints:

- `POST /api/upload-url`: Get presigned URL for document upload
- `POST /api/process-document`: Trigger document processing
- `GET /api/status/{jobId}`: Check processing status
- `GET /api/results/{jobId}`: Retrieve processing results
- `GET /api/health`: Health check

## Troubleshooting

### Cannot connect to API

- Verify API_BASE_URL is correct in secrets.toml
- Check that API Gateway is deployed and accessible
- Ensure CORS is enabled on the API Gateway

### File upload fails

- Check file size (must be under 10MB)
- Verify file format is supported (PDF, PNG, JPG, TXT)
- Ensure S3 bucket has correct permissions

### Processing takes too long

- Large documents may take 30-60 seconds to process
- Check CloudWatch logs for Lambda function errors
- Verify Lambda timeout is set to at least 300 seconds

## Development

### Project Structure

```
frontend/
├── app.py                    # Main Streamlit application
├── requirements.txt          # Python dependencies
├── .streamlit/
│   └── secrets.toml.example # Configuration template
└── README.md                # This file
```

### Adding Features

To add new features:

1. Edit `app.py`
2. Test locally with `streamlit run app.py`
3. Commit and push changes
4. Redeploy to your hosting platform

## Requirements Validation

This frontend implementation satisfies:

- **Requirement 2.2**: Document upload form with file picker ✅
- **Requirement 2.2**: Text input for symptom description ✅
- **Requirement 2.2**: Submit button to trigger processing ✅
- **Requirement 2.2**: File upload to S3 using presigned URL ✅
- **Requirement 2.8**: Display results in structured format ✅

## License

See LICENSE file in the root directory.
