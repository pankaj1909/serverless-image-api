#!/usr/bin/env python3

from typing import Dict, Any
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from src.utils.image_service import ImageService
from src.utils.logger import get_logger

logger = get_logger(__name__)

def setup_localstack() -> None:
    """Setup LocalStack resources for development"""
    logger.info("Setting up LocalStack resources...")
    
    service = ImageService()
    service.setup_resources()
    
    logger.info("S3 bucket created: instagram-images")
    logger.info("DynamoDB table created: image-metadata")
    logger.info("LocalStack setup complete!")

if __name__ == "__main__":
    setup_localstack()