import unittest
from unittest.mock import Mock, patch, MagicMock
import os
import sys

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from s3_client import S3Client
from utils import validate_file_path, validate_s3_key, format_file_size

class TestS3Client(unittest.TestCase):
    
    @patch('s3_client.boto3.client')
    @patch('s3_client.config')
    def setUp(self, mock_config, mock_boto3_client):
        # Mock configuration
        mock_config.AWS_ACCESS_KEY_ID = 'test_access_key'
        mock_config.AWS_SECRET_ACCESS_KEY = 'test_secret_key'
        mock_config.AWS_DEFAULT_REGION = 'us-east-1'
        mock_config.S3_BUCKET_NAME = 'test-bucket'
        
        # Mock boto3 client
        self.mock_s3_client = MagicMock()
        mock_boto3_client.return_value = self.mock_s3_client
        
        # Create S3Client instance
        self.s3_client = S3Client()
    
    def test_list_objects_success(self):
        # Mock response
        mock_response = {
            'Contents': [
                {'Key': 'file1.txt', 'Size': 1024, 'LastModified': '2025-01-01'},
                {'Key': 'file2.txt', 'Size': 2048, 'LastModified': '2025-01-02'}
            ]
        }
        self.mock_s3_client.list_objects_v2.return_value = mock_response
        
        # Test
        result = self.s3_client.list_objects()
        
        # Assertions
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0]['Key'], 'file1.txt')
        self.mock_s3_client.list_objects_v2.assert_called_once()
    
    def test_list_objects_empty(self):
        # Mock empty response
        mock_response = {}
        self.mock_s3_client.list_objects_v2.return_value = mock_response
        
        # Test
        result = self.s3_client.list_objects()
        
        # Assertions
        self.assertEqual(len(result), 0)
    
    @patch('s3_client.os.path.exists')
    @patch('s3_client.os.path.basename')
    def test_upload_file_success(self, mock_basename, mock_exists):
        # Setup mocks
        mock_exists.return_value = True
        mock_basename.return_value = 'test.txt'
        
        # Test
        result = self.s3_client.upload_file('test.txt')
        
        # Assertions
        self.assertTrue(result)
        self.mock_s3_client.upload_file.assert_called_once()
    
    @patch('s3_client.os.path.exists')
    def test_upload_file_not_found(self, mock_exists):
        # Setup mock
        mock_exists.return_value = False
        
        # Test and assert exception
        with self.assertRaises(FileNotFoundError):
            self.s3_client.upload_file('nonexistent.txt')

class TestUtils(unittest.TestCase):
    
    def test_validate_s3_key_valid(self):
        self.assertTrue(validate_s3_key('documents/file.txt'))
        self.assertTrue(validate_s3_key('file.txt'))
        self.assertTrue(validate_s3_key('folder/subfolder/file.pdf'))
    
    def test_validate_s3_key_invalid(self):
        self.assertFalse(validate_s3_key(''))
        self.assertFalse(validate_s3_key('   '))
        self.assertFalse(validate_s3_key('file\\with\\backslash.txt'))
        self.assertFalse(validate_s3_key('file{with}braces.txt'))
    
    def test_format_file_size(self):
        self.assertEqual(format_file_size(1024), '1.00 KB')
        self.assertEqual(format_file_size(1048576), '1.00 MB')
        self.assertEqual(format_file_size(1073741824), '1.00 GB')

if __name__ == '__main__':
    unittest.main()
