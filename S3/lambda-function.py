import json
import urllib.parse
import boto3
import os
import datetime
import PyPDF2

print('Loading function...')

s3 = boto3.client('s3')
dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('demoPDFMetaDataTable')  # DynamoDB table name


def extract_metadata(pdf_path):
    metadata = {
        "num_pages": 0,
        "title": "Unknown",
        "author": "Unknown",
        "creator": "Unknown",
        "producer": "Unknown"
    }
    try:
        with open(pdf_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file, strict=False)

            if pdf_reader.is_encrypted:
                try:
                    pdf_reader.decrypt("")
                except Exception as e:
                    print(f"Skipping encrypted PDF: {pdf_path} ({e})")
                    return metadata

            metadata['num_pages'] = len(pdf_reader.pages)

            if pdf_reader.metadata:
                metadata['title'] = pdf_reader.metadata.get(
                    '/Title', 'Unknown')
                metadata['author'] = pdf_reader.metadata.get(
                    '/Author', 'Unknown')
                metadata['creator'] = pdf_reader.metadata.get(
                    '/Creator', 'Unknown')
                metadata['producer'] = pdf_reader.metadata.get(
                    '/Producer', 'Unknown')

    except Exception as e:
        print(f"Failed to extract metadata from {pdf_path}: {e}")

    return metadata


def lambda_handler(event, context):
    bucket = event['Records'][0]['s3']['bucket']['name']
    key = urllib.parse.unquote_plus(
        event['Records'][0]['s3']['object']['key'], encoding='utf-8')

    try:
        response = s3.get_object(Bucket=bucket, Key=key)
        print("CONTENT TYPE: " + response['ContentType'])

        if not key.lower().endswith(".pdf"):
            print(f"Skipping non-PDF file: {key}")
            return {
                'statusCode': 400,
                'body': json.dumps(f"Skipped {key}, not a PDF")
            }

        download_path = f"/tmp/{os.path.basename(key)}"
        s3.download_file(bucket, key, download_path)

        pdf_metadata = extract_metadata(download_path)

        item = {
            'FileName': key,
            'Bucket': bucket,
            'UploadTime': datetime.datetime.utcnow().isoformat(),
            'ContentType': response['ContentType']
        }
        item.update(pdf_metadata)

        print("Saving to DynamoDB:", item)
        table.put_item(Item=item)

        return {
            'statusCode': 200,
            'body': json.dumps(f"Metadata saved for {key}")
        }

    except Exception as e:
        print(e)
        print(
            f"Error processing object {key} from bucket {bucket}. Ensure the file exists and is in the same region.")
        raise e
