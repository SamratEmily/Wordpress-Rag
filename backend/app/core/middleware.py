from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse
from typing import Dict, List
import time
import logging
from .config import settings

logger = logging.getLogger(__name__)

class RateLimiter:
    """Rate limiter middleware"""
    
    def __init__(self):
        """Initialize rate limiter"""
        self.request_times: Dict[str, List[float]] = {}
    
    def check_rate_limit(self, client_id: str) -> bool:
        """
        Check if client has exceeded rate limit
        
        Args:
            client_id: Client identifier (IP address)
            
        Returns:
            bool: True if within rate limit, False otherwise
        """
        current_time = time.time()
        
        # Initialize client if not exists
        if client_id not in self.request_times:
            self.request_times[client_id] = []
        
        # Remove old requests
        self.request_times[client_id] = [
            t for t in self.request_times[client_id]
            if current_time - t < 60
        ]
        
        # Check rate limit
        if len(self.request_times[client_id]) >= settings.RATE_LIMIT_PER_MINUTE:
            logger.warning(f"Rate limit exceeded for client {client_id}")
            return False
        
        # Add current request
        self.request_times[client_id].append(current_time)
        return True

# Create singleton instance
rate_limiter = RateLimiter()

async def rate_limit_middleware(request: Request, call_next):
    """Rate limiting middleware function"""
    client_id = request.client.host
    
    if not rate_limiter.check_rate_limit(client_id):
        return JSONResponse(
            status_code=429,
            content={
                "detail": "Rate limit exceeded. Please try again later.",
                "retry_after": 60
            }
        )
    
    return await call_next(request) 