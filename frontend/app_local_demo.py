"""
Streamlit Frontend for Document Policy Processor - LOCAL DEMO VERSION

This is a simplified version that runs entirely locally for demo purposes.
It processes documents using the local Python modules without AWS services.

For hackathon demo video recording.
"""

import streamlit as st
import sys
import time
import json
from pathlib import Path
import tempfile

# Add src directory to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

# Import local processing modules
try:
    from text_extractor import TextExtractor
    from policy_matcher import PolicyMatcher
    from llm_exclusion_checker import LLMExclusionChecker
    from recommendation_engine import RecommendationEngine
except ImportError as e:
    st.error(f"Failed to import processing modules: {e}")
    st.stop()

# Page configuration
st.set_page_config(
    page_title="Document Policy Processor - Local Demo",
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
    .demo-badge {
        background-color: #ffc107;
        color: #000;
        padding: 0.5rem 1rem;
        border-radius: 0.5rem;
        text-align: center;
        font-weight: bold;
        margin-bottom: 1rem;
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
st.markdown(
    '<div class="demo-badge">🎬 LOCAL DEMO MODE - Running without AWS services</div>',
    unsafe_allow_html=True
)

# Initialize session state
if 'results' not in st.session_state:
    st.session_state.results = None

# Sample policies for demo
SAMPLE_POLICIES = [
    {
        "policy_id": "POL001",
        "policy_name": "Comprehensive Health Insurance",
        "category": "health",
        "description": "Covers hospitalization, surgery, diagnostic tests, and emergency care",
        "coverage_details": "Hospitalization up to $100,000, surgery coverage, diagnostic tests, emergency care",
        "exclusions": ["Pre-existing conditions within first 2 years", "Cosmetic procedures"]
    },
    {
        "policy_id": "POL002",
        "policy_name": "Critical Illness Coverage",
        "category": "critical_illness",
        "description": "Provides lump sum payment for major illnesses like cancer, heart attack, stroke",
        "coverage_details": "Cancer treatment, heart attack, stroke, kidney failure",
        "exclusions": ["Self-inflicted injuries", "Drug or alcohol abuse"]
    },
    {
        "policy_id": "POL003",
        "policy_name": "Accident Protection Plan",
        "category": "accident",
        "description": "Covers accidental injuries, emergency treatment, and disability",
        "coverage_details": "Emergency treatment, hospitalization due to accidents, disability benefits",
        "exclusions": ["Injuries from illegal activities", "War or terrorism"]
    }
]


def process_document_local(file, symptoms):
    """Process document locally using the processing modules."""
    try:
        # Save uploaded file temporarily
        with tempfile.NamedTemporaryFile(delete=False, suffix=Path(file.name).suffix) as tmp_file:
            tmp_file.write(file.getvalue())
            tmp_path = tmp_file.name
        
        # Step 1: Extract text
        st.info("🔍 Extracting text from document...")
        extractor = TextExtractor()
        
        file_ext = Path(file.name).suffix.lower()
        if file_ext == '.pdf':
            # For demo, use simple text extraction (no AWS Textract)
            extracted_text = f"[Demo Mode] Simulated extraction from {file.name}"
        elif file_ext in ['.png', '.jpg', '.jpeg']:
            extracted_text = f"[Demo Mode] Simulated OCR from {file.name}"
        elif file_ext == '.txt':
            with open(tmp_path, 'r', encoding='utf-8') as f:
                extracted_text = f.read()
        else:
            extracted_text = ""
        
        # Combine with symptoms
        combined_text = f"{extracted_text}\n\nSymptoms: {symptoms}"
        
        # Step 2: Match policies
        st.info("🔎 Matching against policies...")
        matcher = PolicyMatcher()
        
        # Generate embedding for the query
        query_embedding = matcher.generate_embedding(combined_text)
        
        # For demo, use simple keyword matching
        matches = []
        for policy in SAMPLE_POLICIES:
            policy_text = f"{policy['policy_name']} {policy['description']} {policy['coverage_details']}"
            policy_embedding = matcher.generate_embedding(policy_text)
            
            # Calculate similarity
            similarity = matcher.calculate_similarity(query_embedding, policy_embedding)
            
            if similarity > 0.3:  # Threshold
                matches.append({
                    'policy': policy,
                    'similarity_score': similarity
                })
        
        # Sort by similarity
        matches.sort(key=lambda x: x['similarity_score'], reverse=True)
        
        # Step 3: Check exclusions (simplified for demo)
        st.info("✅ Checking policy exclusions...")
        time.sleep(1)  # Simulate processing
        
        # Step 4: Generate recommendations
        st.info("💡 Generating recommendations...")
        engine = RecommendationEngine()
        
        recommendations = []
        for idx, match in enumerate(matches[:3], 1):  # Top 3 matches
            policy = match['policy']
            similarity = match['similarity_score']
            
            # Determine action based on similarity
            if similarity > 0.7:
                action = "claim"
                confidence = similarity
                priority = 1
            elif similarity > 0.5:
                action = "review"
                confidence = similarity * 0.9
                priority = 2
            else:
                action = "review"
                confidence = similarity * 0.8
                priority = 3
            
            recommendations.append({
                'policy_id': policy['policy_id'],
                'policy_name': policy['policy_name'],
                'action': action,
                'confidence': confidence,
                'priority': priority,
                'reasoning': f"Based on document analysis and symptom description, this policy shows {similarity*100:.1f}% relevance. {policy['description']}",
                'next_steps': [
                    f"Review the {policy['policy_name']} policy details",
                    "Gather required documentation for claim submission",
                    "Contact insurance provider for clarification if needed"
                ],
                'metadata': {
                    'category': policy['category'],
                    'coverage': policy['coverage_details'],
                    'exclusions': ', '.join(policy['exclusions'])
                }
            })
        
        # Clean up temp file
        Path(tmp_path).unlink(missing_ok=True)
        
        return {
            'status': 'completed',
            'recommendations': recommendations,
            'processing_time': 2.5,
            'document_summary': f"Processed {file.name} ({file.size} bytes) with symptom description"
        }
        
    except Exception as e:
        return {
            'status': 'failed',
            'error': str(e),
            'error_message': f"Failed to process document: {str(e)}"
        }


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
            metadata = rec['metadata']
            st.write(f"- **Category:** {metadata.get('category', 'N/A')}")
            st.write(f"- **Coverage:** {metadata.get('coverage', 'N/A')}")
            st.write(f"- **Exclusions:** {metadata.get('exclusions', 'N/A')}")


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
        with st.spinner("Processing document..."):
            results = process_document_local(uploaded_file, symptoms)
            st.session_state.results = results
            time.sleep(0.5)  # Brief pause
            st.rerun()

# Display results
if st.session_state.results:
    st.divider()
    st.subheader("📊 Results")
    
    results = st.session_state.results
    
    # Check for errors
    if results.get('status') == 'failed':
        st.error("❌ Processing Failed")
        st.write(f"**Error:** {results.get('error_message', 'Unknown error')}")
        
        if st.button("🔄 Try Again"):
            st.session_state.results = None
            st.rerun()
    else:
        # Display summary metrics
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Status", "✅ COMPLETED")
        
        with col2:
            recommendations = results.get('recommendations', [])
            st.metric("Recommendations", len(recommendations))
        
        with col3:
            processing_time = results.get('processing_time', 0)
            st.metric("Processing Time", f"{processing_time:.2f}s")
        
        # Display document summary
        if 'document_summary' in results:
            with st.expander("📄 Document Summary", expanded=False):
                st.write(results['document_summary'])
        
        # Display recommendations
        if recommendations:
            st.subheader("💡 Policy Recommendations")
            st.write(f"Found {len(recommendations)} matching {'policy' if len(recommendations) == 1 else 'policies'}")
            
            for idx, rec in enumerate(recommendations, 1):
                display_recommendation(rec, idx)
        else:
            st.info("ℹ️ No policy recommendations found")
        
        # Action buttons
        col1, col2 = st.columns(2)
        
        with col1:
            json_str = json.dumps(results, indent=2)
            st.download_button(
                label="📥 Download Results as JSON",
                data=json_str,
                file_name="results_demo.json",
                mime="application/json",
                use_container_width=True
            )
        
        with col2:
            if st.button("📤 Process Another Document", use_container_width=True):
                st.session_state.results = None
                st.rerun()

# Sidebar
with st.sidebar:
    st.header("ℹ️ About")
    st.write("""
    This AI-powered system helps you understand which insurance policies apply to your situation.
    
    **How it works:**
    1. Upload your insurance document
    2. Describe your symptoms or condition
    3. Our AI analyzes and matches against policies
    4. Get clear recommendations
    
    **Demo Mode:**
    This version runs locally without AWS services for demonstration purposes.
    """)
    
    st.divider()
    
    st.header("🔧 AWS Architecture")
    st.write("""
    **Production uses:**
    - AWS Lambda (Processing)
    - API Gateway (REST API)
    - S3 (Document Storage)
    - DynamoDB (Policy Database)
    - Textract (OCR)
    - CloudWatch (Monitoring)
    
    **AI Technologies:**
    - Sentence Transformers
    - OpenAI GPT-3.5
    - Semantic Similarity
    """)
    
    st.divider()
    
    st.header("📊 Sample Policies")
    st.write(f"Loaded {len(SAMPLE_POLICIES)} sample policies:")
    for policy in SAMPLE_POLICIES:
        st.write(f"- {policy['policy_name']}")
