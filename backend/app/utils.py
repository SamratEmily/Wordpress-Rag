from fastapi import HTTPException
from typing import Any, Dict
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def handle_api_error(error: Exception) -> Dict[str, Any]:
    """Handle API errors and return appropriate response"""
    logger.error(f"API Error: {str(error)}")
    raise HTTPException(
        status_code=500,
        detail=f"An error occurred: {str(error)}"
    )

def validate_api_key(api_key: str) -> None:
    """Validate OpenAI API key"""
    if not api_key:
        raise HTTPException(
            status_code=400,
            detail="OpenAI API key is not configured"
        ) 