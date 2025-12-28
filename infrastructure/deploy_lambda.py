#!/usr/bin/env python3

import boto3
import zipfile
import os
import sys
from pathlib import Path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from src.utils.logger import get_logger

logger = get_logger(__name__)

def create_deployment_package():
    """Create a deployment package for Lambda functions"""
    logger.info("Creating deployment package...")
    
    # Create a zip file with the source code
    with zipfile.ZipFile('lambda_package.zip', 'w', zipfile.ZIP_DEFLATED) as zipf:
        # Add all Python files from src directory
        for root, dirs, files in os.walk('src'):
            for file in files:
                if file.endswith('.py'):
                    file_path = os.path.join(root, file)
                    arcname = file_path
                    zipf.write(file_path, arcname)
    
    logger.info("Deployment package created: lambda_package.zip")
    return 'lambda_package.zip'

def deploy_lambda_functions():
    """Deploy Lambda functions to LocalStack"""
    lambda_client = boto3.client('lambda', endpoint_url='http://localhost:4566')
    
    # Create deployment package
    zip_file = create_deployment_package()
    
    # Read the zip file
    with open(zip_file, 'rb') as f:
        zip_content = f.read()
    
    functions = [
        {
            'name': 'upload-image',
            'handler': 'src.handlers.upload_image.lambda_handler',
            'description': 'Upload image to S3 and save metadata'
        },
        {
            'name': 'list-images', 
            'handler': 'src.handlers.list_images.lambda_handler',
            'description': 'List images with optional filters'
        },
        {
            'name': 'view-image',
            'handler': 'src.handlers.view_image.lambda_handler', 
            'description': 'View/download a specific image'
        },
        {
            'name': 'delete-image',
            'handler': 'src.handlers.delete_image.lambda_handler',
            'description': 'Delete an image and its metadata'
        }
    ]
    
    for func in functions:
        try:
            # Try to update if exists, otherwise create
            try:
                lambda_client.update_function_code(
                    FunctionName=func['name'],
                    ZipFile=zip_content
                )
                # Update timeout for existing functions
                lambda_client.update_function_configuration(
                    FunctionName=func['name'],
                    Timeout=30
                )
                logger.info(f"Updated Lambda function: {func['name']}")
            except lambda_client.exceptions.ResourceNotFoundException:
                # Create new function
                lambda_client.create_function(
                    FunctionName=func['name'],
                    Runtime='python3.9',
                    Role='arn:aws:iam::000000000000:role/lambda-role',
                    Handler=func['handler'],
                    Code={'ZipFile': zip_content},
                    Description=func['description'],
                    Timeout=30,
                    Environment={'Variables': {
                        'BUCKET_NAME': 'instagram-images',
                        'TABLE_NAME': 'image-metadata',
                        'LOCALSTACK_HOSTNAME': 'host.docker.internal'
                    }}
                )
                logger.info(f"Created Lambda function: {func['name']}")
                
        except Exception as e:
            logger.error(f"Error deploying {func['name']}: {e}")
    
    # Clean up
    os.remove(zip_file)
    logger.info("Lambda deployment complete!")

if __name__ == "__main__":
    deploy_lambda_functions()