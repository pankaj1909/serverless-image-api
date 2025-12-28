import json
import base64
import uuid
from datetime import datetime, timezone
from typing import Dict, Any
from ..utils.image_service import ImageService
from ..utils.response import create_response
from ..utils.logger import get_logger

logger = get_logger(__name__)

def lambda_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    service = ImageService()

    try:
        body = json.loads(event['body'])
        image_data_raw = body['image']
        metadata = body['metadata']

        # Handle data URL format (data:image/png;base64,xxxxx)
        if image_data_raw.startswith('data:'):
            # Extract base64 part after comma
            image_data_raw = image_data_raw.split(',', 1)[1]

        image_data = base64.b64decode(image_data_raw)

        image_id = str(uuid.uuid4())
        s3_key = f"images/{image_id}"

        logger.info(f"Uploading image {image_id} for user {metadata['user_id']}")

        # Upload to S3
        service.s3.put_object(
            Bucket=service.bucket_name,
            Key=s3_key,
            Body=image_data,
            ContentType=metadata.get('content_type', 'image/jpeg')
        )

        # Save metadata to DynamoDB
        table = service.dynamodb.Table(service.table_name)
        table.put_item(Item={
            'image_id': image_id,
            'user_id': metadata['user_id'],
            'title': metadata.get('title', ''),
            'description': metadata.get('description', ''),
            'tags': metadata.get('tags', []),
            'content_type': metadata.get('content_type', 'image/jpeg'),
            'created_at': datetime.now(timezone.utc).isoformat(),
            's3_key': s3_key
        })

        logger.info(f"Successfully uploaded image {image_id}")
        return create_response(201, {'image_id': image_id, 'message': 'Image uploaded successfully'})

    except Exception as e:
        logger.error(f"Error uploading image: {str(e)}")
        return create_response(500, {'error': str(e)})