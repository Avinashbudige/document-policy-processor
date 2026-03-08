# AWS Architecture - Mermaid Diagram

## Interactive Architecture Diagram

Copy this Mermaid code into GitHub README or any Mermaid-compatible viewer:

```mermaid
graph TB
    subgraph "Frontend Layer"
        User[👤 End User<br/>Browser]
        Streamlit[🌐 Streamlit Cloud<br/>Python Web App<br/>Document Upload UI]
    end
    
    subgraph "API Layer"
        APIGateway[🚪 API Gateway<br/>REST API<br/>bmi41mg6uf<br/>us-east-1]
    end
    
    subgraph "Compute Layer"
        Lambda[⚡ AWS Lambda<br/>DocumentPolicyProcessor<br/>Python 3.11 Container<br/>3GB Memory, 900s Timeout]
        
        subgraph "Processing Components"
            TextExtractor[📄 Text Extractor<br/>Tesseract OCR<br/>PyMuPDF]
            PolicyMatcher[🔍 Policy Matcher<br/>Sentence Transformers<br/>384-dim Embeddings]
            LLMChecker[🤖 LLM Checker<br/>Mistral AI<br/>Exclusion Analysis]
            RecEngine[💡 Recommendation<br/>Engine<br/>Scoring & Priority]
        end
    end
    
    subgraph "Storage Layer"
        S3[🗄️ Amazon S3<br/>document-policy-<br/>processor-uploads<br/>Documents & Embeddings]
        
        subgraph "DynamoDB Tables"
            DynamoPolicies[(📊 Policies Table<br/>Policy Data<br/>& Embeddings)]
            DynamoJobs[(📋 ProcessingJobs<br/>Job Status<br/>& Results)]
        end
        
        ECR[📦 Amazon ECR<br/>Container Registry<br/>Lambda Image<br/>~2.3GB]
    end
    
    subgraph "External Services"
        MistralAI[🌐 Mistral AI API<br/>mistral-small-latest<br/>NLP & Reasoning]
    end
    
    subgraph "Monitoring & Security"
        CloudWatch[📊 CloudWatch<br/>Logs & Metrics<br/>7-day Retention]
        IAM[🔐 IAM<br/>Roles & Policies<br/>Least Privilege]
    end
    
    %% Data Flow
    User -->|HTTPS| Streamlit
    Streamlit -->|REST API<br/>X-Api-Key Auth| APIGateway
    APIGateway -->|Lambda Proxy<br/>Integration| Lambda
    
    Lambda -->|Get/Put<br/>Documents| S3
    Lambda -->|Query/Update<br/>Policies| DynamoPolicies
    Lambda -->|Query/Update<br/>Job Status| DynamoJobs
    Lambda -->|Pull Container<br/>Image| ECR
    Lambda -->|API Call<br/>Exclusion Check| MistralAI
    
    %% Processing Flow
    Lambda --> TextExtractor
    TextExtractor --> PolicyMatcher
    PolicyMatcher --> LLMChecker
    LLMChecker --> RecEngine
    
    %% Monitoring
    APIGateway -.->|Logs| CloudWatch
    Lambda -.->|Logs &<br/>Metrics| CloudWatch
    S3 -.->|Metrics| CloudWatch
    DynamoPolicies -.->|Metrics| CloudWatch
    DynamoJobs -.->|Metrics| CloudWatch
    
    %% Security
    Lambda -.->|Assume<br/>Role| IAM
    APIGateway -.->|Assume<br/>Role| IAM
    
    %% Styling
    classDef frontend fill:#e1f5ff,stroke:#01579b,stroke-width:2px
    classDef api fill:#fff3e0,stroke:#e65100,stroke-width:2px
    classDef compute fill:#f3e5f5,stroke:#4a148c,stroke-width:2px
    classDef storage fill:#e8f5e9,stroke:#1b5e20,stroke-width:2px
    classDef external fill:#fff9c4,stroke:#f57f17,stroke-width:2px
    classDef monitoring fill:#fce4ec,stroke:#880e4f,stroke-width:2px
    
    class User,Streamlit frontend
    class APIGateway api
    class Lambda,TextExtractor,PolicyMatcher,LLMChecker,RecEngine compute
    class S3,DynamoPolicies,DynamoJobs,ECR storage
    class MistralAI external
    class CloudWatch,IAM monitoring
```

## Simplified Flow Diagram

```mermaid
sequenceDiagram
    participant User
    participant Streamlit
    participant APIGateway
    participant Lambda
    participant S3
    participant DynamoDB
    participant MistralAI
    
    User->>Streamlit: Upload Document
    Streamlit->>APIGateway: POST /api/upload-url
    APIGateway->>Lambda: Generate Presigned URL
    Lambda->>S3: Create Presigned URL
    Lambda-->>Streamlit: Return URL
    Streamlit->>S3: Upload Document (Direct)
    
    Streamlit->>APIGateway: POST /api/process-document
    APIGateway->>Lambda: Process Request
    Lambda->>S3: Download Document
    Lambda->>Lambda: Extract Text (OCR)
    Lambda->>DynamoDB: Get Policies
    Lambda->>Lambda: Generate Embeddings
    Lambda->>Lambda: Calculate Similarity
    Lambda->>MistralAI: Check Exclusions
    MistralAI-->>Lambda: Reasoning
    Lambda->>Lambda: Generate Recommendations
    Lambda->>DynamoDB: Save Results
    Lambda-->>Streamlit: Return Job ID
    
    loop Poll Status
        Streamlit->>APIGateway: GET /api/status/{jobId}
        APIGateway->>Lambda: Check Status
        Lambda->>DynamoDB: Query Job
        Lambda-->>Streamlit: Status Update
    end
    
    Streamlit->>APIGateway: GET /api/results/{jobId}
    APIGateway->>Lambda: Get Results
    Lambda->>DynamoDB: Query Results
    Lambda-->>Streamlit: Recommendations
    Streamlit-->>User: Display Results
```

## Component Interaction Diagram

```mermaid
graph LR
    subgraph "Input"
        Doc[📄 Medical<br/>Document]
        Symptoms[💬 Patient<br/>Symptoms]
    end
    
    subgraph "Processing Pipeline"
        Extract[1️⃣ Text<br/>Extraction]
        Embed[2️⃣ Generate<br/>Embeddings]
        Match[3️⃣ Policy<br/>Matching]
        Check[4️⃣ Exclusion<br/>Checking]
        Recommend[5️⃣ Generate<br/>Recommendations]
    end
    
    subgraph "Output"
        Results[📊 Policy<br/>Recommendations<br/>+ Confidence<br/>+ Reasoning]
    end
    
    Doc --> Extract
    Symptoms --> Extract
    Extract --> Embed
    Embed --> Match
    Match --> Check
    Check --> Recommend
    Recommend --> Results
    
    classDef input fill:#e3f2fd,stroke:#1565c0
    classDef process fill:#f3e5f5,stroke:#6a1b9a
    classDef output fill:#e8f5e9,stroke:#2e7d32
    
    class Doc,Symptoms input
    class Extract,Embed,Match,Check,Recommend process
    class Results output
```

## AWS Services Overview

```mermaid
mindmap
  root((Document Policy<br/>Processor))
    Frontend
      Streamlit Cloud
        Python Web App
        Document Upload
        Results Display
    API Layer
      API Gateway
        REST API
        API Key Auth
        CORS Enabled
    Compute
      Lambda Container
        Python 3.11
        3GB Memory
        900s Timeout
        ML Models
    Storage
      S3
        Documents
        Embeddings
        Results
      DynamoDB
        Policies Table
        Jobs Table
      ECR
        Container Image
        2.3GB Size
    External
      Mistral AI
        NLP Analysis
        Reasoning
        Exclusion Check
    Monitoring
      CloudWatch
        Logs
        Metrics
        Alarms
      IAM
        Roles
        Policies
        Security
```

## Cost Architecture

```mermaid
pie title Monthly Cost Breakdown (After Free Tier)
    "Lambda" : 50
    "API Gateway" : 10
    "S3" : 10
    "DynamoDB" : 10
    "CloudWatch" : 10
    "Mistral AI" : 10
```

## Deployment Architecture

```mermaid
graph TB
    subgraph "Development"
        Code[💻 Source Code<br/>Python + CDK]
        Docker[🐳 Dockerfile<br/>Lambda Container]
    end
    
    subgraph "CI/CD"
        Build[🔨 Docker Build<br/>2.3GB Image]
        Push[📤 Push to ECR<br/>Container Registry]
    end
    
    subgraph "Deployment"
        Update[🚀 Update Lambda<br/>Function Code]
        Test[✅ Integration<br/>Testing]
    end
    
    subgraph "Production"
        Live[🌐 Live System<br/>24/7 Available]
    end
    
    Code --> Docker
    Docker --> Build
    Build --> Push
    Push --> Update
    Update --> Test
    Test --> Live
    
    classDef dev fill:#e3f2fd,stroke:#1565c0
    classDef cicd fill:#fff3e0,stroke:#e65100
    classDef deploy fill:#f3e5f5,stroke:#6a1b9a
    classDef prod fill:#e8f5e9,stroke:#2e7d32
    
    class Code,Docker dev
    class Build,Push cicd
    class Update,Test deploy
    class Live prod
```

---

## How to Use These Diagrams

### In GitHub README
1. Copy the Mermaid code blocks
2. Paste into your README.md
3. GitHub will automatically render them

### In Documentation Sites
- **GitBook**: Supports Mermaid natively
- **Docusaurus**: Install `@docusaurus/theme-mermaid`
- **MkDocs**: Install `mkdocs-mermaid2-plugin`

### In Presentations
1. Use [Mermaid Live Editor](https://mermaid.live/)
2. Export as PNG/SVG
3. Insert into PowerPoint/Google Slides

### In Confluence/Notion
1. Use Mermaid Live Editor
2. Export as image
3. Upload to your wiki

---

**Diagram Version**: 1.0  
**Last Updated**: March 8, 2026  
**Format**: Mermaid (GitHub-compatible)
