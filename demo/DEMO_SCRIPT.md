# Demo Video Script - Document Policy Processor

**Total Duration**: 3:00 minutes (180 seconds)
**Target Audience**: Hackathon judges and evaluators
**Goal**: Demonstrate complete AI-powered document processing workflow

---

## Timeline Breakdown

### 0:00 - 0:20 | Introduction (20 seconds)

**Visual**: Title slide with project name and AWS logo

**Script**:
> "Hi! This is the Document Policy Processor - an AI-powered solution that helps users understand which insurance policies apply to their medical situation. Built entirely on AWS, it combines OCR, semantic matching, and large language models to provide instant, accurate policy recommendations."

**On-Screen Text**:
- "Document Policy Processor"
- "AI-Powered Insurance Policy Analysis"
- "Built with AWS Services"

**Notes**:
- Speak clearly and confidently
- Show enthusiasm but stay professional
- Keep pace moderate - not too fast

---

### 0:20 - 0:50 | Document Upload & Input (30 seconds)

**Visual**: Screen recording of Streamlit frontend

**Script**:
> "Let's see it in action. I'm uploading a medical report from a recent doctor's visit - the system accepts PDFs, images, or text files. I'll also describe my symptoms: 'Diagnosed with Type 2 diabetes, requiring insulin therapy and regular monitoring.' Now I'll click Process Document."

**Actions to Record**:
1. Navigate to the application URL
2. Click "Browse files" button
3. Select sample medical document (PDF)
4. Type symptoms in text area: "Diagnosed with Type 2 diabetes, requiring insulin therapy and regular monitoring"
5. Click "Process Document" button
6. Show processing indicator appearing

**On-Screen Text** (optional):
- "Step 1: Upload Document"
- "Step 2: Describe Symptoms"

**Notes**:
- Use a clean, professional-looking document
- Type symptoms slowly enough to be readable
- Ensure UI is clearly visible (zoom if needed)

---

### 0:50 - 1:20 | Processing Explanation (30 seconds)

**Visual**: Split screen or overlay showing processing stages

**Script**:
> "Behind the scenes, AWS Textract extracts text from the document using OCR. Then, a sentence-transformer model generates semantic embeddings - that's a numerical representation of the meaning. These embeddings are matched against our policy database using cosine similarity. Finally, GPT-3.5 validates each match and checks for exclusions, ensuring accuracy."

**Visual Elements**:
- Show processing spinner/progress bar
- Optional: Show architecture diagram overlay
- Optional: Show brief code snippet or AWS console

**On-Screen Text**:
- "AWS Textract → Text Extraction"
- "Sentence Transformers → Embeddings"
- "Cosine Similarity → Policy Matching"
- "GPT-3.5 → Exclusion Checking"

**Notes**:
- This section can be recorded separately and edited in
- Consider using screen annotations or arrows
- Keep technical terms simple but accurate
- Time this section carefully - 30 seconds goes fast

---

### 1:20 - 2:20 | Results Display (60 seconds)

**Visual**: Screen recording showing results page

**Script**:
> "And here are the results! The system found three relevant policies. The top match is 'Comprehensive Health Plus' with 94% confidence - it covers diabetes management including insulin and monitoring supplies. The AI explains that this policy has no exclusions for Type 2 diabetes and recommends proceeding with a claim.

> The second match is 'Basic Health Insurance' at 78% confidence. While it covers hospitalization, the AI detected that it excludes pre-existing conditions in the first two years - important information that could save time and frustration.

> Each recommendation includes clear next steps, confidence scores, and AI-generated reasoning. This transforms hours of policy document review into seconds of clear, actionable guidance."

**Actions to Record**:
1. Scroll through results slowly
2. Expand first recommendation to show details
3. Highlight confidence score (94%)
4. Show reasoning section
5. Show next steps
6. Briefly show second recommendation
7. Highlight exclusion warning

**On-Screen Text** (optional):
- "94% Confidence"
- "No Exclusions Found"
- "Proceed with Claim"

**Notes**:
- This is the most important section - take time
- Pause briefly on key information
- Use mouse cursor to highlight important text
- Ensure all text is readable (zoom if needed)

---

### 2:20 - 2:50 | AWS Services & Innovation (30 seconds)

**Visual**: Architecture diagram or AWS services icons

**Script**:
> "This solution leverages six AWS services: Lambda for serverless compute, API Gateway for the REST API, S3 for document storage, DynamoDB for the policy database, Textract for OCR, and CloudWatch for monitoring. The entire architecture is serverless, scalable, and cost-effective.

> What makes this innovative? It's not just keyword matching - it's semantic understanding. The AI actually comprehends the meaning of policies and medical conditions, providing human-like analysis at machine speed."

**Visual Elements**:
- Show architecture diagram from docs
- Show AWS service icons
- Optional: Show AWS console briefly

**On-Screen Text**:
- "AWS Lambda"
- "API Gateway"
- "S3"
- "DynamoDB"
- "Textract"
- "CloudWatch"

**Notes**:
- This can be recorded separately and edited in
- Consider using animated diagram
- Emphasize "serverless" and "scalable"

---

### 2:50 - 3:00 | Conclusion & Call to Action (10 seconds)

**Visual**: Closing slide with links

**Script**:
> "The Document Policy Processor makes insurance accessible, accurate, and instant. Check out the full code on GitHub and try the live demo yourself. Thank you!"

**On-Screen Text**:
- "Document Policy Processor"
- "GitHub: [your-repo-url]"
- "Live Demo: [your-prototype-url]"
- "Built for AWS AI for Bharat Hackathon"

**Notes**:
- Smile and be enthusiastic
- Keep it brief - 10 seconds max
- Ensure URLs are clearly visible

---

## Recording Tips

### Before Recording

- [ ] Test the application end-to-end multiple times
- [ ] Prepare sample documents and have them ready
- [ ] Clear browser cache and cookies for clean UI
- [ ] Close unnecessary browser tabs and applications
- [ ] Set browser zoom to 100% or 125% for readability
- [ ] Disable browser extensions that might interfere
- [ ] Prepare your script and practice 2-3 times
- [ ] Set up recording software and test audio

### During Recording

- [ ] Record in a quiet environment
- [ ] Speak clearly and at moderate pace
- [ ] Use a good quality microphone
- [ ] Record in 1080p resolution minimum
- [ ] Keep mouse movements smooth and deliberate
- [ ] Pause briefly between sections for easier editing
- [ ] Record each section 2-3 times for options

### After Recording

- [ ] Review all footage for quality
- [ ] Check audio levels and clarity
- [ ] Verify all text is readable
- [ ] Ensure timing fits within 3 minutes
- [ ] Have backup recordings of each section

---

## Backup Script (If Something Goes Wrong)

If the live demo fails during recording:

**Option 1**: Use pre-recorded results
> "Here's what the system returns after processing..."

**Option 2**: Explain the issue honestly
> "In a live demo, the system would process this in about 30 seconds. Let me show you the typical results..."

**Option 3**: Use screenshots
> "The processing completed successfully, and here are the results..."

---

## Timing Checkpoints

- **0:20**: Should be starting document upload
- **0:50**: Should be explaining processing
- **1:20**: Should be showing results
- **2:20**: Should be discussing AWS services
- **2:50**: Should be on conclusion slide

If you're running over time:
- Cut 5-10 seconds from processing explanation
- Shorten AWS services section
- Show fewer recommendation details

If you're running under time:
- Add more detail to results section
- Show additional recommendations
- Explain more about the AI reasoning

---

## Key Messages to Emphasize

1. **AI-Powered**: Not just keyword matching - semantic understanding
2. **Complete Workflow**: End-to-end solution from upload to recommendations
3. **AWS Services**: Fully serverless, scalable architecture
4. **Practical Value**: Saves time, improves accuracy, reduces claim rejections
5. **Innovation**: Combines OCR, embeddings, and LLM for comprehensive analysis

---

## Common Mistakes to Avoid

- ❌ Speaking too fast (judges need to understand)
- ❌ Using too much technical jargon
- ❌ Showing errors or bugs
- ❌ Going over 3 minutes
- ❌ Poor audio quality
- ❌ Unreadable text on screen
- ❌ Boring monotone delivery
- ❌ Not showing the actual results clearly
- ❌ Forgetting to mention AWS services
- ❌ No clear call to action at the end

---

## Success Criteria

Your demo video is successful if:

✅ Total duration is under 3 minutes
✅ Shows complete workflow from upload to results
✅ Clearly demonstrates AI-powered features
✅ Mentions all AWS services used
✅ Audio is clear and professional
✅ All text on screen is readable
✅ Results are impressive and clearly explained
✅ Includes GitHub and demo links
✅ Leaves judges wanting to try it themselves

