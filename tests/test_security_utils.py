import os
import sys

# Add the repository root to sys.path to allow direct execution
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

import pytest
from unittest.mock import patch, MagicMock
import tempfile
from MyFlaskapp.security_utils import (
    allowed_file, validate_file_upload, safe_file_save,
    validate_game_file_path, sanitize_score
)

@pytest.fixture
def app():
    from MyFlaskapp import create_app
    app = create_app()
    app.config['TESTING'] = True
    return app

class TestSecurityUtils:
    def test_allowed_file_valid_extensions(self):
        """Test allowed file extensions."""
        valid_files = [
            'image.png',
            'photo.jpg',
            'picture.jpeg',
            'animation.gif',
            'modern.webp',
            'IMAGE.PNG',  # Test case insensitive
            'photo.JPG'
        ]
        for filename in valid_files:
            assert allowed_file(filename) is True

    def test_allowed_file_invalid_extensions(self):
        """Test invalid file extensions."""
        invalid_files = [
            'document.pdf',
            'script.js',
            'executable.exe',
            'archive.zip',
            'video.mp4',
            'file',  # No extension
            '.hidden',  # Hidden file without extension
            'file.txt.exe'  # Double extension
        ]
        for filename in invalid_files:
            assert allowed_file(filename) is False

    def test_validate_file_upload_no_file(self):
        """Test file upload validation with no file."""
        result = validate_file_upload(None)
        assert result[0] is False  # is_valid
        assert result[1] == "No file selected"  # error_message
        assert result[2] is None  # safe_filename

    def test_validate_file_upload_no_filename(self):
        """Test file upload validation with empty filename."""
        mock_file = MagicMock()
        mock_file.filename = None
        
        result = validate_file_upload(mock_file)
        assert result[0] is False
        assert result[1] == "No file selected"
        assert result[2] is None

    def test_validate_file_upload_too_large(self):
        """Test file upload validation with oversized file."""
        mock_file = MagicMock()
        mock_file.filename = 'image.png'
        mock_file.content_length = 10 * 1024 * 1024  # 10MB (over 5MB limit)
        
        result = validate_file_upload(mock_file)
        assert result[0] is False
        assert "File too large" in result[1]

    def test_validate_file_upload_invalid_extension(self):
        """Test file upload validation with invalid extension."""
        mock_file = MagicMock()
        mock_file.filename = 'document.pdf'
        mock_file.content_length = 1024  # 1KB
        
        result = validate_file_upload(mock_file)
        assert result[0] is False
        assert "Invalid file type" in result[1]

    def test_validate_file_upload_success(self):
        """Test successful file upload validation."""
        mock_file = MagicMock()
        mock_file.filename = 'image.png'
        mock_file.content_length = 1024  # 1KB
        mock_file.read.return_value = b'\x89PNG\r\n\x1a\n...'  # PNG header
        mock_file.seek.return_value = None
        
        result = validate_file_upload(mock_file)
        assert result[0] is True
        assert result[1] is None
        assert result[2] == 'image.png'

    @patch('MyFlaskapp.security_utils.os.makedirs')
    @patch('MyFlaskapp.security_utils.uuid.uuid4')
    def test_safe_file_save_success(self, mock_uuid, mock_makedirs, app):
        """Test successful safe file save."""
        mock_uuid.return_value.hex = 'test123'
        mock_file = MagicMock()
        mock_file.filename = 'image.png'
        mock_file.content_length = 1024
        mock_file.read.return_value = b'fake image data'
        mock_file.seek.return_value = None
        mock_file.save.return_value = None
        
        with app.app_context():
            with patch('MyFlaskapp.security_utils.validate_file_upload') as mock_validate:
                mock_validate.return_value = (True, None, 'image.png')
                
                success, result = safe_file_save(mock_file)
                assert success is True
                assert 'image.png' in result
                assert 'test123' in result

    def test_safe_file_save_validation_failure(self):
        """Test safe file save with validation failure."""
        mock_file = MagicMock()
        
        with patch('MyFlaskapp.security_utils.validate_file_upload') as mock_validate:
            mock_validate.return_value = (False, "Invalid file", None)
            
            success, result = safe_file_save(mock_file)
            assert success is False
            assert result == "Invalid file"

    def test_validate_game_file_path_no_path(self):
        """Test game file validation with no path."""
        result = validate_game_file_path(None)
        assert result[0] is False
        assert result[1] == "No file path provided"

    def test_validate_game_file_path_directory_traversal(self):
        """Test game file validation with directory traversal attempt."""
        malicious_paths = [
            '../../../etc/passwd',
            '..\\..\\windows\\system32',
            '/etc/passwd',
            'C:\\Windows\\System32'
        ]
        
        for path in malicious_paths:
            result = validate_game_file_path(path)
            assert result[0] is False
            assert "directory traversal" in result[1].lower()

    def test_validate_game_file_path_nonexistent(self):
        """Test game file validation with nonexistent file."""
        result = validate_game_file_path('nonexistent_file.py')
        assert result[0] is False
        assert "not found" in result[1].lower()

    def test_validate_game_file_path_non_python(self):
        """Test game file validation with non-Python file."""
        # Create a temporary file to test with
        with tempfile.NamedTemporaryFile(suffix='.txt', delete=False) as temp_file:
            temp_file.write(b'This is not a Python file')
            temp_file_path = temp_file.name
        
        try:
            # Extract just the filename for testing
            filename = os.path.basename(temp_file_path)
            result = validate_game_file_path(filename, os.path.dirname(temp_file_path))
            assert result[0] is False
            assert "Python game files" in result[1]
        finally:
            os.unlink(temp_file_path)

    def test_validate_game_file_path_malicious_content(self):
        """Test game file validation with malicious content."""
        # Create a temporary Python file with malicious content
        malicious_code = """
import os
os.system('rm -rf /')
eval('malicious_code')
exec('dangerous_command')
"""
        
        with tempfile.NamedTemporaryFile(suffix='.py', delete=False, mode='w') as temp_file:
            temp_file.write(malicious_code)
            temp_file_path = temp_file.name
        
        try:
            filename = os.path.basename(temp_file_path)
            result = validate_game_file_path(filename, os.path.dirname(temp_file_path))
            assert result[0] is False
            assert "dangerous code" in result[1].lower()
        finally:
            os.unlink(temp_file_path)

    def test_sanitize_score_valid_numbers(self):
        """Test score sanitization with valid numbers."""
        valid_scores = [0, 100, 500, 999999, "100", "500"]
        for score in valid_scores:
            result = sanitize_score(score)
            assert isinstance(result, int)
            assert result >= 0
            assert result <= 999999

    def test_sanitize_score_negative_numbers(self):
        """Test score sanitization with negative numbers."""
        negative_scores = [-1, -100, "-50", -999999]
        for score in negative_scores:
            result = sanitize_score(score)
            assert result == 0

    def test_sanitize_score_too_large(self):
        """Test score sanitization with too large numbers."""
        large_scores = [1000000, 9999999, "2000000"]
        for score in large_scores:
            result = sanitize_score(score)
            assert result == 0

    def test_sanitize_score_invalid_types(self):
        """Test score sanitization with invalid types."""
        invalid_scores = ["abc", None, [], {}, "12.5", "100abc"]
        for score in invalid_scores:
            result = sanitize_score(score)
            assert result == 0

    def test_sanitize_score_edge_cases(self):
        """Test score sanitization with edge cases."""
        # Test boundary values
        assert sanitize_score(0) == 0
        assert sanitize_score(999999) == 999999
        assert sanitize_score(1000000) == 0  # Just over limit
        
        # Test string representations
        assert sanitize_score("0") == 0
        assert sanitize_score("999999") == 999999
        assert sanitize_score("1000000") == 0

    @patch('MyFlaskapp.security_utils.magic')
    def test_validate_file_upload_with_magic_library(self, mock_magic):
        """Test file upload validation with python-magic library."""
        mock_file = MagicMock()
        mock_file.filename = 'image.png'
        mock_file.content_length = 1024
        mock_file.read.return_value = b'fake image data'
        mock_file.seek.return_value = None
        mock_magic.from_buffer.return_value = 'image/png'
        
        # Enable magic library
        import MyFlaskapp.security_utils
        original_magic = MyFlaskapp.security_utils.magic
        MyFlaskapp.security_utils.magic = mock_magic
        
        try:
            result = validate_file_upload(mock_file)
            assert result[0] is True
            mock_magic.from_buffer.assert_called_once()
        finally:
            MyFlaskapp.security_utils.magic = original_magic

    @patch('MyFlaskapp.security_utils.magic')
    def test_validate_file_upload_magic_mismatch(self, mock_magic):
        """Test file upload validation when magic library detects wrong type."""
        mock_file = MagicMock()
        mock_file.filename = 'image.png'
        mock_file.content_length = 1024
        mock_file.read.return_value = b'fake image data'
        mock_file.seek.return_value = None
        mock_magic.from_buffer.return_value = 'application/pdf'  # Wrong type
        
        # Enable magic library
        import MyFlaskapp.security_utils
        original_magic = MyFlaskapp.security_utils.magic
        MyFlaskapp.security_utils.magic = mock_magic
        
        try:
            result = validate_file_upload(mock_file)
            assert result[0] is False
            assert "doesn't match allowed type" in result[1]
        finally:
            MyFlaskapp.security_utils.magic = original_magic
