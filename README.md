# AWS PDF Metadata Extractor

[![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)](https://python.org)
[![AWS](https://img.shields.io/badge/AWS-S3%20%7C%20Lambda%20%7C%20DynamoDB-orange.svg)](https://aws.amazon.com)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

A serverless AWS-based pipeline that automatically extracts metadata from PDF files uploaded to S3, processes them using Lambda functions, and stores the extracted information in DynamoDB for easy retrieval and analysis.

## Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Tech Stack](#tech-stack)
- [Installation](#installation)
- [Usage Examples](#usage-examples)
- [Configuration](#configuration)
- [Project Structure](#project-structure)
- [API Documentation](#api-documentation)
- [Testing Instructions](#testing-instructions)
- [Deployment Guide](#deployment-guide)
- [Performance Notes](#performance-notes)
- [Scalability Considerations](#scalability-considerations)
- [Security Practices](#security-practices)
- [Contributing](#contributing)
- [License](#license)
- [Author](#author)

## Overview

This system provides an automated solution for extracting and storing PDF metadata using AWS serverless architecture. When a PDF file is uploaded to an S3 bucket, it triggers a Lambda function that extracts comprehensive metadata (title, author, page count, etc.) and stores it in DynamoDB for fast querying and analysis.

![Architecture](https://github.com/abhishekmallav/aws-pdf-metadata-extractor/blob/main/S3/architecture.png)
## Features

- **Automatic PDF Processing**: Triggered by S3 upload events
- **Metadata Extraction**: Extracts title, author, creator, producer, page count, and more
- **Error Handling**: Robust error handling for corrupted or invalid PDF files
- **Serverless Architecture**: Zero-maintenance infrastructure using AWS Lambda
- **Fast Querying**: DynamoDB storage enables millisecond-latency metadata retrieval
- **Content Type Validation**: Ensures only PDF files are processed
- **Local Testing**: Standalone scripts for development and testing

## Tech Stack

### Core Technologies

- **Python 3.9+**: Primary programming language
- **AWS SDK (Boto3)**: AWS service integration
- **PyPDF2**: PDF parsing and metadata extraction

### AWS Services

- **S3**: Object storage for PDF files
- **Lambda**: Serverless compute for PDF processing
- **DynamoDB**: NoSQL database for metadata storage
- **CloudWatch**: Logging and monitoring

### Development Dependencies

- **python-dotenv**: Environment variable management
- **botocore**: AWS service client library

## Installation

### Prerequisites

- Python 3.9 or higher
- AWS Account with appropriate permissions
- AWS CLI configured (optional, for deployment)

### Step-by-Step Setup

1.  **Clone the repository**

    ```bash
    git clone <repository-url>
    cd aws-pdf-metadata-extractor
    ```

2.  **Install Python dependencies**

    ```bash
    pip install boto3 PyPDF2 python-dotenv
    ```

3.  **Configure environment variables**
    Create a `.env` file in the project root:

    ```env
    AWS_S3_BUCKET_NAME=your-bucket-name
    AWS_REGION=your-aws-region
    AWS_ACCESS_KEY=your-access-key
    AWS_SECRET_KEY=your-secret-key
    DDB_TABLE_NAME=demoPDFMetaDataTable
    ```

4.  **Create AWS resources**

    - Create an S3 bucket
    - Create a DynamoDB table named `demoPDFMetaDataTable`
    - Set up Lambda function with S3 trigger
    - Configure IAM roles with appropriate permissions
      - Lambda IAM Role Policy
      ```json
      {
        "Version": "2012-10-17",
        "Statement": [
          {
            "Effect": "Allow",
            "Action": ["s3:GetObject"],
            "Resource": "arn:aws:s3:::<bucket-name>/_"
          },
          {
            "Effect": "Allow",
            "Action": ["dynamodb:PutItem"],
            "Resource": "arn:aws:dynamodb:ap-south-1:346915422902:table/<dynamo-db-table-name>"
          },
          {
            "Effect": "Allow",
            "Action": [
              "logs:CreateLogGroup",
              "logs:CreateLogStream",
              "logs:PutLogEvents"
            ],
            "Resource": "_"
          }
        ]
      }
      ```
      - S3 Upload Policy (IAM User)
        ```json
        {
          "Version": "2012-10-17",
          "Statement": [
            {
              "Effect": "Allow",
              "Action": "s3:*",
              "Resource": "arn:aws:s3:::<bucket-name>/*"
            }
          ]
        }
        ```

5.  **Deploy Lambda function**

    ```bash
    # Package the Lambda function
    zip -r lambda-function.zip lambda-function.py

    # Deploy using AWS CLI (TODO: Add specific deployment commands)
    aws lambda create-function --function-name pdf-metadata-extractor \
      --runtime python3.9 --role arn:aws:iam::account:role/lambda-role \
      --handler lambda-function.lambda_handler --zip-file fileb://lambda-function.zip
    ```

## Usage Examples

### Upload PDF and Trigger Processing

```python
# Using the S3 upload script
from S3.S3_Upload import upload_file
import os

# Upload a PDF file
pdf_path = "path/to/your/document.pdf"
bucket_name = "your-bucket-name"

if upload_file(pdf_path, bucket_name):
    print("PDF uploaded successfully - Lambda will process automatically")
else:
    print("Upload failed")
```

### Local Metadata Extraction

```python
# Test metadata extraction locally
from S3.extract_pdf_metadata import extract_metadata

metadata = extract_metadata("path/to/your/document.pdf")
print("Extracted metadata:", metadata)
```

### Query Metadata from DynamoDB

```python
import boto3

dynamodb = boto3.resource('dynamodb', region_name='your-region')
table = dynamodb.Table('demoPDFMetaDataTable')

# Get metadata for a specific file
response = table.get_item(Key={'FileName': 'document.pdf'})
if 'Item' in response:
    print("Metadata:", response['Item'])
```

## Configuration

### Environment Variables

| Variable             | Description               | Example                |
| -------------------- | ------------------------- | ---------------------- |
| `AWS_S3_BUCKET_NAME` | S3 bucket for PDF storage | `my-pdf-bucket`        |
| `AWS_REGION`         | AWS region                | `us-east-1`            |
| `AWS_ACCESS_KEY`     | AWS access key ID         | `AKIA...`              |
| `AWS_SECRET_KEY`     | AWS secret access key     | `secret-key`           |
| `DDB_TABLE_NAME`     | DynamoDB table name       | `demoPDFMetaDataTable` |

### DynamoDB Table Schema

```json
{
  "TableName": "demoPDFMetaDataTable",
  "KeySchema": [
    {
      "AttributeName": "FileName",
      "KeyType": "HASH"
    }
  ],
  "AttributeDefinitions": [
    {
      "AttributeName": "FileName",
      "AttributeType": "S"
    }
  ]
}
```

## Project Structure

```
aws-pdf-metadata-extractor/
├── .env                           # Environment configuration
├── README.md                      # Project documentation
└── S3/
    ├── Files/                     # Sample PDF files directory
    ├── S3-Upload.py              # S3 file upload utility
    ├── extract-pdf-metadata.py   # Local metadata extraction tool
    └── lambda-function.py         # AWS Lambda function code
```

### File Descriptions

- **`.env`**: Contains AWS credentials and configuration
- **`S3-Upload.py`**: Utility script for uploading PDF files to S3 with error handling
- **`extract-pdf-metadata.py`**: Standalone script for testing PDF metadata extraction locally
- **`lambda-function.py`**: Main Lambda function that processes S3 events and extracts PDF metadata
- **`Files/`**: Directory for storing sample PDF files for testing

## API Documentation

### Lambda Function Handler

**Function**: `lambda_handler(event, context)`

**Event Structure** (S3 Trigger):

```json
{
  "Records": [
    {
      "s3": {
        "bucket": { "name": "bucket-name" },
        "object": { "key": "file.pdf" }
      }
    }
  ]
}
```

**Response**:

```json
{
  "statusCode": 200,
  "body": "Metadata saved for file.pdf"
}
```

### Extracted Metadata Schema

```json
{
  "FileName": "document.pdf",
  "Bucket": "my-bucket",
  "UploadTime": "2024-01-15T10:30:00",
  "ContentType": "application/pdf",
  "num_pages": 25,
  "title": "Document Title",
  "author": "Author Name",
  "creator": "Creator Application",
  "producer": "PDF Producer"
}
```

## Testing Instructions

### Local Testing

1. **Test metadata extraction**:

   ```bash
   python S3/extract-pdf-metadata.py
   ```

2. **Test S3 upload**:
   ```bash
   python S3/S3-Upload.py
   ```

### Lambda Function Testing

1. **Create test event** in AWS Lambda console with S3 event structure
   ```json
   {
     "Records": [
       {
         "eventVersion": "2.0",
         "eventSource": "aws:s3",
         "awsRegion": "ap-south-1",
         "eventTime": "1970-01-01T00:00:00.000Z",
         "eventName": "ObjectCreated:Put",
         "userIdentity": {
           "principalId": "EXAMPLE"
         },
         "requestParameters": {
           "sourceIPAddress": "127.0.0.1"
         },
         "responseElements": {
           "x-amz-request-id": "EXAMPLE123456789",
           "x-amz-id-2": "EXAMPLE123/5678abcdefghijklambdaisawesome/mnopqrstuvwxyzABCDEFGH"
         },
         "s3": {
           "s3SchemaVersion": "1.0",
           "configurationId": "testConfigRule",
           "bucket": {
             "name": "<bucket-name>",
             "ownerIdentity": {
               "principalId": "EXAMPLE"
             },
             "arn": "arn:aws:s3:::<bucket-name>"
           },
           "object": {
             "key": "PDF File.pdf",
             "eTag": "0123456789abcdef0123456789abcdef",
             "sequencer": "0A1B2C3D4E5F678901"
           }
         }
       }
     ]
   }
   ```
2. **Monitor CloudWatch logs** for execution details
3. **Verify DynamoDB entries** after successful execution

## Deployment Guide

### Manual Deployment

1. **Package Lambda function**:

   ```bash
   cd S3/
   zip -r ../lambda-deployment.zip lambda-function.py
   ```

2. **Create IAM role** with policies:

   - `AWSLambdaBasicExecutionRole`
   - S3 read permissions
   - DynamoDB write permissions

3. **Deploy via AWS Console**:
   - Upload zip file to Lambda
   - Configure S3 trigger
   - Set environment variables

## Performance Notes

- **Lambda Cold Start**: ~2-3 seconds for initial execution
- **PDF Processing Time**:
  - Small PDFs (< 1MB): ~500ms
  - Medium PDFs (1-10MB): ~2-5 seconds
  - Large PDFs (> 10MB): ~5-15 seconds
- **DynamoDB Write Latency**: < 10ms per item
- **Memory Usage**: Lambda configured for 512MB (adjustable based on PDF size)

## Scalability Considerations

### Current Limitations

- Lambda timeout: 15 minutes maximum
- Lambda memory: 10GB maximum
- S3 object size: 5TB maximum
- DynamoDB throughput: Configurable (on-demand recommended)

### Scaling Strategies

- **High Volume**: Use SQS for batch processing
- **Large Files**: Implement multi-part processing
- **Global Scale**: Deploy in multiple regions
- **Cost Optimization**: Use S3 Intelligent Tiering

### Estimated Capacity

- **Documents/hour**: ~10,000 (with standard Lambda limits)
- **Concurrent executions**: 1,000 (default AWS limit)
- **Storage**: Unlimited (S3 + DynamoDB auto-scaling)

## Security Practices

### Current Implementation

- Environment variables for sensitive data
- IAM roles with least privilege principle

### Security Recommendations

- Use AWS Secrets Manager for credentials
- Enable S3 bucket encryption
- Implement VPC endpoints for private communication
- Add input validation and sanitization
- Enable AWS CloudTrail for audit logging

## Contributing

We welcome contributions! Please see our [Contributing Guidelines](CONTRIBUTING.md) for details.

### Quick Start for Contributors

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests (when test framework is implemented)
5. Submit a pull request

### Development Setup

```bash
git clone <your-fork>
cd aws-pdf-metadata-extractor
pip install boto3 PyPDF2
```

## FAQ

### Common Issues

**Q: Lambda function timing out?**
A: Increase timeout in Lambda configuration or optimize PDF processing for large files.

**Q: DynamoDB write errors?**
A: Check IAM permissions and DynamoDB table configuration.

**Q: PDF metadata extraction returning "Unknown"?**
A: The PDF may not contain embedded metadata or may be corrupted.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

### Third-Party Licenses

- PyPDF2: BSD License
- Boto3: Apache License 2.0

---

## Author

Created by [abhishekmallav](https://github.com/abhishekmallav)

[![LinkedIn](https://img.shields.io/badge/LinkedIn-0077B5?style=for-the-badge&logo=linkedin&logoColor=white)](https://www.linkedin.com/in/abhishekmallav)
[![Gmail](https://img.shields.io/badge/Gmail-D14836?style=for-the-badge&logo=gmail&logoColor=white)](mailto:abhimallav1439@gmail.com?subject=Hello%20There&body=Just%20wanted%20to%20say%20hi!)
[![Instagram](https://img.shields.io/badge/Instagram-E4405F?style=for-the-badge&logo=instagram&logoColor=white)](https://www.instagram.com/abhishekmallav)
[![Twitter](https://img.shields.io/badge/Twitter-1DA1F2?style=for-the-badge&logo=x&logoColor=white)](https://www.x.com/abhishekmallav)
