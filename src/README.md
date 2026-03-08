# Document Policy Processor - Source Code

This directory contains the core modules for the Document Policy Processor application.

## Modules

### TextExtractor (`text_extractor.py`)

Handles text extraction from various document formats using AWS Textract.

**Features:**
- Extract text from PDF documents using AWS Textract
- Extract text from images (PNG, JPG, JPEG) using AWS Textract OCR
- Read plain text files directly
- Normalize extracted text (lowercase, remove extra whitespace, clean special characters)
- Comprehensive error handling for AWS service failures

**Usage:**

```python
from text_extractor import TextExtractor

# Initialize the extractor
extractor = TextExtractor(region_name='us-east-1')

# Extract from PDF
text = extractor.extract_from_pdf('document.pdf')

# Extract from image
text = extractor.extract_from_image('scan.png')

# Extract from text file
text = extractor.extract_from_text('notes.txt')

# Normalize extracted text
normalized = extractor.normalize_text(text)
```

**Requirements:**
- boto3 >= 1.34.0
- AWS credentials configured with Textract permissions

**Error Handling:**
- `FileNotFoundError`: File doesn't exist
- `ValueError`: Invalid file format
- `RuntimeError`: AWS Textract or connection failures

## Testing

Run tests from the `tests/` directory:

```bash
cd tests
pip install -r requirements.txt
pytest test_text_extractor.py -v
```

## Dependencies

Install dependencies:

```bash
pip install -r requirements.txt
```
