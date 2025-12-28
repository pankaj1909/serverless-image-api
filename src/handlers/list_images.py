import json
from typing import Dict, Any
from boto3.dynamodb.conditions import Key
from ..utils.image_service import ImageService
from ..utils.response import create_response
from ..utils.logger import get_logger

logger = get_logger(__name__)

def lambda_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    service = ImageService()
    
    try:
        params = event.get('queryStringParameters') or {}
        user_id = params.get('user_id')
        tag = params.get('tag')
        
        logger.info(f"Listing images with filters - user_id: {user_id}, tag: {tag}")
        
        table = service.dynamodb.Table(service.table_name)
        
        if user_id:
            # Filter by user_id using GSI
            response = table.query(
                IndexName='user-index',
                KeyConditionExpression=Key('user_id').eq(user_id)
            )
        else:
            # Scan all items
            response = table.scan()
        
        items = response['Items']
        
        # Additional filtering by tag
        if tag:
            items = [item for item in items if tag in item.get('tags', [])]
        
        # Remove S3 key from response for security
        for item in items:
            item.pop('s3_key', None)
            
        logger.info(f"Found {len(items)} images")
        return create_response(200, {'images': items, 'count': len(items)})
        
    except Exception as e:
        logger.error(f"Error listing images: {str(e)}")
        return create_response(500, {'error': str(e)})