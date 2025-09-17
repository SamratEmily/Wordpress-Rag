from pydantic import BaseModel, Field
from typing import Optional

class QueryRequest(BaseModel):
    """Request model for querying the RAG system"""
    question: str = Field(..., description="The question to ask about the documents")
    context: Optional[str] = Field(None, description="Additional context for the question")

class QueryResponse(BaseModel):
    """Response model for RAG system queries"""
    answer: Optional[str] = Field(None, description="The answer to the question, or None if not relevant")
    sources: Optional[list[str]] = Field(None, description="Sources used to generate the answer")
    confidence: Optional[float] = Field(None, description="Confidence score of the answer")
    message: Optional[str] = Field(None, description="Additional message about the response")

class DocumentUploadResponse(BaseModel):
    """Response model for document upload operations"""
    success: bool = Field(..., description="Whether the upload was successful")
    message: str = Field(..., description="Message about the upload result")
    chunks_added: Optional[int] = Field(None, description="Number of document chunks added")

class HealthResponse(BaseModel):
    """Response model for health check endpoint"""
    status: str = Field(..., description="Health status of the API")
    version: str = Field(..., description="API version")
    model: str = Field(..., description="Model being used")
    uptime: Optional[float] = Field(None, description="API uptime in seconds") 