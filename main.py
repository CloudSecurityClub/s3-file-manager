#!/usr/bin/env python3

from s3_client import S3Client
import sys
import os

def print_usage():
    print("""
AWS S3 File Manager

Usage:
    python main.py list [prefix]           - List files in bucket
    python main.py upload <file> [key]     - Upload file to bucket
    python main.py download <key> [file]   - Download file from bucket
    python main.py delete <key>            - Delete file from bucket

Examples:
    python main.py list
    python main.py list documents/
    python main.py upload ./data.txt
    python main.py upload ./data.txt documents/data.txt
    python main.py download documents/data.txt
    python main.py delete documents/data.txt
    """)

def main():
    if len(sys.argv) < 2:
        print_usage()
        return
    
    try:
        s3_client = S3Client()
    except Exception as e:
        print(f"❌ Failed to initialize S3 client: {e}")
        return
    
    command = sys.argv[1].lower()
    
    if command == 'list':
        prefix = sys.argv[2] if len(sys.argv) > 2 else ''
        objects = s3_client.list_objects(prefix)
        if objects:
            print(f"\nFiles in bucket (prefix: '{prefix}'):")
            for obj in objects:
                size_mb = obj['Size'] / (1024 * 1024)
                print(f"  📄 {obj['Key']} ({size_mb:.2f} MB) - {obj['LastModified']}")
        else:
            print(f"No files found with prefix '{prefix}'")
    
    elif command == 'upload':
        if len(sys.argv) < 3:
            print("❌ Please specify a file to upload")
            return
        
        local_file = sys.argv[2]
        s3_key = sys.argv[3] if len(sys.argv) > 3 else None
        s3_client.upload_file(local_file, s3_key)
    
    elif command == 'download':
        if len(sys.argv) < 3:
            print("❌ Please specify a file to download")
            return
        
        s3_key = sys.argv[2]
        local_file = sys.argv[3] if len(sys.argv) > 3 else None
        s3_client.download_file(s3_key, local_file)
    
    elif command == 'delete':
        if len(sys.argv) < 3:
            print("❌ Please specify a file to delete")
            return
        
        s3_key = sys.argv[2]
        s3_client.delete_file(s3_key)
    
    else:
        print(f"❌ Unknown command: {command}")
        print_usage()

if __name__ == "__main__":
    main()
