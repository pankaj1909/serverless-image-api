#!/usr/bin/env python3

import subprocess
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from src.utils.logger import get_logger

logger = get_logger(__name__)

def start_api_server():
    """Start the FastAPI server for interactive API documentation"""
    logger.info("Starting Interactive API Documentation Server...")
    logger.info("Server will be available at: http://localhost:8000")
    logger.info("Swagger UI: http://localhost:8000/docs")
    logger.info("ReDoc: http://localhost:8000/redoc")
    logger.info("Press Ctrl+C to stop the server")
    
    try:
        # Change to project root directory
        project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        os.chdir(project_root)
        
        # Start uvicorn server
        subprocess.run([
            sys.executable, "-m", "uvicorn", 
            "api_server:app", 
            "--host", "0.0.0.0", 
            "--port", "8000", 
            "--reload"
        ], check=True)
    except KeyboardInterrupt:
        logger.info("Server stopped by user")
    except Exception as e:
        logger.error(f"Error starting server: {e}")

if __name__ == "__main__":
    start_api_server()