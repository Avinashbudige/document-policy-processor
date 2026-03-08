# Optimized Test Cases for Policy Matching

These test cases are specifically designed to match the policies in the database and generate recommendations.

---

## Test Case 1: Diabetes Care Plan (POL-003)

### Document
**File**: `optimized_diabetes_bill.txt`

### Symptoms (Copy & Paste)
```
Type 2 diabetes mellitus requiring insulin therapy, continuous glucose monitoring, blood glucose test strips, diabetic supplies, endocrinologist visits, diabetes management, specialist care for diabetes complications, diabetic neuropathy, need coverage for insulin and monitoring supplies
```

### Expected Results
- **Primary Match**: Diabetes Care Plan (POL-003)
- **Confidence**: 60-80%
- **Action**: CLAIM
- **Reasoning**: Document explicitly mentions diabetes management, insulin, monitoring supplies, and specialist visits - all covered under Diabetes Care Plan

### Key Matching Terms
- Diabetes management
- Insulin therapy
- Glucose monitoring
- Diabetic supplies
- Specialist visits
- Endocrinologist

---

## Test Case 2: Basic Health Insurance - Emergency (POL-001)

### Document
**File**: `optimized_emergency_bill.txt`

### Symptoms (Copy & Paste)
```
Severe chest pain, difficulty breathing, heart attack, acute myocardial infarction, emergency room visit, required immediate hospitalization, emergency cardiac surgery, coronary angioplasty, stent placement, ICU admission, life-threatening emergency requiring urgent medical care
```

### Expected Results
- **Primary Match**: Basic Health Insurance (POL-001)
- **Secondary Match**: Comprehensive Health Plus (POL-002)
- **Confidence**: 70-85%
- **Action**: CLAIM
- **Reasoning**: Emergency care, hospitalization, and surgery are all covered under basic health insurance

### Key Matching Terms
- Emergency care
- Hospitalization
- Surgery
- Heart attack
- ICU admission
- Life-threatening emergency

---

## Test Case 3: Basic Health Insurance - Surgery (POL-001)

### Document
**File**: `optimized_surgery_bill.txt`

### Symptoms (Copy & Paste)
```
Acute appendicitis, severe abdominal pain, required emergency surgery, laparoscopic appendectomy, hospitalization for 3 days, surgical procedure, post-operative care, medically necessary surgery to prevent rupture and complications
```

### Expected Results
- **Primary Match**: Basic Health Insurance (POL-001)
- **Secondary Match**: Comprehensive Health Plus (POL-002)
- **Confidence**: 75-90%
- **Action**: CLAIM
- **Reasoning**: Emergency surgery and hospitalization are core benefits covered under basic health insurance

### Key Matching Terms
- Emergency surgery
- Hospitalization
- Surgical procedure
- Appendectomy
- Post-operative care
- Medically necessary

---

## Test Case 4: Comprehensive Health Plus (POL-002)

### Document
**File**: `optimized_comprehensive_bill.txt`

### Symptoms (Copy & Paste)
```
Multiple health conditions requiring comprehensive care including hospitalization for gallbladder surgery, outpatient follow-up visits, dental treatment including root canal, vision care with prescription eyeglasses, emergency room visit, ongoing medical management with primary care and specialist consultations
```

### Expected Results
- **Primary Match**: Comprehensive Health Plus (POL-002)
- **Secondary Match**: Basic Health Insurance (POL-001)
- **Confidence**: 80-95%
- **Action**: CLAIM
- **Reasoning**: Comprehensive coverage includes all services: hospitalization, surgery, outpatient care, dental, and vision - all mentioned in the document

### Key Matching Terms
- Comprehensive care
- Hospitalization
- Surgery
- Outpatient care
- Dental treatment
- Vision care
- Emergency care
- Specialist consultations

---

## Test Case 5: Multiple Policy Match

### Document
**File**: `optimized_emergency_bill.txt`

### Symptoms (Copy & Paste)
```
Emergency hospitalization, cardiac surgery, required immediate medical intervention, life-saving procedure, emergency room care, surgical treatment, intensive care unit admission
```

### Expected Results
- **Match 1**: Basic Health Insurance (POL-001) - 75-85%
- **Match 2**: Comprehensive Health Plus (POL-002) - 70-80%
- **Action**: CLAIM (both policies)
- **Reasoning**: Both policies cover emergency care, hospitalization, and surgery

### Key Matching Terms
- Emergency
- Hospitalization
- Surgery
- Medical intervention
- ICU

---

## Quick Test Symptoms (Short Versions)

### For Diabetes Document
```
Diabetes insulin therapy glucose monitoring specialist visits diabetic supplies
```

### For Emergency Document
```
Emergency heart attack hospitalization cardiac surgery ICU life-threatening
```

### For Surgery Document
```
Emergency appendectomy surgery hospitalization post-operative care
```

### For Comprehensive Document
```
Hospitalization surgery outpatient dental vision emergency comprehensive care
```

---

## Testing Tips

### 1. Use Specific Medical Terms
✅ Good: "Type 2 diabetes mellitus requiring insulin therapy"  
❌ Bad: "Sugar problem need medicine"

### 2. Mention Coverage Areas
✅ Good: "Emergency hospitalization requiring surgery"  
❌ Bad: "Went to hospital"

### 3. Include Multiple Keywords
✅ Good: "Diabetes management, insulin, monitoring supplies, specialist visits"  
❌ Bad: "Diabetes"

### 4. Be Detailed
✅ Good: "Acute appendicitis requiring emergency laparoscopic appendectomy with 3-day hospitalization"  
❌ Bad: "Appendix surgery"

---

## Expected Similarity Scores

With threshold set to 0.3 (30%):

| Document Type | Policy | Expected Score | Status |
|---------------|--------|----------------|--------|
| Diabetes Bill | POL-003 | 0.60-0.80 | ✅ Match |
| Diabetes Bill | POL-002 | 0.35-0.45 | ✅ Match |
| Emergency Bill | POL-001 | 0.70-0.85 | ✅ Match |
| Emergency Bill | POL-002 | 0.65-0.75 | ✅ Match |
| Surgery Bill | POL-001 | 0.75-0.90 | ✅ Match |
| Surgery Bill | POL-002 | 0.70-0.80 | ✅ Match |
| Comprehensive | POL-002 | 0.80-0.95 | ✅ Match |
| Comprehensive | POL-001 | 0.60-0.70 | ✅ Match |

---

## Troubleshooting

### If No Results Returned

1. **Check Threshold**: Should be 0.3 or lower
   ```bash
   aws lambda get-function-configuration \
     --function-name DocumentPolicyProcessor \
     --region us-east-1 \
     --query "Environment.Variables.SIMILARITY_THRESHOLD"
   ```

2. **Check Embeddings**: Verify policy embeddings exist in S3
   ```bash
   aws s3 ls s3://document-policy-processor-uploads/embeddings/
   ```

3. **Check Policies**: Verify policies exist in DynamoDB
   ```bash
   aws dynamodb scan --table-name Policies --region us-east-1
   ```

4. **Check Logs**: View Lambda execution logs
   ```bash
   aws logs tail /aws/lambda/DocumentPolicyProcessor --follow --region us-east-1
   ```

### If Low Confidence Scores

- Add more specific medical terminology
- Include policy-relevant keywords
- Mention specific coverage areas (hospitalization, surgery, etc.)
- Use longer, more detailed symptom descriptions

---

## Demo Script

### For Live Demonstration

1. **Open Streamlit App**
   ```
   https://document-policy-proceappr-azqz9dlbpaj2ls5z98pypi.streamlit.app
   ```

2. **Select Document**
   - Choose: `optimized_diabetes_bill.txt`

3. **Enter Symptoms**
   - Paste: "Type 2 diabetes mellitus requiring insulin therapy, continuous glucose monitoring, blood glucose test strips, diabetic supplies, endocrinologist visits, diabetes management"

4. **Process**
   - Click "Process Document"
   - Wait 30-90 seconds (first request)

5. **Show Results**
   - Point out: Diabetes Care Plan match
   - Highlight: Confidence score (60-80%)
   - Explain: Why it matched (insulin, supplies, specialist visits)

---

## Success Criteria

✅ At least 1 policy recommendation returned  
✅ Confidence score between 30-95%  
✅ Correct policy matched (diabetes → POL-003, emergency → POL-001, etc.)  
✅ Reasoning explains the match  
✅ Action recommendation provided (CLAIM/REVIEW/EXCLUDE)

---

**Last Updated**: March 8, 2026  
**Threshold**: 0.3 (30%)  
**Status**: Optimized for current policy database
