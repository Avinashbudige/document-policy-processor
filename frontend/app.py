"""
Streamlit Frontend for Document Policy Processor

This application provides a user interface for uploading documents and symptom descriptions,
then displays policy recommendations from the backend API.

Requirements: 2.2
"""

import streamlit as st
import requests
import time
import json
from pathlib import Path

# Configuration
try:
    API_BASE_URL = st.secrets["api"]["base_url"]
    API_KEY = st.secrets["api"]["api_key"]
except Exception:
    # Fallback if secrets not configured
    API_BASE_URL = "https://bmi41mg6uf.execute-api.us-east-1.amazonaws.com/prod"
    API_KEY = "9wx9nHe2NV5vSAOyRps9l3c7PpQ19OttaJqHw4mw"

# Page configuration
st.set_page_config(
    page_title="Document Policy Processor",
    page_icon="📄",
    layout="wide"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 1rem;
    }
    .sub-header {
        font-size: 1.2rem;
        color: #666;
        text-align: center;
        margin-bottom: 2rem;
    }
    .recommendation-card {
        padding: 1.5rem;
        border-radius: 0.5rem;
        margin-bottom: 1rem;
        border-left: 4px solid;
    }
    .high-priority {
        border-left-color: #28a745;
        background-color: #d4edda;
    }
    .medium-priority {
        border-left-color: #ffc107;
        background-color: #fff3cd;
    }
    .low-priority {
        border-left-color: #dc3545;
        background-color: #f8d7da;
    }
</style>
""", unsafe_allow_html=True)

# Header
st.markdown('<div class="main-header">📄 Document Policy Processor</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="sub-header">AI-powered insurance policy matching and recommendations</div>',
    unsafe_allow_html=True
)

# Initialize session state
if 'processing' not in st.session_state:
    st.session_state.processing = False
if 'results' not in st.session_state:
    st.session_state.results = None
if 'job_id' not in st.session_state:
    st.session_state.job_id = None


def upload_to_s3(file, presigned_url):
    """Upload file to S3 using presigned URL."""
    try:
        response = requests.put(
            presigned_url,
            data=file.getvalue(),
            headers={'Content-Type': file.type},
            timeout=60
        )
        response.raise_for_status()
        return True
    except requests.exceptions.Timeout:
        st.error("❌ Upload timed out. Please try again with a smaller file.")
        return False
    except requests.exceptions.RequestException as e:
        st.error(f"❌ Failed to upload file: {str(e)}")
        return False
    except Exception as e:
        st.error(f"❌ Unexpected error during upload: {str(e)}")
        return False


def get_upload_url(filename, file_type):
    """Get presigned URL for file upload."""
    try:
        headers = {
            "X-Api-Key": API_KEY,
            "Content-Type": "application/json"
        }
        response = requests.post(
            f"{API_BASE_URL}/api/upload-url",
            json={
                "filename": filename,
                "file_type": file_type
            },
            headers=headers,
            timeout=60  # Increased timeout for Lambda cold start
        )
        response.raise_for_status()
        return response.json()
    except requests.exceptions.Timeout:
        st.error("❌ Request timed out after 60 seconds. The Lambda function may be cold starting. Please try again.")
        return None
    except requests.exceptions.RequestException as e:
        st.error(f"❌ Failed to get upload URL: {str(e)}")
        return None
    except Exception as e:
        st.error(f"❌ Unexpected error: {str(e)}")
        return None


def process_document(job_id, document_url, symptoms):
    """Trigger document processing."""
    try:
        headers = {
            "X-Api-Key": API_KEY,
            "Content-Type": "application/json"
        }
        response = requests.post(
            f"{API_BASE_URL}/api/process-document",
            json={
                "job_id": job_id,
                "document_url": document_url,
                "symptoms": symptoms
            },
            headers=headers,
            timeout=120  # Increased timeout for processing (Lambda can take up to 300s)
        )
        response.raise_for_status()
        return response.json()
    except requests.exceptions.Timeout:
        st.error("❌ Request timed out after 120 seconds. The document may be too large or Lambda is cold starting.")
        return None
    except requests.exceptions.RequestException as e:
        st.error(f"❌ Failed to process document: {str(e)}")
        return None
    except Exception as e:
        st.error(f"❌ Unexpected error: {str(e)}")
        return None


def get_job_status(job_id):
    """Get job processing status."""
    try:
        headers = {
            "X-Api-Key": API_KEY
        }
        response = requests.get(
            f"{API_BASE_URL}/api/status/{job_id}",
            headers=headers,
            timeout=30  # Increased timeout
        )
        response.raise_for_status()
        return response.json()
    except requests.exceptions.Timeout:
        st.warning("⚠️ Status check timed out. Retrying...")
        return None
    except requests.exceptions.RequestException as e:
        st.error(f"Failed to check status: {str(e)}")
        return None
    except Exception as e:
        st.error(f"Unexpected error checking status: {str(e)}")
        return None


def get_job_results(job_id):
    """Get job results."""
    try:
        headers = {
            "X-Api-Key": API_KEY
        }
        response = requests.get(
            f"{API_BASE_URL}/api/results/{job_id}",
            headers=headers,
            timeout=60  # Increased timeout
        )
        response.raise_for_status()
        return response.json()
    except requests.exceptions.Timeout:
        st.error("❌ Request timed out after 60 seconds while fetching results")
        return None
    except requests.exceptions.RequestException as e:
        st.error(f"Failed to get results: {str(e)}")
        return None
    except Exception as e:
        st.error(f"Unexpected error: {str(e)}")
        return None


def display_recommendation(rec, index):
    """Display a single recommendation card."""
    priority_class = {
        1: "high-priority",
        2: "medium-priority",
        3: "low-priority"
    }.get(rec.get('priority', 2), "medium-priority")
    
    action_emoji = {
        "claim": "✅",
        "review": "⚠️",
        "exclude": "❌"
    }.get(rec.get('action', '').lower(), "ℹ️")
    
    confidence = rec.get('confidence', 0)
    confidence_pct = confidence * 100 if confidence <= 1 else confidence
    
    # Determine confidence level
    if confidence_pct >= 80:
        confidence_label = "High Confidence"
        confidence_color = "#28a745"
    elif confidence_pct >= 60:
        confidence_label = "Medium Confidence"
        confidence_color = "#ffc107"
    else:
        confidence_label = "Low Confidence"
        confidence_color = "#dc3545"
    
    st.markdown(f"""
    <div class="recommendation-card {priority_class}">
        <h3>{action_emoji} {rec.get('policy_name', 'Unknown Policy')}</h3>
        <p><strong>Policy ID:</strong> {rec.get('policy_id', 'N/A')}</p>
        <p><strong>Action:</strong> {rec.get('action', 'N/A').upper()}</p>
        <p><strong>Confidence:</strong> 
            <span style="color: {confidence_color}; font-weight: bold;">
                {confidence_pct:.1f}% ({confidence_label})
            </span>
        </p>
        <p><strong>Priority:</strong> {'🔴 High' if rec.get('priority') == 1 else '🟡 Medium' if rec.get('priority') == 2 else '🟢 Low'}</p>
    </div>
    """, unsafe_allow_html=True)
    
    with st.expander("📋 View Details", expanded=False):
        st.write("**Reasoning:**")
        st.write(rec.get('reasoning', 'No reasoning provided'))
        
        st.write("**Next Steps:**")
        next_steps = rec.get('next_steps', [])
        if next_steps:
            for i, step in enumerate(next_steps, 1):
                st.write(f"{i}. {step}")
        else:
            st.write("No specific next steps provided")
        
        # Show additional metadata if available
        if 'metadata' in rec:
            st.write("**Additional Information:**")
            for key, value in rec['metadata'].items():
                st.write(f"- **{key}:** {value}")


# Main form
with st.form("upload_form"):
    st.subheader("📤 Upload Document")
    
    # File upload
    uploaded_file = st.file_uploader(
        "Choose a document (PDF, PNG, JPG, or TXT)",
        type=['pdf', 'png', 'jpg', 'jpeg', 'txt'],
        help="Upload your insurance document or medical records"
    )
    
    # Symptom description
    symptoms = st.text_area(
        "Describe your symptoms or medical condition",
        height=150,
        placeholder="Example: I have been experiencing severe headaches and dizziness for the past two weeks...",
        help="Provide a detailed description of your symptoms or medical condition"
    )
    
    # Submit button
    submit_button = st.form_submit_button("🔍 Process Document", use_container_width=True)

# Handle form submission
if submit_button:
    if not uploaded_file:
        st.error("Please upload a document")
    elif not symptoms or len(symptoms.strip()) < 10:
        st.error("Please provide a detailed symptom description (at least 10 characters)")
    else:
        st.session_state.processing = True
        st.session_state.results = None
        
        # Step 1: Get presigned URL
        with st.spinner("Preparing upload..."):
            upload_data = get_upload_url(uploaded_file.name, uploaded_file.type)
        
        if upload_data:
            # Step 2: Upload file to S3
            with st.spinner("Uploading document..."):
                if upload_to_s3(uploaded_file, upload_data['upload_url']):
                    # Step 3: Trigger processing
                    st.session_state.job_id = upload_data['job_id']
                    
                    result = process_document(
                        upload_data['job_id'],
                        upload_data['document_url'],
                        symptoms
                    )
                    
                    if result:
                        # Step 4: Poll for completion
                        progress_bar = st.progress(0)
                        status_text = st.empty()
                        
                        max_polls = 60  # 5 minutes max (60 * 5 seconds)
                        poll_count = 0
                        
                        while poll_count < max_polls:
                            status_data = get_job_status(upload_data['job_id'])
                            
                            if status_data:
                                status = status_data.get('status', 'processing')
                                progress = min((poll_count + 1) / max_polls, 0.95)
                                progress_bar.progress(progress)
                                
                                if status == 'completed':
                                    progress_bar.progress(1.0)
                                    status_text.success("✅ Processing complete!")
                                    
                                    # Fetch results
                                    results = get_job_results(upload_data['job_id'])
                                    if results:
                                        st.session_state.results = results
                                        st.session_state.processing = False
                                        time.sleep(1)  # Brief pause to show success
                                        st.rerun()
                                    break
                                
                                elif status == 'failed':
                                    progress_bar.empty()
                                    error_msg = status_data.get('error_message', 'Unknown error occurred')
                                    status_text.error(f"❌ Processing failed: {error_msg}")
                                    st.session_state.processing = False
                                    break
                                
                                else:
                                    # Still processing
                                    status_text.info(f"🔄 Processing... ({status})")
                            
                            poll_count += 1
                            time.sleep(5)  # Poll every 5 seconds
                        
                        if poll_count >= max_polls:
                            progress_bar.empty()
                            status_text.error("❌ Processing timeout. Please try again with a smaller document.")
                            st.session_state.processing = False
                    else:
                        st.error("Failed to start processing")
                        st.session_state.processing = False
                else:
                    st.error("Failed to upload document")
                    st.session_state.processing = False
        else:
            st.error("Failed to prepare upload")
            st.session_state.processing = False

# Display results
if st.session_state.results:
    st.divider()
    st.subheader("📊 Results")
    
    results = st.session_state.results
    
    # Check for errors in results
    if results.get('status') == 'failed' or 'error' in results:
        st.error("❌ Processing Failed")
        error_msg = results.get('error_message') or results.get('error', 'Unknown error occurred')
        st.write(f"**Error:** {error_msg}")
        
        # Show suggestions if available
        if 'suggestions' in results:
            st.write("**Suggestions:**")
            for suggestion in results['suggestions']:
                st.write(f"- {suggestion}")
        
        # Allow retry
        if st.button("🔄 Try Again"):
            st.session_state.results = None
            st.session_state.job_id = None
            st.rerun()
    else:
        # Display summary metrics
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Status", results.get('status', 'Unknown').upper())
        
        with col2:
            recommendations = results.get('recommendations', [])
            st.metric("Recommendations", len(recommendations))
        
        with col3:
            processing_time = results.get('processing_time', 0)
            st.metric("Processing Time", f"{processing_time:.2f}s")
        
        # Display document summary if available
        if 'document_summary' in results:
            with st.expander("📄 Document Summary", expanded=False):
                st.write(results['document_summary'])
        
        # Display recommendations
        if recommendations:
            st.subheader("💡 Policy Recommendations")
            st.write(f"Found {len(recommendations)} matching {'policy' if len(recommendations) == 1 else 'policies'}")
            
            # Sort by priority (high to low)
            sorted_recs = sorted(recommendations, key=lambda x: x.get('priority', 2))
            
            for idx, rec in enumerate(sorted_recs, 1):
                display_recommendation(rec, idx)
        else:
            st.info("ℹ️ No policy recommendations found")
            st.write("**This could mean:**")
            st.write("- No policies in the database match your document and symptoms")
            st.write("- The document may not be related to insurance policies")
            st.write("- Try providing more detailed symptom descriptions")
            st.write("- Ensure the document is clear and readable")
        
        # Action buttons
        col1, col2 = st.columns(2)
        
        with col1:
            # Download results button
            if st.button("📥 Download Results as JSON", use_container_width=True):
                json_str = json.dumps(results, indent=2)
                st.download_button(
                    label="Click to Download",
                    data=json_str,
                    file_name=f"results_{st.session_state.job_id}.json",
                    mime="application/json",
                    use_container_width=True
                )
        
        with col2:
            # Process another document
            if st.button("📤 Process Another Document", use_container_width=True):
                st.session_state.results = None
                st.session_state.job_id = None
                st.rerun()

# Sidebar with information
with st.sidebar:
    st.header("ℹ️ About")
    st.write("""
    This AI-powered system helps you understand which insurance policies apply to your situation.
    
    **How it works:**
    1. Upload your insurance document
    2. Describe your symptoms or condition
    3. Our AI analyzes the document and matches it against policies
    4. Get clear recommendations on what actions to take
    
    **Supported formats:**
    - PDF documents
    - Images (PNG, JPG)
    - Text files (TXT)
    """)
    
    st.divider()
    
    st.header("🔧 Technical Details")
    st.write("""
    **AWS Services Used:**
    - AWS Lambda (Processing)
    - API Gateway (REST API)
    - S3 (Document Storage)
    - DynamoDB (Policy Database)
    - Textract (OCR)
    - CloudWatch (Monitoring)
    
    **AI Technologies:**
    - Sentence Transformers (Embeddings)
    - OpenAI GPT-3.5 (Exclusion Checking)
    - Semantic Similarity Matching
    """)
    
    st.divider()
    
    st.header("📞 Support")
    st.write("For questions or issues, please contact the development team.")
    
    # Health check
    if st.button("🏥 Check API Health"):
        try:
            response = requests.get(f"{API_BASE_URL}/api/health")
            if response.status_code == 200:
                st.success("✅ API is healthy")
            else:
                st.error("❌ API is not responding correctly")
        except Exception as e:
            st.error(f"❌ Cannot reach API: {str(e)}")
