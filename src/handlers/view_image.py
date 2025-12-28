import json
import base64
from typing import Dict, Any
from ..utils.image_service import ImageService
from ..utils.response import create_response
from ..utils.logger import get_logger

logger = get_logger(__name__)

def lambda_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    service = ImageService()
    
    try:
        image_id = event['pathParameters']['image_id']
        logger.info(f"Retrieving image {image_id}")
        
        # Get metadata from DynamoDB
        table = service.dynamodb.Table(service.table_name)
        response = table.get_item(Key={'image_id': image_id})
        
        if 'Item' not in response:
            logger.warning(f"Image {image_id} not found")
            return create_response(404, {'error': 'Image not found'})
        
        metadata = response['Item']
        s3_key = metadata['s3_key']
        
        # Get image from S3
        s3_response = service.s3.get_object(Bucket=service.bucket_name, Key=s3_key)
        image_data = s3_response['Body'].read()
        
        logger.info(f"Successfully retrieved image {image_id}")
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': metadata['content_type'],
                'Content-Disposition': f'inline; filename="{image_id}"'
            },
            'body': base64.b64encode(image_data).decode('utf-8'),
            'isBase64Encoded': True
        }
        
    except Exception as e:
        logger.error(f"Error retrieving image {image_id}: {str(e)}")
        return create_response(500, {'error': str(e)})