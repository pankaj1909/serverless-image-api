import json
from typing import Dict, Any
from ..utils.image_service import ImageService
from ..utils.response import create_response
from ..utils.logger import get_logger

logger = get_logger(__name__)

def lambda_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    service = ImageService()
    
    try:
        image_id = event['pathParameters']['image_id']
        logger.info(f"Deleting image {image_id}")
        
        # Get metadata from DynamoDB
        table = service.dynamodb.Table(service.table_name)
        response = table.get_item(Key={'image_id': image_id})
        
        if 'Item' not in response:
            logger.warning(f"Image {image_id} not found for deletion")
            return create_response(404, {'error': 'Image not found'})
        
        metadata = response['Item']
        s3_key = metadata['s3_key']
        
        # Delete from S3
        service.s3.delete_object(Bucket=service.bucket_name, Key=s3_key)
        
        # Delete from DynamoDB
        table.delete_item(Key={'image_id': image_id})
        
        logger.info(f"Successfully deleted image {image_id}")
        return create_response(200, {'message': 'Image deleted successfully'})
        
    except Exception as e:
        logger.error(f"Error deleting image {image_id}: {str(e)}")
        return create_response(500, {'error': str(e)})