# Document Upload Flow

This document explains the document upload flow implementation for the Document Policy Processor.

## Overview

The upload flow enables frontend applications to upload documents directly to S3 using presigned URLs, then trigger Lambda processing. This approach provides several benefits:

- **Direct Upload**: Files go directly from client to S3, reducing Lambda payload size
- **Scalability**: No file size limits imposed by API Gateway (10MB) or Lambda (6MB)
- **Security**: Presigned URLs are temporary and scoped to specific S3 keys
- **Performance**: Parallel upload and processing possible

## Architecture

```
┌─────────────┐
│  Frontend   │
└──────┬──────┘
       │
       │ 1. POST /api/upload-url
       │    {filename, file_type}
       ▼
┌─────────────────┐
│  API Gateway    │
└──────┬──────────┘
       │
       │ 2. Generate presigned URL
       ▼
┌─────────────────┐
│     Lambda      │
└──────┬──────────┘
       │
       │ 3. Return presigned URL + job_id
       ▼
┌─────────────┐
│  Frontend   │
└──────┬──────┘
       │
       │ 4. PUT file to presigned URL
       ▼
┌─────────────────┐
│       S3        │
└─────────────────┘
       │
       │ 5. POST /api/process-document
       │    {job_id, document_url, symptoms}
       ▼
┌─────────────────┐
│  API Gateway    │
└──────┬──────────┘
       │
       │ 6. Process document
       ▼
┌─────────────────┐
│     Lambda      │
│  (Processing)   │
└─────────────────┘
```

## Implementation Details

### 1. Generate Presigned URL Endpoint

**Endpoint**: `POST /api/upload-url`

**Request**:
```json
{
  "filename": "medical-report.pdf",
  "file_type": "application/pdf"
}
```

**Response**:
```json
{
  "upload_url": "https://s3.amazonaws.com/bucket/documents/uuid/file.pdf?...",
  "document_url": "s3://bucket/documents/uuid/file.pdf",
  "job_id": "550e8400-e29b-41d4-a716-446655440000",
  "expires_in": 3600,
  "upload_method": "PUT"
}
```

**Implementation**:
- Validates filename and file type
- Generates unique job ID (UUID)
- Creates S3 key: `documents/{job_id}/{filename}`
- Generates presigned URL with 1-hour expiration
- Returns both presigned URL and S3 URL for later processing

**Supported File Types**:
- `.pdf` - PDF documents
- `.png` - PNG images
- `.jpg`, `.jpeg` - JPEG images
- `.txt` - Plain text files

### 2. Upload File to S3

The frontend uses the presigned URL to upload the file directly to S3:

```javascript
await fetch(upload_url, {
  method: 'PUT',
  headers: {
    'Content-Type': file.type
  },
  body: file
});
```

**Important**:
- Use `PUT` method (not POST)
- Set `Content-Type` header to match the file type
- Send raw file data in body
- No authentication needed (presigned URL includes credentials)

### 3. Trigger Processing

After successful upload, call the processing endpoint:

**Endpoint**: `POST /api/process-document`

**Request**:
```json
{
  "job_id": "550e8400-e29b-41d4-a716-446655440000",
  "document_url": "s3://bucket/documents/uuid/file.pdf",
  "symptoms": "Fever and cough for 3 days"
}
```

The Lambda function will:
1. Download the document from S3
2. Extract text using AWS Textract
3. Generate embeddings and match policies
4. Check exclusions with LLM
5. Generate recommendations
6. Return results

## Frontend Integration

### Complete Example (JavaScript)

```javascript
async function uploadAndProcessDocument(file, symptoms, apiKey, apiBaseUrl) {
  try {
    // Step 1: Get upload URL
    console.log('Requesting upload URL...');
    const uploadUrlResponse = await fetch(`${apiBaseUrl}/api/upload-url`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'X-Api-Key': apiKey
      },
      body: JSON.stringify({
        filename: file.name,
        file_type: file.type
      })
    });
    
    if (!uploadUrlResponse.ok) {
      throw new Error(`Failed to get upload URL: ${uploadUrlResponse.status}`);
    }
    
    const { upload_url, document_url, job_id } = await uploadUrlResponse.json();
    console.log(`Got upload URL for job ${job_id}`);
    
    // Step 2: Upload file to S3
    console.log('Uploading file to S3...');
    const uploadResponse = await fetch(upload_url, {
      method: 'PUT',
      headers: {
        'Content-Type': file.type
      },
      body: file
    });
    
    if (!uploadResponse.ok) {
      throw new Error(`Failed to upload file: ${uploadResponse.status}`);
    }
    
    console.log('File uploaded successfully');
    
    // Step 3: Trigger processing
    console.log('Triggering document processing...');
    const processResponse = await fetch(`${apiBaseUrl}/api/process-document`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'X-Api-Key': apiKey
      },
      body: JSON.stringify({
        job_id: job_id,
        document_url: document_url,
        symptoms: symptoms
      })
    });
    
    if (!processResponse.ok) {
      throw new Error(`Failed to process document: ${processResponse.status}`);
    }
    
    const result = await processResponse.json();
    console.log('Processing completed:', result);
    
    return result;
    
  } catch (error) {
    console.error('Error in upload and process flow:', error);
    throw error;
  }
}

// Usage
const fileInput = document.getElementById('file-input');
const symptomsInput = document.getElementById('symptoms-input');

fileInput.addEventListener('change', async (event) => {
  const file = event.target.files[0];
  const symptoms = symptomsInput.value;
  
  if (!file || !symptoms) {
    alert('Please select a file and enter symptoms');
    return;
  }
  
  try {
    const result = await uploadAndProcessDocument(
      file,
      symptoms,
      'your-api-key',
      'https://api-id.execute-api.region.amazonaws.com/Prod'
    );
    
    // Display recommendations
    displayRecommendations(result.recommendations);
    
  } catch (error) {
    alert(`Error: ${error.message}`);
  }
});
```

### React Example

```jsx
import React, { useState } from 'react';

function DocumentUploader() {
  const [file, setFile] = useState(null);
  const [symptoms, setSymptoms] = useState('');
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);
  
  const API_KEY = process.env.REACT_APP_API_KEY;
  const API_BASE_URL = process.env.REACT_APP_API_BASE_URL;
  
  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!file || !symptoms) {
      setError('Please select a file and enter symptoms');
      return;
    }
    
    setLoading(true);
    setError(null);
    
    try {
      // Step 1: Get upload URL
      const uploadUrlResponse = await fetch(`${API_BASE_URL}/api/upload-url`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-Api-Key': API_KEY
        },
        body: JSON.stringify({
          filename: file.name,
          file_type: file.type
        })
      });
      
      const { upload_url, document_url, job_id } = await uploadUrlResponse.json();
      
      // Step 2: Upload file
      await fetch(upload_url, {
        method: 'PUT',
        headers: {
          'Content-Type': file.type
        },
        body: file
      });
      
      // Step 3: Process document
      const processResponse = await fetch(`${API_BASE_URL}/api/process-document`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-Api-Key': API_KEY
        },
        body: JSON.stringify({
          job_id: job_id,
          document_url: document_url,
          symptoms: symptoms
        })
      });
      
      const processResult = await processResponse.json();
      setResult(processResult);
      
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };
  
  return (
    <div>
      <form onSubmit={handleSubmit}>
        <div>
          <label>Document:</label>
          <input
            type="file"
            accept=".pdf,.png,.jpg,.jpeg,.txt"
            onChange={(e) => setFile(e.target.files[0])}
          />
        </div>
        
        <div>
          <label>Symptoms:</label>
          <textarea
            value={symptoms}
            onChange={(e) => setSymptoms(e.target.value)}
            placeholder="Describe your symptoms..."
          />
        </div>
        
        <button type="submit" disabled={loading}>
          {loading ? 'Processing...' : 'Upload and Process'}
        </button>
      </form>
      
      {error && <div className="error">{error}</div>}
      
      {result && (
        <div className="results">
          <h3>Recommendations:</h3>
          {result.recommendations.map((rec, index) => (
            <div key={index} className="recommendation">
              <h4>{rec.policy_name}</h4>
              <p><strong>Action:</strong> {rec.action}</p>
              <p><strong>Confidence:</strong> {(rec.confidence * 100).toFixed(1)}%</p>
              <p><strong>Reasoning:</strong> {rec.reasoning}</p>
              <ul>
                {rec.next_steps.map((step, i) => (
                  <li key={i}>{step}</li>
                ))}
              </ul>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

export default DocumentUploader;
```

## Testing

### Using the Test Scripts

**Linux/Mac**:
```bash
# Set environment variables
export API_BASE_URL="https://your-api-id.execute-api.us-east-1.amazonaws.com/Prod"
export API_KEY="your-api-key-here"
export TEST_FILE="test-document.pdf"
export SYMPTOMS="Fever and cough for 3 days"

# Run test
chmod +x test-upload-flow.sh
./test-upload-flow.sh
```

**Windows**:
```cmd
REM Set environment variables
set API_BASE_URL=https://your-api-id.execute-api.us-east-1.amazonaws.com/Prod
set API_KEY=your-api-key-here
set TEST_FILE=test-document.pdf
set SYMPTOMS=Fever and cough for 3 days

REM Run test
test-upload-flow.bat
```

### Manual Testing with curl

```bash
# Step 1: Get upload URL
curl -X POST https://api-id.execute-api.region.amazonaws.com/Prod/api/upload-url \
  -H "X-Api-Key: your-api-key" \
  -H "Content-Type: application/json" \
  -d '{"filename": "test.pdf", "file_type": "application/pdf"}'

# Step 2: Upload file (use URL from step 1)
curl -X PUT "https://s3.amazonaws.com/..." \
  -H "Content-Type: application/pdf" \
  --data-binary @test.pdf

# Step 3: Process document
curl -X POST https://api-id.execute-api.region.amazonaws.com/Prod/api/process-document \
  -H "X-Api-Key: your-api-key" \
  -H "Content-Type: application/json" \
  -d '{
    "job_id": "job-id-from-step-1",
    "document_url": "s3://bucket/documents/uuid/test.pdf",
    "symptoms": "Test symptoms"
  }'
```

## Error Handling

### Common Errors

**400 - Invalid File Type**:
```json
{
  "error": "INVALID_FILE_TYPE",
  "message": "Unsupported file type: .doc. Allowed: .pdf, .png, .jpg, .jpeg, .txt",
  "allowed_extensions": [".pdf", ".png", ".jpg", ".jpeg", ".txt"]
}
```

**403 - Upload Failed**:
- Presigned URL expired (1 hour limit)
- Incorrect Content-Type header
- File size exceeds S3 limits

**404 - Document Not Found**:
```json
{
  "error": "DOCUMENT_NOT_FOUND",
  "message": "Document not found in S3: s3://bucket/key"
}
```

### Best Practices

1. **Validate file type** before requesting upload URL
2. **Check upload response** status code (should be 200)
3. **Handle expired URLs** by requesting a new one
4. **Implement retry logic** for transient failures
5. **Show progress indicators** during upload and processing
6. **Validate file size** on frontend (recommend < 10MB)

## Security Considerations

1. **Presigned URLs expire** after 1 hour
2. **URLs are scoped** to specific S3 keys (no directory traversal)
3. **API key required** for generating URLs
4. **CORS configured** for frontend access
5. **File type validation** prevents malicious uploads
6. **S3 bucket policies** restrict access to Lambda role only

## Performance Optimization

1. **Parallel operations**: Upload and processing can overlap if using async processing
2. **Lambda warm starts**: Reuse Lambda containers for faster response
3. **S3 Transfer Acceleration**: Enable for faster uploads from distant regions
4. **CloudFront**: Add CDN for API Gateway if needed

## Future Enhancements

1. **S3 Event Trigger**: Automatically trigger Lambda on S3 upload (remove step 3)
2. **Multipart Upload**: Support large files (>5GB) with multipart upload
3. **Progress Tracking**: WebSocket or polling for real-time progress
4. **Async Processing**: Return immediately and notify via webhook/SNS
5. **Batch Processing**: Upload multiple documents in one request

## Troubleshooting

### Upload fails with 403

- Check presigned URL hasn't expired
- Verify Content-Type header matches file type
- Ensure file size is within limits

### Processing fails with "Document not found"

- Verify file was uploaded successfully to S3
- Check document_url matches the upload location
- Ensure Lambda has S3 read permissions

### Slow processing

- Check Lambda memory allocation (increase if needed)
- Monitor CloudWatch logs for bottlenecks
- Consider async processing for large documents

## Related Documentation

- [API Gateway Guide](docs/API_GATEWAY_GUIDE.md)
- [Lambda Handler README](src/LAMBDA_HANDLER_README.md)
- [Deployment Guide](DEPLOYMENT_README.md)

## Requirements Validation

This implementation satisfies **Requirement 2.2**:
> THE Document_Policy_Processor SHALL accept user documents as input (PDF, PNG, JPG, TXT formats)

The upload flow enables users to upload documents in all required formats through a secure, scalable presigned URL mechanism.
