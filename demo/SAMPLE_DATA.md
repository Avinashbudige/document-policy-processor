# Sample Documents and Test Data for Demo Video

This file contains sample documents and test data to use during the demo video recording.

---

## Sample Document 1: Medical Report (Primary Demo)

**File Name**: `sample_medical_report.txt`

**Content**:
```
MEDICAL REPORT

Patient: John Doe
Date: January 20, 2025
Provider: Dr. Sarah Johnson, MD

DIAGNOSIS:
Type 2 Diabetes Mellitus (E11.9)

CLINICAL FINDINGS:
Patient presents with elevated blood glucose levels (HbA1c: 8.2%). 
Symptoms include increased thirst, frequent urination, and fatigue.
Physical examination reveals no acute complications.

TREATMENT PLAN:
1. Insulin therapy - Lantus 20 units daily
2. Blood glucose monitoring - 4 times daily
3. Dietary modifications - low carbohydrate diet
4. Regular follow-up appointments every 3 months

MEDICATIONS PRESCRIBED:
- Insulin glargine (Lantus) 100 units/mL
- Metformin 500mg twice daily
- Blood glucose test strips (100 count)

RECOMMENDATIONS:
Patient requires ongoing diabetes management including insulin therapy,
regular monitoring, and lifestyle modifications. Coverage for diabetic
supplies and medications is essential for proper disease management.

Dr. Sarah Johnson, MD
License #: MD-12345
```

**Why This Document**:
- Clear medical diagnosis
- Specific treatment requirements
- Mentions medications and supplies
- Professional format
- Easy to read on screen

**Corresponding Symptoms**:
"Diagnosed with Type 2 diabetes, requiring insulin therapy and regular monitoring"

**Expected Results**:
- Should match "Comprehensive Health Plus" (high confidence)
- Should match "Basic Health Insurance" (medium confidence, with exclusions)
- Should recommend proceeding with claim for comprehensive policy

---

## Sample Document 2: Prescription (Alternative)

**File Name**: `sample_prescription.txt`

**Content**:
```
PRESCRIPTION

Patient: Jane Smith
Date: January 22, 2025
Provider: Dr. Michael Chen, MD

Rx:
1. Lisinopril 10mg - Take 1 tablet daily for hypertension
2. Atorvastatin 20mg - Take 1 tablet daily for cholesterol
3. Aspirin 81mg - Take 1 tablet daily for cardiovascular protection

Diagnosis: Hypertension (I10), Hyperlipidemia (E78.5)

Refills: 3 months supply with 2 refills

Dr. Michael Chen, MD
```

**Corresponding Symptoms**:
"High blood pressure and high cholesterol, need ongoing medication"

---

## Sample Document 3: Hospital Bill (Alternative)

**File Name**: `sample_hospital_bill.txt`

**Content**:
```
HOSPITAL BILLING STATEMENT

Patient: Robert Williams
Date of Service: January 15, 2025
Facility: City General Hospital

SERVICES PROVIDED:
- Emergency Room Visit: $850.00
- X-Ray (Chest): $320.00
- Laboratory Tests: $180.00
- Physician Consultation: $250.00

DIAGNOSIS: Pneumonia (J18.9)

TOTAL CHARGES: $1,600.00

TREATMENT SUMMARY:
Patient presented to ER with severe cough, fever, and difficulty breathing.
Chest X-ray confirmed pneumonia. Prescribed antibiotics and discharged
with follow-up instructions.
```

**Corresponding Symptoms**:
"Hospitalized for pneumonia, need to file insurance claim"

---

## Sample Symptom Descriptions

### For Diabetes Document (Primary)
```
Diagnosed with Type 2 diabetes, requiring insulin therapy and regular monitoring
```

### Alternative Diabetes Symptoms
```
Recently diagnosed with diabetes. Doctor prescribed insulin and blood sugar testing supplies. Need to know which policy covers these medications and supplies.
```

### For Hypertension Document
```
High blood pressure and high cholesterol, need ongoing medication
```

### For Hospital Bill
```
Hospitalized for pneumonia, need to file insurance claim
```

### Generic Symptoms (Fallback)
```
Chronic medical condition requiring ongoing treatment and medication. Need to understand my insurance coverage options.
```

---

## Sample Policies in Database

These are the policies that should be in your DynamoDB table for the demo:

### Policy 1: Comprehensive Health Plus
```json
{
  "policy_id": "POL-001",
  "policy_name": "Comprehensive Health Plus",
  "policy_text": "Comprehensive health insurance covering all medical expenses including hospitalization, outpatient care, prescription medications, diabetic supplies, and preventive care. Coverage includes insulin therapy, blood glucose monitoring equipment, and diabetes management programs. No exclusions for Type 2 diabetes. Pre-existing conditions covered after 6 months.",
  "category": "health",
  "coverage_details": {
    "hospitalization": true,
    "outpatient": true,
    "prescriptions": true,
    "diabetic_supplies": true,
    "preventive_care": true
  },
  "exclusions": [
    "Cosmetic procedures",
    "Experimental treatments"
  ]
}
```

### Policy 2: Basic Health Insurance
```json
{
  "policy_id": "POL-002",
  "policy_name": "Basic Health Insurance",
  "policy_text": "Basic health insurance covering hospitalization, emergency care, and surgery. Limited outpatient coverage. Pre-existing conditions excluded for first 2 years. Does not cover diabetic supplies or ongoing medication management for chronic conditions diagnosed before policy start date.",
  "category": "health",
  "coverage_details": {
    "hospitalization": true,
    "emergency": true,
    "surgery": true,
    "outpatient": "limited"
  },
  "exclusions": [
    "Pre-existing conditions (first 2 years)",
    "Diabetic supplies",
    "Chronic medication management"
  ]
}
```

### Policy 3: Premium Care Plan
```json
{
  "policy_id": "POL-003",
  "policy_name": "Premium Care Plan",
  "policy_text": "Premium health insurance with comprehensive coverage including all medical services, prescription drugs, medical equipment, home healthcare, and wellness programs. Covers all chronic conditions including diabetes with no waiting period. Includes coverage for insulin pumps, continuous glucose monitors, and diabetes education programs.",
  "category": "health",
  "coverage_details": {
    "all_medical_services": true,
    "prescriptions": true,
    "medical_equipment": true,
    "home_healthcare": true,
    "wellness_programs": true,
    "advanced_diabetic_care": true
  },
  "exclusions": [
    "Cosmetic procedures"
  ]
}
```

---

## Expected Demo Results

When processing the primary medical report with diabetes symptoms, the system should return:

### Recommendation 1: Comprehensive Health Plus
- **Confidence**: 92-95%
- **Action**: "Proceed with claim"
- **Reasoning**: "Policy explicitly covers insulin therapy, blood glucose monitoring, and diabetic supplies. No exclusions for Type 2 diabetes. Patient's treatment plan aligns perfectly with policy coverage."
- **Next Steps**:
  - Submit claim with medical report and prescription
  - Include itemized list of diabetic supplies needed
  - Expect approval within 5-7 business days

### Recommendation 2: Premium Care Plan
- **Confidence**: 88-92%
- **Action**: "Proceed with claim"
- **Reasoning**: "Comprehensive coverage includes all aspects of diabetes management. No waiting period for chronic conditions. Covers advanced equipment like insulin pumps if needed."
- **Next Steps**:
  - Submit claim with complete medical documentation
  - Consider requesting coverage for continuous glucose monitor
  - Contact provider for diabetes education program enrollment

### Recommendation 3: Basic Health Insurance
- **Confidence**: 65-75%
- **Action**: "Review with agent"
- **Reasoning**: "Policy covers hospitalization but excludes diabetic supplies and chronic medication management. Pre-existing condition exclusion may apply if diabetes was diagnosed before policy start date."
- **Exclusions Found**:
  - Pre-existing conditions (first 2 years)
  - Diabetic supplies not covered
  - Ongoing medication management excluded
- **Next Steps**:
  - Contact insurance agent to verify policy start date
  - Check if diabetes diagnosis predates policy
  - Consider upgrading to comprehensive plan

---

## Creating Sample Documents

### Option 1: Text Files (Easiest)
1. Copy the content above into a text file
2. Save as `sample_medical_report.txt`
3. Use this for the demo

### Option 2: PDF (More Professional)
1. Copy content into Microsoft Word or Google Docs
2. Format with proper headers and spacing
3. Add a simple header/footer
4. Export as PDF
5. Save as `sample_medical_report.pdf`

### Option 3: Image (Shows OCR Capability)
1. Create PDF as above
2. Take a screenshot or convert to PNG/JPG
3. Save as `sample_medical_report.png`
4. This demonstrates the OCR capability

---

## Demo Data Checklist

Before recording, ensure you have:

- [ ] Primary medical report document (text, PDF, or image)
- [ ] Symptom description copied and ready to paste
- [ ] All sample policies loaded in DynamoDB
- [ ] Policy embeddings pre-computed and in S3
- [ ] Test the complete flow at least once
- [ ] Verify results are impressive (high confidence scores)
- [ ] Backup documents ready in case of issues
- [ ] Document files named clearly and professionally

---

## Testing Your Sample Data

Before recording the demo, test your sample data:

```bash
# Test 1: Upload the document through the UI
# Expected: Upload succeeds, file appears in S3

# Test 2: Process with symptoms
# Expected: Processing completes in 30-60 seconds

# Test 3: Check results
# Expected: 2-3 policy matches with confidence > 70%

# Test 4: Verify reasoning
# Expected: Clear, human-readable explanations

# Test 5: Check for exclusions
# Expected: Basic Health Insurance shows exclusions
```

---

## Troubleshooting Sample Data

### If confidence scores are too low:
- Ensure policy text includes keywords from the medical report
- Verify embeddings are properly generated
- Check that symptoms match policy coverage areas

### If no matches are found:
- Verify policies are in DynamoDB
- Check that embeddings are loaded correctly
- Ensure similarity threshold isn't too high

### If LLM returns errors:
- Check OpenAI API key is valid
- Verify API quota isn't exceeded
- Test with simpler policy text

### If processing takes too long:
- Use smaller document (text file instead of large PDF)
- Reduce number of policies in database
- Check Lambda timeout settings

---

## Alternative Demo Scenarios

If you want to show multiple use cases:

### Scenario 1: Diabetes Management (Primary)
- Document: Medical report with diabetes diagnosis
- Symptoms: Insulin therapy and monitoring
- Expected: High confidence match with comprehensive plans

### Scenario 2: Emergency Care
- Document: Hospital bill for emergency visit
- Symptoms: Emergency hospitalization
- Expected: Matches all policies (basic coverage)

### Scenario 3: Chronic Medication
- Document: Prescription for ongoing medication
- Symptoms: Need coverage for regular prescriptions
- Expected: Mixed results showing coverage differences

---

## Tips for Impressive Demo Results

1. **Use realistic medical terminology** - Makes it look professional
2. **Ensure high confidence scores** - Adjust policy text if needed
3. **Show clear exclusions** - Demonstrates AI understanding
4. **Include specific next steps** - Shows practical value
5. **Use professional document formatting** - Looks polished on screen

---

## Final Checklist

Before recording:

- [ ] Sample documents created and tested
- [ ] Symptoms prepared and tested
- [ ] Results are impressive and clear
- [ ] All policies loaded in database
- [ ] Embeddings pre-computed
- [ ] Complete workflow tested end-to-end
- [ ] Backup documents ready
- [ ] Know exactly which document to use
- [ ] Know exactly what symptoms to type
- [ ] Confident in the expected results
