"""
Text Extraction Module for Document Policy Processor

This module handles text extraction from various document formats (PDF, images, plain text)
using AWS Textract for OCR capabilities.
"""

import re
import logging
from typing import Optional
from pathlib import Path

import boto3
from botocore.exceptions import ClientError, BotoCoreError

# Configure logging
logger = logging.getLogger(__name__)


class TextExtractor:
    """
    Extracts text from various document formats using AWS Textract and fallback methods.
    
    Supports:
    - PDF documents (via AWS Textract)
    - Image files: PNG, JPG, JPEG (via AWS Textract)
    - Plain text files (direct reading)
    """
    
    def __init__(self, region_name: str = 'us-east-1'):
        """
        Initialize TextExtractor with AWS Textract client.
        
        Args:
            region_name: AWS region for Textract service
        """
        self.textract_client = boto3.client('textract', region_name=region_name)
        self.s3_client = boto3.client('s3', region_name=region_name)
        
    def extract_from_pdf(self, file_path: str) -> str:
        """
        Extract text from PDF using AWS Textract.
        
        Args:
            file_path: Path to the PDF file
            
        Returns:
            Extracted text as a string
            
        Raises:
            FileNotFoundError: If the file doesn't exist
            ValueError: If the file is not a valid PDF
            RuntimeError: If Textract extraction fails
        """
        path = Path(file_path)
        
        if not path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
            
        if path.suffix.lower() != '.pdf':
            raise ValueError(f"File is not a PDF: {file_path}")
        
        try:
            # Read the PDF file
            with open(file_path, 'rb') as document:
                document_bytes = document.read()
            
            # Call Textract to detect document text
            response = self.textract_client.detect_document_text(
                Document={'Bytes': document_bytes}
            )
            
            # Extract text from response
            text = self._extract_text_from_response(response)
            
            logger.info(f"Successfully extracted text from PDF: {file_path}")
            return text
            
        except ClientError as e:
            error_code = e.response['Error']['Code']
            error_message = e.response['Error']['Message']
            logger.error(f"AWS Textract error ({error_code}): {error_message}")
            raise RuntimeError(f"Textract extraction failed: {error_message}") from e
            
        except BotoCoreError as e:
            logger.error(f"AWS connection error: {str(e)}")
            raise RuntimeError(f"AWS connection failed: {str(e)}") from e
            
        except Exception as e:
            logger.error(f"Unexpected error during PDF extraction: {str(e)}")
            raise RuntimeError(f"PDF extraction failed: {str(e)}") from e
    
    def extract_from_image(self, file_path: str) -> str:
        """
        Extract text from image using AWS Textract.
        
        Supports: PNG, JPG, JPEG formats
        
        Args:
            file_path: Path to the image file
            
        Returns:
            Extracted text as a string
            
        Raises:
            FileNotFoundError: If the file doesn't exist
            ValueError: If the file is not a supported image format
            RuntimeError: If Textract extraction fails
        """
        path = Path(file_path)
        
        if not path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
            
        supported_formats = {'.png', '.jpg', '.jpeg'}
        if path.suffix.lower() not in supported_formats:
            raise ValueError(
                f"Unsupported image format: {path.suffix}. "
                f"Supported formats: {', '.join(supported_formats)}"
            )
        
        try:
            # Read the image file
            with open(file_path, 'rb') as document:
                document_bytes = document.read()
            
            # Call Textract to detect document text
            response = self.textract_client.detect_document_text(
                Document={'Bytes': document_bytes}
            )
            
            # Extract text from response
            text = self._extract_text_from_response(response)
            
            logger.info(f"Successfully extracted text from image: {file_path}")
            return text
            
        except ClientError as e:
            error_code = e.response['Error']['Code']
            error_message = e.response['Error']['Message']
            logger.error(f"AWS Textract error ({error_code}): {error_message}")
            raise RuntimeError(f"Textract extraction failed: {error_message}") from e
            
        except BotoCoreError as e:
            logger.error(f"AWS connection error: {str(e)}")
            raise RuntimeError(f"AWS connection failed: {str(e)}") from e
            
        except Exception as e:
            logger.error(f"Unexpected error during image extraction: {str(e)}")
            raise RuntimeError(f"Image extraction failed: {str(e)}") from e
    
    def extract_from_text(self, file_path: str) -> str:
        """
        Extract text from plain text file.
        
        Args:
            file_path: Path to the text file
            
        Returns:
            File contents as a string
            
        Raises:
            FileNotFoundError: If the file doesn't exist
            ValueError: If the file is not a text file
            RuntimeError: If reading fails
        """
        path = Path(file_path)
        
        if not path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
            
        if path.suffix.lower() != '.txt':
            raise ValueError(f"File is not a text file: {file_path}")
        
        try:
            # Read the text file with UTF-8 encoding
            with open(file_path, 'r', encoding='utf-8') as f:
                text = f.read()
            
            logger.info(f"Successfully read text file: {file_path}")
            return text
            
        except UnicodeDecodeError:
            # Try with latin-1 encoding as fallback
            try:
                with open(file_path, 'r', encoding='latin-1') as f:
                    text = f.read()
                logger.warning(f"Read text file with latin-1 encoding: {file_path}")
                return text
            except Exception as e:
                logger.error(f"Failed to read text file with fallback encoding: {str(e)}")
                raise RuntimeError(f"Text file reading failed: {str(e)}") from e
                
        except Exception as e:
            logger.error(f"Unexpected error reading text file: {str(e)}")
            raise RuntimeError(f"Text file reading failed: {str(e)}") from e
    
    def normalize_text(self, text: str) -> str:
        """
        Clean and normalize extracted text.
        
        Performs:
        - Removes extra whitespace
        - Normalizes line breaks
        - Removes special characters (preserves alphanumeric and basic punctuation)
        - Converts to lowercase
        - Strips leading/trailing whitespace
        
        Args:
            text: Raw extracted text
            
        Returns:
            Normalized text string
        """
        if not text:
            return ""
        
        # Replace multiple whitespace with single space
        text = re.sub(r'\s+', ' ', text)
        
        # Remove special characters but keep alphanumeric, spaces, and basic punctuation
        text = re.sub(r'[^\w\s.,!?;:()\-]', '', text)
        
        # Convert to lowercase
        text = text.lower()
        
        # Strip leading/trailing whitespace
        text = text.strip()
        
        return text
    
    def _extract_text_from_response(self, response: dict) -> str:
        """
        Extract text from Textract API response.
        
        Args:
            response: Textract detect_document_text response
            
        Returns:
            Concatenated text from all blocks
        """
        text_blocks = []
        
        # Extract LINE blocks (which contain the actual text lines)
        for block in response.get('Blocks', []):
            if block['BlockType'] == 'LINE':
                text_blocks.append(block.get('Text', ''))
        
        # Join with newlines to preserve document structure
        return '\n'.join(text_blocks)
