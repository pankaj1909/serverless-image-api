#!/usr/bin/env python3

import boto3
import json
import base64
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from src.utils.logger import get_logger

logger = get_logger(__name__)

def test_lambda_functions():
    """Test Lambda functions deployed in LocalStack"""
    lambda_client = boto3.client('lambda', endpoint_url='http://localhost:4566')
    
    logger.info("Testing Lambda functions...")
    
    # Test 1: Upload Image
    logger.info("1. Testing upload-image...")
    upload_payload = {
        'body': json.dumps({
            'image': base64.b64encode(b'fake_image_data').decode(),
            'metadata': {
                'user_id': 'test_user_123',
                'title': 'Test Image',
                'description': 'A test image for LocalStack',
                'tags': ['test', 'localstack'],
                'content_type': 'image/jpeg'
            }
        })
    }
    
    try:
        response = lambda_client.invoke(
            FunctionName='upload-image',
            Payload=json.dumps(upload_payload)
        )
        result = json.loads(response['Payload'].read())
        logger.info(f"Upload response: {result}")
        
        # Extract image_id for further tests
        if result.get('statusCode') == 201:
            body = json.loads(result['body'])
            image_id = body.get('image_id')
            logger.info(f"Image ID: {image_id}")
        else:
            logger.error("Upload failed")
            return
            
    except Exception as e:
        logger.error(f"Upload error: {e}")
        return
    
    # Test 2: List Images
    logger.info("2. Testing list-images...")
    list_payload = {
        'queryStringParameters': {'user_id': 'test_user_123'}
    }
    
    try:
        response = lambda_client.invoke(
            FunctionName='list-images',
            Payload=json.dumps(list_payload)
        )
        result = json.loads(response['Payload'].read())
        logger.info(f"List response: {result}")
    except Exception as e:
        logger.error(f"List error: {e}")
    
    # Test 3: View Image
    logger.info("3. Testing view-image...")
    view_payload = {
        'pathParameters': {'image_id': image_id}
    }
    
    try:
        response = lambda_client.invoke(
            FunctionName='view-image',
            Payload=json.dumps(view_payload)
        )
        result = json.loads(response['Payload'].read())
        logger.info(f"View response status: {result.get('statusCode')}")
    except Exception as e:
        logger.error(f"View error: {e}")
    
    # Test 4: Delete Image
    logger.info("4. Testing delete-image...")
    delete_payload = {
        'pathParameters': {'image_id': image_id}
    }
    
    try:
        response = lambda_client.invoke(
            FunctionName='delete-image',
            Payload=json.dumps(delete_payload)
        )
        result = json.loads(response['Payload'].read())
        logger.info(f"Delete response: {result}")
    except Exception as e:
        logger.error(f"Delete error: {e}")
    
    logger.info("Lambda testing complete!")

if __name__ == "__main__":
    test_lambda_functions()