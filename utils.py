import os
import mimetypes
from typing import Optional, List

def validate_file_path(file_path: str) -> bool:
    """Validate if file path exists and is accessible"""
    return os.path.exists(file_path) and os.path.isfile(file_path)

def get_file_size_mb(file_path: str) -> float:
    """Get file size in MB"""
    if not validate_file_path(file_path):
        return 0.0
    return os.path.getsize(file_path) / (1024 * 1024)

def get_file_mime_type(file_path: str) -> Optional[str]:
    """Get MIME type of a file"""
    mime_type, _ = mimetypes.guess_type(file_path)
    return mime_type

def format_file_size(size_bytes: int) -> str:
    """Format file size in human readable format"""
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if size_bytes < 1024.0:
            return f"{size_bytes:.2f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.2f} PB"

def validate_s3_key(s3_key: str) -> bool:
    """Validate S3 key format"""
    # S3 keys cannot be empty or contain certain characters
    if not s3_key or s3_key.strip() == '':
        return False
    
    # Check for invalid characters
    invalid_chars = ['\\', '{', '}', '^', '%', '`', '[', ']', '"', '>', '<', '~', '#', '|']
    for char in invalid_chars:
        if char in s3_key:
            return False
    
    return True

def is_allowed_file_type(file_path: str, allowed_extensions: List[str] = None) -> bool:
    """Check if file type is allowed"""
    if allowed_extensions is None:
        # Default allowed extensions
        allowed_extensions = ['.txt', '.pdf', '.doc', '.docx', '.jpg', '.jpeg', '.png', '.gif', '.csv', '.json', '.xml']
    
    _, ext = os.path.splitext(file_path.lower())
    return ext in [e.lower() for e in allowed_extensions]
