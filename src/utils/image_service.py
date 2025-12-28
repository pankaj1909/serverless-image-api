import boto3
from typing import Optional
from botocore.exceptions import ClientError
from .logger import get_logger
import os

logger = get_logger(__name__)

class ImageService:
    def __init__(self, localstack_endpoint: Optional[str] = None):
        # Use different endpoints for Lambda vs local testing
        if os.environ.get('AWS_LAMBDA_FUNCTION_NAME'):
            # Running inside Lambda - use LocalStack internal endpoint
            self.endpoint = 'http://host.docker.internal:4566'
        else:
            # Running locally - use localhost
            self.endpoint = localstack_endpoint or "http://localhost:4566"
            
        self.s3 = boto3.client('s3', endpoint_url=self.endpoint)
        self.dynamodb = boto3.resource('dynamodb', endpoint_url=self.endpoint)
        self.bucket_name = 'instagram-images'
        self.table_name = 'image-metadata'
        
    def setup_resources(self) -> None:
        """Setup S3 bucket and DynamoDB table"""
        try:
            self.s3.create_bucket(Bucket=self.bucket_name)
            logger.info(f"Created S3 bucket: {self.bucket_name}")
        except ClientError as e:
            if e.response['Error']['Code'] == 'BucketAlreadyOwnedByYou':
                logger.info(f"S3 bucket {self.bucket_name} already exists")
            else:
                logger.error(f"Failed to create S3 bucket: {e}")
                raise
            
        try:
            table = self.dynamodb.create_table(
                TableName=self.table_name,
                KeySchema=[{'AttributeName': 'image_id', 'KeyType': 'HASH'}],
                AttributeDefinitions=[
                    {'AttributeName': 'image_id', 'AttributeType': 'S'},
                    {'AttributeName': 'user_id', 'AttributeType': 'S'}
                ],
                GlobalSecondaryIndexes=[{
                    'IndexName': 'user-index',
                    'KeySchema': [{'AttributeName': 'user_id', 'KeyType': 'HASH'}],
                    'Projection': {'ProjectionType': 'ALL'},
                    'ProvisionedThroughput': {'ReadCapacityUnits': 5, 'WriteCapacityUnits': 5}
                }],
                BillingMode='PROVISIONED',
                ProvisionedThroughput={'ReadCapacityUnits': 5, 'WriteCapacityUnits': 5}
            )
            table.wait_until_exists()
            logger.info(f"Created DynamoDB table: {self.table_name}")
        except ClientError as e:
            if e.response['Error']['Code'] == 'ResourceInUseException':
                logger.info(f"DynamoDB table {self.table_name} already exists")
            else:
                logger.error(f"Failed to create DynamoDB table: {e}")
                raise