import boto3
from botocore.exceptions import ClientError, NoCredentialsError
import config
import os

class S3Client:
    def __init__(self):
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
            print(f"✅ Connected to S3 bucket: {self.bucket_name}")
        except NoCredentialsError:
            raise Exception("AWS credentials not found")
        except ClientError as e:
            error_code = e.response['Error']['Code']
            if error_code == '404':
                raise Exception(f"Bucket '{self.bucket_name}' not found")
            else:
                raise Exception(f"Error connecting to S3: {e}")
    
    def list_objects(self, prefix=''):
        """List objects in the S3 bucket"""
        try:
            response = self.s3.list_objects_v2(
                Bucket=self.bucket_name,
                Prefix=prefix
            )
            return response.get('Contents', [])
        except ClientError as e:
            print(f"Error listing objects: {e}")
            return []
    
    def upload_file(self, local_file_path, s3_key=None):
        """Upload a file to S3"""
        if not os.path.exists(local_file_path):
            raise FileNotFoundError(f"Local file not found: {local_file_path}")
        
        if s3_key is None:
            s3_key = os.path.basename(local_file_path)
        
        try:
            self.s3.upload_file(local_file_path, self.bucket_name, s3_key)
            print(f"✅ Uploaded {local_file_path} to s3://{self.bucket_name}/{s3_key}")
            return True
        except ClientError as e:
            print(f"❌ Error uploading file: {e}")
            return False
