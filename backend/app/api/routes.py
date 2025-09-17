from fastapi import APIRouter, Request, HTTPException, UploadFile, File, Form
from typing import Dict, Any, List
import time
import logging
import os
from pathlib import Path

from ..models.schemas import QueryRequest, QueryResponse, HealthResponse, DocumentUploadResponse
from ..services.rag_service import rag_service
from ..core.config import settings

logger = logging.getLogger(__name__)
router = APIRouter()

# Track API start time for uptime calculation
START_TIME = time.time()

@router.post("/ask", response_model=QueryResponse)
async def ask_docs(request: QueryRequest, req: Request) -> Dict[str, Any]:
    """
    Query the RAG system with a question about documents
    
    Args:
        request: Query request containing question and optional context
        req: FastAPI request object
        
    Returns:
        QueryResponse containing answer and metadata, or None if not relevant
    """
    try:
        logger.info(f"Received question from {req.client.host}: {request.question}")
        
        # Process query through RAG service
        result = await rag_service.query(
            question=request.question,
            context=request.context
        )
        
        return QueryResponse(**result)
    except Exception as e:
        logger.error(f"Error processing query: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error processing query: {str(e)}"
        )

@router.post("/documents/upload", response_model=DocumentUploadResponse)
async def upload_document(
    file: UploadFile = File(...),
    source_name: str = Form(None)
) -> Dict[str, Any]:
    """
    Upload a document to the RAG system
    
    Args:
        file: The document file to upload
        source_name: Optional custom name for the document source
        
    Returns:
        DocumentUploadResponse containing upload result
    """
    try:
        # Create uploads directory if it doesn't exist
        upload_dir = Path("uploads")
        upload_dir.mkdir(exist_ok=True)
        
        # Save uploaded file
        file_path = upload_dir / file.filename
        with open(file_path, "wb") as buffer:
            content = await file.read()
            buffer.write(content)
        
        # Add document to RAG system
        result = await rag_service.add_document_from_file(
            str(file_path), 
            source_name or file.filename
        )
        
        # Clean up uploaded file
        os.remove(file_path)
        
        return DocumentUploadResponse(**result)
    except Exception as e:
        logger.error(f"Error uploading document: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error uploading document: {str(e)}"
        )

@router.post("/documents/add-text")
async def add_text_document(
    content: str = Form(...),
    source_name: str = Form(...)
) -> Dict[str, Any]:
    """
    Add a text document directly to the RAG system
    
    Args:
        content: The text content of the document
        source_name: Name for the document source
        
    Returns:
        Dict containing the result of the operation
    """
    try:
        from langchain.schema import Document
        
        # Create document from text content
        document = Document(
            page_content=content,
            metadata={"source": source_name, "type": "text_input"}
        )
        
        # Add to RAG system
        result = await rag_service.add_documents([document])
        
        return result
    except Exception as e:
        logger.error(f"Error adding text document: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error adding text document: {str(e)}"
        )

@router.get("/documents/count")
async def get_document_count() -> Dict[str, Any]:
    """
    Get the number of documents in the RAG system
    
    Returns:
        Dict containing document count
    """
    try:
        count = await rag_service.get_document_count()
        return {"document_count": count}
    except Exception as e:
        logger.error(f"Error getting document count: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error getting document count: {str(e)}"
        )

@router.get("/health", response_model=HealthResponse)
async def health_check() -> Dict[str, Any]:
    """
    Check API health status
    
    Returns:
        HealthResponse containing API status and metadata
    """
    uptime = time.time() - START_TIME
    
    return HealthResponse(
        status="healthy",
        version=settings.API_VERSION,
        model=settings.MODEL_NAME,
        uptime=uptime
    ) 