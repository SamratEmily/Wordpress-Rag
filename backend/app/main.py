from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
import logging

from .core.config import settings
from .core.middleware import rate_limit_middleware
from .core.exceptions import (
    RAGException,
    http_exception_handler,
    rag_exception_handler,
    general_exception_handler
)
from .core.logging import setup_logging
from .api.routes import router

# Configure logging
setup_logging(
    log_level="DEBUG" if settings.DEBUG else "INFO",
    log_file="logs/app.log" if not settings.DEBUG else None
)
logger = logging.getLogger(__name__)

def create_app() -> FastAPI:
    """Create and configure FastAPI application"""
    
    app = FastAPI(
        title="WordPress Documentation RAG API",
        description="API for querying WordPress documentation using RAG",
        version=settings.API_VERSION,
        debug=settings.DEBUG
    )
    
    # Add CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Add rate limiting middleware
    app.middleware("http")(rate_limit_middleware)
    
    # Add exception handlers
    app.add_exception_handler(RAGException, rag_exception_handler)
    app.add_exception_handler(Exception, general_exception_handler)
    
    # Include API routes
    app.include_router(router, prefix="/api/v1")
    
    @app.on_event("startup")
    async def startup_event():
        """Initialize components on startup"""
        logger.info("Starting up WordPress Documentation RAG API")
    
    @app.on_event("shutdown")
    async def shutdown_event():
        """Cleanup on shutdown"""
        logger.info("Shutting down WordPress Documentation RAG API")
    
    return app

app = create_app() 