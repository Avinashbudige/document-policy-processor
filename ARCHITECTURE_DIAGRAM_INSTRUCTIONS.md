# How to Create AWS Architecture Diagram

Since the Python script requires Graphviz installation, here are easier alternatives:

## ✅ Option 1: Use Mermaid Diagrams (Recommended - Already Done!)

The **ARCHITECTURE_MERMAID.md** file contains ready-to-use diagrams that render automatically in GitHub!

**View it here**: https://github.com/Avinashbudige/document-policy-processor/blob/main/ARCHITECTURE_MERMAID.md

**For presentations**:
1. Go to https://mermaid.live/
2. Copy any Mermaid code from `ARCHITECTURE_MERMAID.md`
3. Paste into the editor
4. Click "Download PNG" or "Download SVG"
5. Use in your presentation!

## ✅ Option 2: Use AWS Architecture Icons (Professional)

### Step 1: Download AWS Architecture Icons
1. Go to: https://aws.amazon.com/architecture/icons/
2. Click "Download AWS Architecture Icons"
3. Extract the ZIP file

### Step 2: Use draw.io (Free Online Tool)
1. Go to: https://app.diagrams.net/
2. Click "Create New Diagram"
3. Choose "Blank Diagram"
4. Import AWS icons:
   - Click "File" → "Open Library from" → "Device"
   - Navigate to extracted AWS icons folder
   - Select the icon library files

### Step 3: Create Your Diagram
Use this layout based on our architecture:

```
┌─────────────────────────────────────────────────────────────┐
│                     FRONTEND LAYER                           │
│  [User Icon] → [Streamlit Cloud Icon]                       │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│                     API LAYER                                │
│  [API Gateway Icon] - bmi41mg6uf                            │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│                     COMPUTE LAYER                            │
│  [Lambda Icon] - DocumentPolicyProcessor                     │
│  (3GB, 900s timeout, Container)                             │
└─────────────────────────────────────────────────────────────┘
            ↓           ↓           ↓           ↓
┌──────────────┐ ┌──────────────┐ ┌──────────────┐ ┌──────────────┐
│  [S3 Icon]   │ │[DynamoDB Icon]│ │  [ECR Icon]  │ │[External API]│
│  Documents   │ │  Policies &   │ │  Container   │ │  Mistral AI  │
│  Storage     │ │  Jobs Tables  │ │  Registry    │ │              │
└──────────────┘ └──────────────┘ └──────────────┘ └──────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│                  MONITORING & SECURITY                       │
│  [CloudWatch Icon] - Logs & Metrics                         │
│  [IAM Icon] - Roles & Policies                              │
└─────────────────────────────────────────────────────────────┘
```

### AWS Icons to Use:
- **User**: General Icons → Users
- **Streamlit**: Compute → EC2 (or use generic server icon)
- **API Gateway**: Networking & Content Delivery → API Gateway
- **Lambda**: Compute → Lambda
- **S3**: Storage → S3
- **DynamoDB**: Database → DynamoDB
- **ECR**: Containers → Elastic Container Registry
- **CloudWatch**: Management & Governance → CloudWatch
- **IAM**: Security, Identity & Compliance → IAM

### Step 4: Export
- File → Export as → PNG (or SVG for better quality)
- Use in your presentation or documentation

## ✅ Option 3: Use PowerPoint/Google Slides

### Download AWS Icons for PowerPoint
1. Go to: https://aws.amazon.com/architecture/icons/
2. Download "AWS Architecture Icons - PowerPoint"
3. Extract and open the PowerPoint file

### Create Diagram
1. Open PowerPoint or Google Slides
2. Insert AWS icons from the downloaded file
3. Arrange according to the layout above
4. Add arrows and labels
5. Export as image

## ✅ Option 4: Use Lucidchart (Professional)

1. Go to: https://www.lucidchart.com/
2. Sign up for free account
3. Create new diagram
4. Search for "AWS" in shape library
5. Drag and drop AWS icons
6. Export as PNG/PDF

## ✅ Option 5: Use Cloudcraft (AWS-Specific)

1. Go to: https://www.cloudcraft.co/
2. Sign up for free account
3. Use AWS-specific diagram tool
4. Automatically generates professional diagrams
5. Export as PNG/PDF

## 📋 Diagram Components Checklist

Make sure your diagram includes:

- [ ] User/Browser icon
- [ ] Streamlit Cloud (Frontend)
- [ ] API Gateway (with ID: bmi41mg6uf)
- [ ] Lambda Function (with specs: 3GB, 900s)
- [ ] S3 Bucket (document-policy-processor-uploads)
- [ ] DynamoDB Tables (Policies, ProcessingJobs)
- [ ] ECR (Container Registry)
- [ ] Mistral AI (External API)
- [ ] CloudWatch (Monitoring)
- [ ] IAM (Security)
- [ ] Arrows showing data flow
- [ ] Labels for each component

## 🎨 Color Coding Suggestions

- **Frontend**: Light Blue (#E1F5FF)
- **API Layer**: Orange (#FFF3E0)
- **Compute**: Purple (#F3E5F5)
- **Storage**: Green (#E8F5E9)
- **External**: Yellow (#FFF9C4)
- **Monitoring**: Pink (#FCE4EC)

## 📸 Quick Screenshot Alternative

If you need a diagram quickly:

1. Open `ARCHITECTURE_MERMAID.md` in GitHub
2. The Mermaid diagram will render automatically
3. Take a screenshot
4. Crop and use in your presentation

This is the fastest way to get a visual diagram!

## 🚀 For Hackathon Presentation

**Recommended approach**:
1. Use the Mermaid diagram from GitHub (renders automatically)
2. For slides, export from https://mermaid.live/
3. Show the text-based diagram from `AWS_ARCHITECTURE_DIAGRAM.md` for details

**Time required**: 5-10 minutes using Mermaid Live Editor

---

## ❌ Skip Python Script (Optional)

The `generate_architecture_diagram.py` script requires:
- Graphviz installation (complex on Windows)
- Additional system configuration

**Not recommended for quick diagram generation.**

Use Mermaid or draw.io instead - much faster and easier!

---

## 📝 Summary

**Fastest**: Use Mermaid diagrams (already in ARCHITECTURE_MERMAID.md)  
**Most Professional**: Use draw.io with AWS icons  
**For PowerPoint**: Use AWS PowerPoint icons  
**For Web**: Use Cloudcraft or Lucidchart

All options are free and don't require complex installations!

---

**Need help?** The Mermaid diagrams in `ARCHITECTURE_MERMAID.md` are ready to use right now in GitHub!
