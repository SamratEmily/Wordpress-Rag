from fastapi import HTTPException, Request
from fastapi.responses import JSONResponse
from typing import Any, Dict
import logging

logger = logging.getLogger(__name__)

class RAGException(HTTPException):
    """Base exception for RAG-related errors"""
    def __init__(self, status_code: int, detail: str):
        super().__init__(status_code=status_code, detail=detail)

class ModelInitializationError(RAGException):
    """Exception raised when model initialization fails"""
    def __init__(self, detail: str = "Failed to initialize model"):
        super().__init__(status_code=500, detail=detail)

class QueryProcessingError(RAGException):
    """Exception raised when query processing fails"""
    def __init__(self, detail: str = "Failed to process query"):
        super().__init__(status_code=500, detail=detail)

class RateLimitExceeded(RAGException):
    """Exception raised when rate limit is exceeded"""
    def __init__(self, detail: str = "Rate limit exceeded"):
        super().__init__(status_code=429, detail=detail)

async def http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
    """Handle HTTP exceptions"""
    logger.error(f"HTTP error: {exc.detail}")
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail}
    )

async def rag_exception_handler(request: Request, exc: RAGException) -> JSONResponse:
    """Handle RAG-specific exceptions"""
    logger.error(f"RAG error: {exc.detail}")
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "detail": exc.detail,
            "type": exc.__class__.__name__
        }
    )

async def general_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Handle unexpected exceptions"""
    logger.error(f"Unexpected error: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "detail": "An unexpected error occurred",
            "type": exc.__class__.__name__
        }
    ) 