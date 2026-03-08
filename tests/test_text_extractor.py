"""
Unit tests for TextExtractor class
"""

import pytest
from unittest.mock import Mock, patch, mock_open
from pathlib import Path
from botocore.exceptions import ClientError, BotoCoreError

import sys
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from text_extractor import TextExtractor


class TestTextExtractor:
    """Test suite for TextExtractor class"""
    
    @pytest.fixture
    def extractor(self):
        """Create a TextExtractor instance with mocked AWS clients"""
        with patch('text_extractor.boto3.client'):
            return TextExtractor()
    
    @pytest.fixture
    def mock_textract_response(self):
        """Mock Textract API response"""
        return {
            'Blocks': [
                {
                    'BlockType': 'LINE',
                    'Text': 'This is line one'
                },
                {
                    'BlockType': 'LINE',
                    'Text': 'This is line two'
                },
                {
                    'BlockType': 'WORD',
                    'Text': 'ignored'
                }
            ]
        }
    
    # Tests for extract_from_pdf
    
    def test_extract_from_pdf_success(self, extractor, mock_textract_response, tmp_path):
        """Test successful PDF text extraction"""
        # Create a temporary PDF file
        pdf_file = tmp_path / "test.pdf"
        pdf_file.write_bytes(b"fake pdf content")
        
        # Mock Textract response
        extractor.textract_client.detect_document_text = Mock(
            return_value=mock_textract_response
        )
        
        # Extract text
        result = extractor.extract_from_pdf(str(pdf_file))
        
        # Verify
        assert result == "This is line one\nThis is line two"
        extractor.textract_client.detect_document_text.assert_called_once()
    
    def test_extract_from_pdf_file_not_found(self, extractor):
        """Test PDF extraction with non-existent file"""
        with pytest.raises(FileNotFoundError, match="File not found"):
            extractor.extract_from_pdf("/nonexistent/file.pdf")
    
    def test_extract_from_pdf_invalid_extension(self, extractor, tmp_path):
        """Test PDF extraction with non-PDF file"""
        txt_file = tmp_path / "test.txt"
        txt_file.write_text("content")
        
        with pytest.raises(ValueError, match="File is not a PDF"):
            extractor.extract_from_pdf(str(txt_file))
    
    def test_extract_from_pdf_textract_error(self, extractor, tmp_path):
        """Test PDF extraction with Textract API error"""
        pdf_file = tmp_path / "test.pdf"
        pdf_file.write_bytes(b"fake pdf content")
        
        # Mock Textract error
        error_response = {'Error': {'Code': 'InvalidParameterException', 'Message': 'Invalid document'}}
        extractor.textract_client.detect_document_text = Mock(
            side_effect=ClientError(error_response, 'detect_document_text')
        )
        
        with pytest.raises(RuntimeError, match="Textract extraction failed"):
            extractor.extract_from_pdf(str(pdf_file))
    
    def test_extract_from_pdf_connection_error(self, extractor, tmp_path):
        """Test PDF extraction with AWS connection error"""
        pdf_file = tmp_path / "test.pdf"
        pdf_file.write_bytes(b"fake pdf content")
        
        # Mock connection error
        extractor.textract_client.detect_document_text = Mock(
            side_effect=BotoCoreError()
        )
        
        with pytest.raises(RuntimeError, match="AWS connection failed"):
            extractor.extract_from_pdf(str(pdf_file))
    
    # Tests for extract_from_image
    
    def test_extract_from_image_png_success(self, extractor, mock_textract_response, tmp_path):
        """Test successful PNG image text extraction"""
        img_file = tmp_path / "test.png"
        img_file.write_bytes(b"fake png content")
        
        extractor.textract_client.detect_document_text = Mock(
            return_value=mock_textract_response
        )
        
        result = extractor.extract_from_image(str(img_file))
        
        assert result == "This is line one\nThis is line two"
        extractor.textract_client.detect_document_text.assert_called_once()
    
    def test_extract_from_image_jpg_success(self, extractor, mock_textract_response, tmp_path):
        """Test successful JPG image text extraction"""
        img_file = tmp_path / "test.jpg"
        img_file.write_bytes(b"fake jpg content")
        
        extractor.textract_client.detect_document_text = Mock(
            return_value=mock_textract_response
        )
        
        result = extractor.extract_from_image(str(img_file))
        
        assert result == "This is line one\nThis is line two"
    
    def test_extract_from_image_jpeg_success(self, extractor, mock_textract_response, tmp_path):
        """Test successful JPEG image text extraction"""
        img_file = tmp_path / "test.jpeg"
        img_file.write_bytes(b"fake jpeg content")
        
        extractor.textract_client.detect_document_text = Mock(
            return_value=mock_textract_response
        )
        
        result = extractor.extract_from_image(str(img_file))
        
        assert result == "This is line one\nThis is line two"
    
    def test_extract_from_image_file_not_found(self, extractor):
        """Test image extraction with non-existent file"""
        with pytest.raises(FileNotFoundError, match="File not found"):
            extractor.extract_from_image("/nonexistent/image.png")
    
    def test_extract_from_image_unsupported_format(self, extractor, tmp_path):
        """Test image extraction with unsupported format"""
        bmp_file = tmp_path / "test.bmp"
        bmp_file.write_bytes(b"fake bmp content")
        
        with pytest.raises(ValueError, match="Unsupported image format"):
            extractor.extract_from_image(str(bmp_file))
    
    def test_extract_from_image_textract_error(self, extractor, tmp_path):
        """Test image extraction with Textract API error"""
        img_file = tmp_path / "test.png"
        img_file.write_bytes(b"fake png content")
        
        error_response = {'Error': {'Code': 'InvalidParameterException', 'Message': 'Invalid image'}}
        extractor.textract_client.detect_document_text = Mock(
            side_effect=ClientError(error_response, 'detect_document_text')
        )
        
        with pytest.raises(RuntimeError, match="Textract extraction failed"):
            extractor.extract_from_image(str(img_file))
    
    # Tests for extract_from_text
    
    def test_extract_from_text_success(self, extractor, tmp_path):
        """Test successful text file reading"""
        txt_file = tmp_path / "test.txt"
        txt_file.write_text("This is a test file\nWith multiple lines")
        
        result = extractor.extract_from_text(str(txt_file))
        
        assert result == "This is a test file\nWith multiple lines"
    
    def test_extract_from_text_file_not_found(self, extractor):
        """Test text extraction with non-existent file"""
        with pytest.raises(FileNotFoundError, match="File not found"):
            extractor.extract_from_text("/nonexistent/file.txt")
    
    def test_extract_from_text_invalid_extension(self, extractor, tmp_path):
        """Test text extraction with non-text file"""
        pdf_file = tmp_path / "test.pdf"
        pdf_file.write_bytes(b"content")
        
        with pytest.raises(ValueError, match="File is not a text file"):
            extractor.extract_from_text(str(pdf_file))
    
    def test_extract_from_text_utf8_encoding(self, extractor, tmp_path):
        """Test text extraction with UTF-8 encoding"""
        txt_file = tmp_path / "test.txt"
        txt_file.write_text("Hello 世界", encoding='utf-8')
        
        result = extractor.extract_from_text(str(txt_file))
        
        assert "Hello" in result
    
    def test_extract_from_text_latin1_fallback(self, extractor, tmp_path):
        """Test text extraction with latin-1 fallback encoding"""
        txt_file = tmp_path / "test.txt"
        # Write with latin-1 encoding
        txt_file.write_bytes("Café".encode('latin-1'))
        
        result = extractor.extract_from_text(str(txt_file))
        
        assert "Caf" in result
    
    # Tests for normalize_text
    
    def test_normalize_text_basic(self, extractor):
        """Test basic text normalization"""
        text = "  Hello   World  "
        result = extractor.normalize_text(text)
        assert result == "hello world"
    
    def test_normalize_text_multiple_whitespace(self, extractor):
        """Test normalization of multiple whitespace"""
        text = "Hello\n\n\nWorld\t\tTest"
        result = extractor.normalize_text(text)
        assert result == "hello world test"
    
    def test_normalize_text_special_characters(self, extractor):
        """Test removal of special characters"""
        text = "Hello@#$%World!"
        result = extractor.normalize_text(text)
        assert result == "helloworld!"
    
    def test_normalize_text_preserve_punctuation(self, extractor):
        """Test preservation of basic punctuation"""
        text = "Hello, World! How are you?"
        result = extractor.normalize_text(text)
        assert "," in result
        assert "!" in result
        assert "?" in result
    
    def test_normalize_text_empty_string(self, extractor):
        """Test normalization of empty string"""
        result = extractor.normalize_text("")
        assert result == ""
    
    def test_normalize_text_none(self, extractor):
        """Test normalization of None"""
        result = extractor.normalize_text(None)
        assert result == ""
    
    def test_normalize_text_lowercase_conversion(self, extractor):
        """Test lowercase conversion"""
        text = "HELLO WORLD"
        result = extractor.normalize_text(text)
        assert result == "hello world"
    
    def test_normalize_text_preserve_numbers(self, extractor):
        """Test preservation of numbers"""
        text = "Policy 12345 covers $1000"
        result = extractor.normalize_text(text)
        assert "12345" in result
        assert "1000" in result
    
    # Tests for _extract_text_from_response
    
    def test_extract_text_from_response_multiple_lines(self, extractor):
        """Test extraction from response with multiple LINE blocks"""
        response = {
            'Blocks': [
                {'BlockType': 'LINE', 'Text': 'Line 1'},
                {'BlockType': 'LINE', 'Text': 'Line 2'},
                {'BlockType': 'LINE', 'Text': 'Line 3'}
            ]
        }
        
        result = extractor._extract_text_from_response(response)
        assert result == "Line 1\nLine 2\nLine 3"
    
    def test_extract_text_from_response_ignore_non_line_blocks(self, extractor):
        """Test that non-LINE blocks are ignored"""
        response = {
            'Blocks': [
                {'BlockType': 'LINE', 'Text': 'Line 1'},
                {'BlockType': 'WORD', 'Text': 'Word 1'},
                {'BlockType': 'PAGE', 'Text': 'Page 1'},
                {'BlockType': 'LINE', 'Text': 'Line 2'}
            ]
        }
        
        result = extractor._extract_text_from_response(response)
        assert result == "Line 1\nLine 2"
    
    def test_extract_text_from_response_empty_blocks(self, extractor):
        """Test extraction from response with no blocks"""
        response = {'Blocks': []}
        
        result = extractor._extract_text_from_response(response)
        assert result == ""
    
    def test_extract_text_from_response_missing_text(self, extractor):
        """Test extraction when Text field is missing"""
        response = {
            'Blocks': [
                {'BlockType': 'LINE', 'Text': 'Line 1'},
                {'BlockType': 'LINE'},  # Missing Text field
                {'BlockType': 'LINE', 'Text': 'Line 3'}
            ]
        }
        
        result = extractor._extract_text_from_response(response)
        assert result == "Line 1\n\nLine 3"


# Edge case tests

class TestTextExtractorEdgeCases:
    """Test edge cases and error conditions"""
    
    @pytest.fixture
    def extractor(self):
        with patch('text_extractor.boto3.client'):
            return TextExtractor()
    
    def test_extract_from_pdf_empty_response(self, extractor, tmp_path):
        """Test PDF extraction with empty Textract response"""
        pdf_file = tmp_path / "test.pdf"
        pdf_file.write_bytes(b"fake pdf content")
        
        extractor.textract_client.detect_document_text = Mock(
            return_value={'Blocks': []}
        )
        
        result = extractor.extract_from_pdf(str(pdf_file))
        assert result == ""
    
    def test_extract_from_text_empty_file(self, extractor, tmp_path):
        """Test text extraction from empty file"""
        txt_file = tmp_path / "empty.txt"
        txt_file.write_text("")
        
        result = extractor.extract_from_text(str(txt_file))
        assert result == ""
    
    def test_normalize_text_only_whitespace(self, extractor):
        """Test normalization of whitespace-only string"""
        text = "   \n\n\t\t   "
        result = extractor.normalize_text(text)
        assert result == ""
    
    def test_normalize_text_only_special_characters(self, extractor):
        """Test normalization of special characters only"""
        text = "@#$%^&*"
        result = extractor.normalize_text(text)
        assert result == ""
