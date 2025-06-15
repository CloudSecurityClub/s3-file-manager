import boto3
from botocore.exceptions import ClientError, NoCredentialsError
import config
import os
from logger import setup_logger

class S3Client:
    def __init__(self):
        self.logger = setup_logger()
        
        try:
            self.s3 = boto3.client(
                's3',
                aws_access_key_id=config.AWS_ACCESS_KEY_ID,
                aws_secret_access_key=config.AWS_SECRET_ACCESS_KEY,
                region_name=config.AWS_DEFAULT_REGION
            )
            self.bucket_name = config.S3_BUCKET_NAME
            # Test connection
            self.s3.head_bucket(Bucket=self.bucket_name)
            self.logger.info(f"Connected to S3 bucket: {self.bucket_name}")
            print(f"✅ Connected to S3 bucket: {self.bucket_name}")
        except NoCredentialsError:
            self.logger.error("AWS credentials not found")
            raise Exception("AWS credentials not found")
        except ClientError as e:
            error_code = e.response['Error']['Code']
            if error_code == '404':
                self.logger.error(f"Bucket '{self.bucket_name}' not found")
                raise Exception(f"Bucket '{self.bucket_name}' not found")
            else:
                self.logger.error(f"Error connecting to S3: {e}")
                raise Exception(f"Error connecting to S3: {e}")
    
    def list_objects(self, prefix=''):
        """List objects in the S3 bucket"""
        try:
            self.logger.debug(f"Listing objects with prefix: '{prefix}'")
            response = self.s3.list_objects_v2(
                Bucket=self.bucket_name,
                Prefix=prefix
            )
            objects = response.get('Contents', [])
            self.logger.info(f"Found {len(objects)} objects")
            return objects
        except ClientError as e:
            self.logger.error(f"Error listing objects: {e}")
            print(f"Error listing objects: {e}")
            return []
    
    def upload_file(self, local_file_path, s3_key=None):
        """Upload a file to S3"""
        if not os.path.exists(local_file_path):
            self.logger.error(f"Local file not found: {local_file_path}")
            raise FileNotFoundError(f"Local file not found: {local_file_path}")
        
        if s3_key is None:
            s3_key = os.path.basename(local_file_path)
        
        try:
            file_size = os.path.getsize(local_file_path)
            self.logger.info(f"Uploading {local_file_path} ({file_size} bytes) to {s3_key}")
            
            self.s3.upload_file(local_file_path, self.bucket_name, s3_key)
            self.logger.info(f"Successfully uploaded {local_file_path} to s3://{self.bucket_name}/{s3_key}")
            print(f"✅ Uploaded {local_file_path} to s3://{self.bucket_name}/{s3_key}")
            return True
        except ClientError as e:
            self.logger.error(f"Error uploading file: {e}")
            print(f"❌ Error uploading file: {e}")
            return False
    
    def download_file(self, s3_key, local_file_path=None):
        """Download a file from S3"""
        if local_file_path is None:
            local_file_path = os.path.basename(s3_key)
        
        try:
            self.logger.info(f"Downloading s3://{self.bucket_name}/{s3_key} to {local_file_path}")
            self.s3.download_file(self.bucket_name, s3_key, local_file_path)
            
            file_size = os.path.getsize(local_file_path)
            self.logger.info(f"Successfully downloaded {s3_key} ({file_size} bytes)")
            print(f"✅ Downloaded s3://{self.bucket_name}/{s3_key} to {local_file_path}")
            return True
        except ClientError as e:
            error_code = e.response['Error']['Code']
            if error_code == '404':
                self.logger.error(f"File not found: s3://{self.bucket_name}/{s3_key}")
                print(f"❌ File not found: s3://{self.bucket_name}/{s3_key}")
            else:
                self.logger.error(f"Error downloading file: {e}")
                print(f"❌ Error downloading file: {e}")
            return False
    
    def delete_file(self, s3_key):
        """Delete a file from S3"""
        try:
            self.logger.info(f"Deleting s3://{self.bucket_name}/{s3_key}")
            self.s3.delete_object(Bucket=self.bucket_name, Key=s3_key)
            self.logger.info(f"Successfully deleted {s3_key}")
            print(f"✅ Deleted s3://{self.bucket_name}/{s3_key}")
            return True
        except ClientError as e:
            self.logger.error(f"Error deleting file: {e}")
            print(f"❌ Error deleting file: {e}")
            return False
