# Instagram-like Image Service API

## Overview
A scalable image upload and management service using AWS Lambda, S3, and DynamoDB with LocalStack for local development.

## Setup Instructions

### Prerequisites
- Python 3.7+
- Docker and Docker Compose
- pip

### Local Development Setup

1. **Install dependencies:**
```bash
pip install -r requirements.txt
```

2. **Start LocalStack:**
```bash
docker compose up -d
```

3. **Setup AWS resources:**
```bash
python3 infrastructure/setup_localstack.py
```

4. **Deploy Lambda functions:**
```bash
python3 infrastructure/deploy_lambda.py
```

5. **Test Lambda functions:**
```bash
python3 infrastructure/test_lambda.py
```

6. **Start Interactive API Documentation:**
```bash
python3 infrastructure/start_api_docs.py
# Or directly from project root: uvicorn api_server:app --reload
# Access at: http://localhost:8000/docs
```

7. **Run unit tests:**
```bash
pytest tests/test_image_service.py -v
```

## Interactive API Documentation

### Quick Start
Start the interactive API documentation server:
```bash
python3 infrastructure/start_api_docs.py
```

### Access Points
- **Swagger UI**: http://localhost:8000/docs (Interactive testing)
- **ReDoc**: http://localhost:8000/redoc (Clean documentation)
- **API Base URL**: http://localhost:8000
- **Health Check**: http://localhost:8000/health

### Features
The interactive documentation allows you to:
- ✅ **Test all endpoints directly** in the browser
- ✅ **See request/response schemas** with validation
- ✅ **Try different parameters** and payloads
- ✅ **Upload and download images** interactively
- ✅ **View real-time responses** with proper error handling
- ✅ **Copy curl commands** for external testing

### Using the Interactive Documentation

1. **Navigate to Swagger UI**: http://localhost:8000/docs
2. **Expand any endpoint** to see details
3. **Click "Try it out"** to enable testing
4. **Fill in parameters** (use the examples below)
5. **Click "Execute"** to make the API call
6. **View the response** in real-time

### Sample Test Data

**For Upload Image endpoint:**
```json
{
  "image": "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8/5+hHgAHggJ/PchI7wAAAABJRU5ErkJggg==",
  "metadata": {
    "user_id": "test_user_123",
    "title": "Test Image",
    "description": "A sample test image",
    "tags": ["test", "sample"],
    "content_type": "image/png"
  }
}
```

**For List Images filters:**
- user_id: `test_user_123`
- tag: `test`

## API Documentation

### Interactive Documentation (Recommended)
For the best experience, use the **interactive API documentation**:

1. **Start the server**: `python3 infrastructure/start_api_docs.py`
2. **Open Swagger UI**: http://localhost:8000/docs
3. **Test endpoints directly** in your browser

### Static Documentation
For detailed API reference, see [API_DOCUMENTATION.md](API_DOCUMENTATION.md)

## API Endpoints Summary

### 1. Upload Image
**POST** `/images`

Upload an image with metadata.

**Request Body:**
```json
{
  "image": "base64_encoded_image_data",
  "metadata": {
    "user_id": "user123",
    "title": "My Photo",
    "description": "A beautiful sunset",
    "tags": ["sunset", "nature"],
    "content_type": "image/jpeg"
  }
}
```

**Response:**
```json
{
  "image_id": "uuid-generated-id",
  "message": "Image uploaded successfully"
}
```

### 2. List Images
**GET** `/images`

List all images with optional filters.

**Query Parameters:**
- `user_id`: Filter by user ID
- `tag`: Filter by tag

**Examples:**
- `/images` - List all images
- `/images?user_id=user123` - List images by user
- `/images?tag=nature` - List images with "nature" tag

**Response:**
```json
{
  "images": [
    {
      "image_id": "uuid",
      "user_id": "user123",
      "title": "My Photo",
      "description": "A beautiful sunset",
      "tags": ["sunset", "nature"],
      "created_at": "2023-01-01T00:00:00"
    }
  ],
  "count": 1
}
```

### 3. View/Download Image
**GET** `/images/{image_id}`

Retrieve and download a specific image.

**Response:**
- Returns the image binary data with appropriate content-type headers
- Status 404 if image not found

### 4. Delete Image
**DELETE** `/images/{image_id}`

Delete an image and its metadata.

**Response:**
```json
{
  "message": "Image deleted successfully"
}
```

## Architecture

### Components
- **Lambda Functions**: Serverless API handlers
- **S3**: Image storage
- **DynamoDB**: Metadata storage with GSI for user queries
- **API Gateway**: REST API routing (production)

### Scalability Features
- DynamoDB Global Secondary Index for efficient user-based queries
- S3 for unlimited image storage
- Lambda auto-scaling
- Stateless design for horizontal scaling

### Security Considerations
- S3 keys not exposed in API responses
- Input validation and error handling
- Base64 encoding for image transport

## Testing

### Interactive Testing (Recommended)
1. **Start API server**: `python3 infrastructure/start_api_docs.py`
2. **Open Swagger UI**: http://localhost:8000/docs
3. **Test all endpoints** directly in browser

### Unit Tests
Run the complete test suite:
```bash
pytest tests/test_image_service.py -v
```

### Lambda Function Testing
Test deployed Lambda functions in LocalStack:
```bash
python3 infrastructure/test_lambda.py
```

### Manual API Testing
You can also invoke Lambda functions directly:
```bash
# Upload image
aws lambda invoke --endpoint-url=http://localhost:4566 \
  --function-name upload-image \
  --payload '{"body":"{\"image\":\"base64data\",\"metadata\":{\"user_id\":\"test\"}}"}' \
  response.json

# List images  
aws lambda invoke --endpoint-url=http://localhost:4566 \
  --function-name list-images \
  --payload '{}' \
  response.json
```

### Alternative Testing Methods

**Using curl with FastAPI server:**
```bash
# Upload image
curl -X POST http://localhost:8000/images \
  -H "Content-Type: application/json" \
  -d '{"image":"base64data","metadata":{"user_id":"test"}}'

# List images
curl http://localhost:8000/images?user_id=test
```

**Using Python requests:**
```python
import requests
import base64

# Upload image
with open('test.jpg', 'rb') as f:
    image_data = base64.b64encode(f.read()).decode()

response = requests.post('http://localhost:8000/images', json={
    'image': image_data,
    'metadata': {'user_id': 'test', 'title': 'Test'}
})
print(response.json())
```

## Project Structure

```
├── src/
│   ├── handlers/          # Lambda function handlers
│   │   ├── upload_image.py
│   │   ├── list_images.py
│   │   ├── view_image.py
│   │   └── delete_image.py
│   └── utils/             # Shared utilities
│       ├── image_service.py
│       ├── response.py
│       └── logger.py
├── tests/                 # Test files
│   └── test_image_service.py
├── infrastructure/        # Infrastructure setup
│   ├── setup_localstack.py
│   ├── deploy_lambda.py
│   ├── test_lambda.py
│   └── start_api_docs.py
├── api_server.py          # FastAPI server for interactive docs
├── serverless.yml         # Serverless deployment config
├── template.yaml          # SAM deployment config
├── docker-compose.yml     # LocalStack setup
├── requirements.txt       # Python dependencies
└── API_DOCUMENTATION.md   # Detailed API reference
```

## Development Workflow

### Complete Setup (First Time)
```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Start LocalStack
docker compose up -d

# 3. Setup AWS resources
python3 infrastructure/setup_localstack.py

# 4. Deploy Lambda functions
python3 infrastructure/deploy_lambda.py

# 5. Start interactive API docs
python3 infrastructure/start_api_docs.py
```

### Daily Development
```bash
# Start LocalStack (if not running)
docker compose up -d

# Start API documentation server
python3 infrastructure/start_api_docs.py

# Open browser to http://localhost:8000/docs
# Test your API changes interactively
```

### Testing Workflow
```bash
# Run unit tests
pytest tests/test_image_service.py -v

# Test Lambda functions
python3 infrastructure/test_lambda.py

# Interactive testing via Swagger UI
# http://localhost:8000/docs
```

## Production Deployment

Using Serverless Framework:
```bash
npm install -g serverless
serverless deploy
```

Or manually:
1. Package Lambda functions with dependencies
2. Configure API Gateway routes
3. Set up proper IAM roles and policies
4. Configure CloudWatch logging
5. Set up monitoring and alerts