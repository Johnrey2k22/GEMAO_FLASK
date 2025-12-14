"""
Security utilities for file validation and other security functions
"""
import os
try:
    import magic
except ImportError:
    magic = None
from werkzeug.utils import secure_filename
from flask import current_app

# Allowed file extensions for profile images
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}

# Maximum file size (5MB)
MAX_FILE_SIZE = 5 * 1024 * 1024

# Allowed MIME types
ALLOWED_MIME_TYPES = {
    'image/png',
    'image/jpeg',
    'image/jpg', 
    'image/gif',
    'image/webp'
}

def allowed_file(filename):
    """Check if file extension is allowed"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def validate_file_upload(file):
    """
    Comprehensive file validation for uploads
    Returns (is_valid, error_message, safe_filename)
    """
    if not file or not file.filename:
        return False, "No file selected", None
    
    # Check file size
    if file.content_length > MAX_FILE_SIZE:
        return False, "File too large. Maximum size is 5MB", None
    
    # Check extension
    if not allowed_file(file.filename):
        return False, "Invalid file type. Only PNG, JPG, JPEG, GIF, and WebP are allowed", None
    
    # Get secure filename
    filename = secure_filename(file.filename)
    if not filename:
        return False, "Invalid filename", None
    
    # Read file content for MIME type validation
    try:
        file_content = file.read()
        file.seek(0)  # Reset file pointer
        
        # Use python-magic to detect real file type if available
        if magic:
            mime_type = magic.from_buffer(file_content, mime=True)
            
            if mime_type not in ALLOWED_MIME_TYPES:
                return False, f"File content doesn't match allowed type. Detected: {mime_type}", None
        else:
            # Fallback: just check file extension if magic library not available
            pass
            
    except Exception as e:
        return False, "Error validating file content", None
    
    return True, None, filename

def safe_file_save(file, upload_folder='static/images/profiles'):
    """
    Safely save file with validation
    Returns (success, filepath_or_error_message)
    """
    # Validate file first
    is_valid, error_msg, safe_name = validate_file_upload(file)
    if not is_valid:
        return False, error_msg
    
    # Create upload directory if it doesn't exist
    upload_path = os.path.join(current_app.root_path, upload_folder)
    os.makedirs(upload_path, exist_ok=True)
    
    # Generate unique filename to prevent overwrites
    import uuid
    unique_filename = f"{uuid.uuid4().hex}_{safe_name}"
    filepath = os.path.join(upload_path, unique_filename)
    
    try:
        file.save(filepath)
        return True, os.path.join(upload_folder, unique_filename)
    except Exception as e:
        return False, f"Error saving file: {str(e)}"

def validate_game_file_path(file_path, base_path=None):
    """
    Enhanced validation that game file path is within allowed directory
    Prevents directory traversal attacks and validates file content
    """
    if not file_path:
        return False, "No file path provided"
    
    if base_path is None:
        base_path = os.path.join(os.path.dirname(__file__), 'games')
    
    # Normalize paths
    base_path = os.path.abspath(base_path)
    full_path = os.path.abspath(os.path.join(base_path, file_path))
    
    # Check if the full path is within the base path
    if not full_path.startswith(base_path):
        return False, "Invalid file path - directory traversal detected"
    
    # Check if file exists
    if not os.path.exists(full_path):
        return False, "Game file not found"
    
    # Check if it's a Python file
    if not file_path.endswith('.py'):
        return False, "Only Python game files are allowed"
    
    # Check file permissions
    if not os.access(full_path, os.R_OK):
        return False, "Game file is not readable"
    
    # Additional security checks for launcher integration
    try:
        import re
        
        # Check file size (prevent extremely large files)
        file_size = os.path.getsize(full_path)
        max_size = 10 * 1024 * 1024  # 10MB
        if file_size > max_size:
            return False, f"File too large: {file_size} bytes (max: {max_size})"
        
        # Basic content validation
        with open(full_path, 'r', encoding='utf-8') as f:
            content = f.read(2048)  # Read first 2KB
            
            # Check for obviously malicious content patterns
            malicious_patterns = [
                r'eval\s*\(',
                r'exec\s*\(',
                r'os\.system\s*\(',
                r'subprocess\.call\s*\(',
                r'__import__\s*\(',
                r'input\s*\(',
                r'raw_input\s*\(',
                r'open\s*\(',
            ]
            
            for pattern in malicious_patterns:
                if re.search(pattern, content, re.IGNORECASE):
                    return False, f"Potentially dangerous code detected: {pattern}"
                    
    except UnicodeDecodeError:
        return False, "File must be UTF-8 encoded"
    except Exception as e:
        return False, f"Error validating file: {str(e)}"
    
    return True, full_path

def sanitize_score(score):
    """
    Sanitize and validate score input.
    
    Args:
        score: Score value to validate
        
    Returns:
        int: Validated score (0 if invalid)
    """
    try:
        score = int(score)
        if score < 0:
            return 0
        if score > 999999:  # Reasonable upper limit
            return 0
        return score
    except (ValueError, TypeError):
        return 0
