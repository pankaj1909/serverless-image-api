import pytest
import json
import base64
from moto import mock_s3, mock_dynamodb
from unittest.mock import patch, MagicMock
from src.handlers import upload_image, list_images, view_image, delete_image
from src.utils.image_service import ImageService

@pytest.fixture
def mock_aws():
    with mock_s3(), mock_dynamodb():
        service = ImageService()
        service.setup_resources()
        yield service

class TestUploadImage:
    def test_upload_success(self, mock_aws):
        event = {
            'body': json.dumps({
                'image': base64.b64encode(b'fake_image_data').decode(),
                'metadata': {
                    'user_id': 'user123',
                    'title': 'Test Image',
                    'description': 'Test Description',
                    'tags': ['test', 'demo'],
                    'content_type': 'image/jpeg'
                }
            })
        }
        
        response = upload_image.lambda_handler(event, {})
        assert response['statusCode'] == 201
        body = json.loads(response['body'])
        assert 'image_id' in body
        assert body['message'] == 'Image uploaded successfully'

    def test_upload_invalid_data(self, mock_aws):
        event = {'body': 'invalid_json'}
        response = upload_image.lambda_handler(event, {})
        assert response['statusCode'] == 500

class TestListImages:
    def test_list_all_images(self, mock_aws):
        # Setup test data
        table = mock_aws.dynamodb.Table(mock_aws.table_name)
        table.put_item(Item={
            'image_id': 'img1',
            'user_id': 'user1',
            'title': 'Image 1',
            'tags': ['nature'],
            'created_at': '2023-01-01T00:00:00'
        })
        
        event = {}
        response = list_images.lambda_handler(event, {})
        assert response['statusCode'] == 200
        body = json.loads(response['body'])
        assert body['count'] == 1

    def test_list_by_user(self, mock_aws):
        event = {'queryStringParameters': {'user_id': 'user1'}}
        response = list_images.lambda_handler(event, {})
        assert response['statusCode'] == 200

    def test_list_by_tag(self, mock_aws):
        event = {'queryStringParameters': {'tag': 'nature'}}
        response = list_images.lambda_handler(event, {})
        assert response['statusCode'] == 200

class TestViewImage:
    def test_view_existing_image(self, mock_aws):
        # Setup test data
        table = mock_aws.dynamodb.Table(mock_aws.table_name)
        table.put_item(Item={
            'image_id': 'img1',
            'user_id': 'user1',
            's3_key': 'images/img1',
            'content_type': 'image/jpeg'
        })
        
        mock_aws.s3.put_object(
            Bucket=mock_aws.bucket_name,
            Key='images/img1',
            Body=b'fake_image_data'
        )
        
        event = {'pathParameters': {'image_id': 'img1'}}
        response = view_image.lambda_handler(event, {})
        assert response['statusCode'] == 200
        assert response['isBase64Encoded'] == True

    def test_view_nonexistent_image(self, mock_aws):
        event = {'pathParameters': {'image_id': 'nonexistent'}}
        response = view_image.lambda_handler(event, {})
        assert response['statusCode'] == 404

class TestDeleteImage:
    def test_delete_existing_image(self, mock_aws):
        # Setup test data
        table = mock_aws.dynamodb.Table(mock_aws.table_name)
        table.put_item(Item={
            'image_id': 'img1',
            'user_id': 'user1',
            's3_key': 'images/img1'
        })
        
        mock_aws.s3.put_object(
            Bucket=mock_aws.bucket_name,
            Key='images/img1',
            Body=b'fake_image_data'
        )
        
        event = {'pathParameters': {'image_id': 'img1'}}
        response = delete_image.lambda_handler(event, {})
        assert response['statusCode'] == 200

    def test_delete_nonexistent_image(self, mock_aws):
        event = {'pathParameters': {'image_id': 'nonexistent'}}
        response = delete_image.lambda_handler(event, {})
        assert response['statusCode'] == 404