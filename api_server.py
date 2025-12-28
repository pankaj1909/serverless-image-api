from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import Response
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import base64
import json
import sys
import os

# Add src to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from src.handlers import upload_image, list_images, view_image, delete_image

app = FastAPI(
    title="Instagram-like Image Service API",
    description="A scalable image upload and management service using AWS Lambda, S3, and DynamoDB",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Pydantic models for request/response validation
class ImageMetadata(BaseModel):
    user_id: str
    title: Optional[str] = ""
    description: Optional[str] = ""
    tags: Optional[List[str]] = []
    content_type: Optional[str] = "image/jpeg"

class UploadImageRequest(BaseModel):
    image: str  # base64 encoded
    metadata: ImageMetadata

class UploadImageResponse(BaseModel):
    image_id: str
    message: str

class ImageInfo(BaseModel):
    image_id: str
    user_id: str
    title: str
    description: str
    tags: List[str]
    content_type: str
    created_at: str

class ListImagesResponse(BaseModel):
    images: List[ImageInfo]
    count: int

class DeleteImageResponse(BaseModel):
    message: str

class ErrorResponse(BaseModel):
    error: str

@app.post("/images", 
          response_model=UploadImageResponse,
          responses={500: {"model": ErrorResponse}},
          summary="Upload Image",
          description="Upload an image with metadata to S3 and save metadata to DynamoDB")
async def upload_image_endpoint(request: UploadImageRequest):
    """
    Upload an image with metadata.
    
    - **image**: Base64 encoded image data (supports data URL format: data:image/type;base64,xxxxx)
    - **metadata**: Image metadata including user_id, title, description, tags, and content_type
    
    Returns the generated image_id and success message.
    """
    event = {
        'body': json.dumps({
            'image': request.image,
            'metadata': request.metadata.dict()
        })
    }
    
    result = upload_image.lambda_handler(event, {})
    
    if result['statusCode'] == 201:
        body = json.loads(result['body'])
        return UploadImageResponse(**body)
    else:
        body = json.loads(result['body'])
        raise HTTPException(status_code=result['statusCode'], detail=body.get('error'))

@app.get("/images",
         response_model=ListImagesResponse,
         responses={500: {"model": ErrorResponse}},
         summary="List Images",
         description="List all images with optional filtering by user_id or tag")
async def list_images_endpoint(
    user_id: Optional[str] = Query(None, description="Filter by user ID"),
    tag: Optional[str] = Query(None, description="Filter by tag")
):
    """
    List images with optional filters.
    
    - **user_id**: Filter images by user ID
    - **tag**: Filter images by tag
    
    Returns list of images and total count.
    """
    query_params = {}
    if user_id:
        query_params['user_id'] = user_id
    if tag:
        query_params['tag'] = tag
    
    event = {
        'queryStringParameters': query_params if query_params else None
    }
    
    result = list_images.lambda_handler(event, {})
    
    if result['statusCode'] == 200:
        body = json.loads(result['body'])
        return ListImagesResponse(**body)
    else:
        body = json.loads(result['body'])
        raise HTTPException(status_code=result['statusCode'], detail=body.get('error'))

@app.get("/images/{image_id}",
         responses={
             200: {"content": {"image/jpeg": {}, "image/png": {}, "image/gif": {}}},
             404: {"model": ErrorResponse},
             500: {"model": ErrorResponse}
         },
         summary="View/Download Image",
         description="Retrieve and download a specific image by ID")
async def view_image_endpoint(image_id: str):
    """
    View/download a specific image.
    
    - **image_id**: The unique identifier of the image
    
    Returns the image binary data with appropriate content-type headers.
    """
    event = {
        'pathParameters': {'image_id': image_id}
    }
    
    result = view_image.lambda_handler(event, {})
    
    if result['statusCode'] == 200:
        image_data = base64.b64decode(result['body'])
        content_type = result['headers']['Content-Type']
        return Response(content=image_data, media_type=content_type)
    else:
        body = json.loads(result['body'])
        raise HTTPException(status_code=result['statusCode'], detail=body.get('error'))

@app.delete("/images/{image_id}",
            response_model=DeleteImageResponse,
            responses={
                404: {"model": ErrorResponse},
                500: {"model": ErrorResponse}
            },
            summary="Delete Image",
            description="Delete an image and its metadata")
async def delete_image_endpoint(image_id: str):
    """
    Delete an image and its metadata.
    
    - **image_id**: The unique identifier of the image to delete
    
    Returns success message.
    """
    event = {
        'pathParameters': {'image_id': image_id}
    }
    
    result = delete_image.lambda_handler(event, {})
    
    if result['statusCode'] == 200:
        body = json.loads(result['body'])
        return DeleteImageResponse(**body)
    else:
        body = json.loads(result['body'])
        raise HTTPException(status_code=result['statusCode'], detail=body.get('error'))

@app.get("/health",
         summary="Health Check",
         description="Check if the API is running")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "message": "Instagram Image Service API is running"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)