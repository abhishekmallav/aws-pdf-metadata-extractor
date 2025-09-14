import boto3
import os
from dotenv import load_dotenv
from botocore.exceptions import ClientError
import logging

logging.basicConfig(level=logging.INFO)

env_path = os.path.join(os.path.dirname(__file__), '../.env')
load_dotenv(dotenv_path=env_path)

BUCKET_NAME = os.getenv("AWS_S3_BUCKET_NAME")
REGION = os.getenv("AWS_REGION")
ACCESS_KEY = os.getenv("AWS_ACCESS_KEY")
SECRET_KEY = os.getenv("AWS_SECRET_KEY")

# Debug: Check if credentials are loaded (don't print actual values for security)
print(f"Bucket: {BUCKET_NAME}")
print(f"Region: {REGION}")
print(f"Access Key loaded: {bool(ACCESS_KEY)}")
print(f"Secret Key loaded: {bool(SECRET_KEY)}")


def upload_file(file_name, bucket, object_name=None):
    if object_name is None:
        object_name = os.path.basename(file_name)

    s3_client = boto3.client(
        's3',
        region_name=REGION,
        aws_access_key_id=ACCESS_KEY,
        aws_secret_access_key=SECRET_KEY
    )

    try:
        # First, check if file exists
        if not os.path.exists(file_name):
            print(f"File does not exist: {file_name}")
            return False

        response = s3_client.upload_file(file_name, bucket, object_name)
        return True
    except ClientError as e:
        error_code = e.response['Error']['Code']
        print(f"AWS Error ({error_code}): {e}")
        return False
    except Exception as e:
        print(f"Error Occurred: {e}")
        return False


PDF_FILE = os.path.join(os.path.dirname(__file__), "Files",
                        "Prompt Engineering by Google.pdf")
S3_NAME = os.path.basename(PDF_FILE)
print(f"File to upload: {PDF_FILE}")
print(f"S3 object name: {S3_NAME}")

if upload_file(PDF_FILE, BUCKET_NAME, S3_NAME):
    logging.info(
        f"File {PDF_FILE} uploaded successfully to bucket {BUCKET_NAME} as {S3_NAME}")
else:
    logging.error("File upload failed")
