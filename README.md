# Document Policy Processor

An AWS-based intelligent document processing system that analyzes insurance documents and symptom descriptions to provide policy recommendations through OCR/NLP parsing, semantic policy matching, and LLM-based validation.

## Overview

The Document Policy Processor leverages AWS services and AI to:
- Extract text from documents (PDF, PNG, JPG, TXT) using AWS Textract
- Match document content against insurance policies using semantic embeddings
- Validate policy applicability with LLM-based exclusion checking
- Generate actionable recommendations with confidence scores

## Features

- **Multi-format Document Support**: Process PDFs, images, and text files
- **Semantic Policy Matching**: Find relevant policies using sentence embeddings
- **AI-Powered Validation**: LLM-based exclusion checking for accurate recommendations
- **Serverless Architecture**: Built on AWS Lambda, API Gateway, S3, and DynamoDB
- **Real-time Processing**: Fast document analysis and recommendation generation

## AWS Services Used

- AWS Lambda - Serverless compute for document processing
- AWS Textract - OCR and text extraction
- Amazon S3 - Document and embedding storage
- Amazon DynamoDB - Policy and job data storage
- Amazon API Gateway - RESTful API endpoints
- AWS CloudWatch - Monitoring and logging

## Project Structure

```
document-policy-processor/
├── src/              # Source code
├── tests/            # Test files
├── docs/             # Documentation
├── infrastructure/   # Infrastructure as code
├── README.md         # This file
├── .gitignore        # Git ignore rules
└── LICENSE           # License file
```

## Getting Started

Documentation for setup, deployment, and usage will be added as the project develops.

## License

This project is licensed under the MIT License - see the LICENSE file for details.
