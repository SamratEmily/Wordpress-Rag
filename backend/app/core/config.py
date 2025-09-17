from pydantic_settings import BaseSettings
from pydantic import Field, validator
from typing import Optional
import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Settings(BaseSettings):
    """Application settings and configuration"""
    
    # API Configuration
    API_VERSION: str = Field(default="1.0.0", description="API version")
    DEBUG: bool = Field(default=False, description="Debug mode")
    OPENAI_API_KEY: str = Field(..., description="OpenAI API key")
    
    # Vector Store Configuration
    CHROMA_PERSIST_DIRECTORY: str = Field(
        default="docs_db",
        description="Directory to persist vector store data"
    )
    CHUNK_SIZE: int = Field(
        default=500,
        description="Size of text chunks for document processing"
    )
    CHUNK_OVERLAP: int = Field(
        default=50,
        description="Overlap between text chunks"
    )
    
    # Model Configuration
    MODEL_NAME: str = Field(
        default="gpt-3.5-turbo",
        description="OpenAI model to use"
    )
    TEMPERATURE: float = Field(
        default=0.7,
        ge=0.0,
        le=1.0,
        description="Model temperature"
    )
    MAX_TOKENS: Optional[int] = Field(
        default=None,
        description="Maximum tokens for model response"
    )
    
    # API Rate Limiting
    RATE_LIMIT_PER_MINUTE: int = Field(
        default=60,
        gt=0,
        description="Maximum requests per minute per client"
    )
    
    # CORS Configuration
    CORS_ORIGINS: list[str] = Field(
        default=["*"],
        description="Allowed CORS origins"
    )
    
    class Config:
        env_file = ".env"
        case_sensitive = True
    
    @validator("OPENAI_API_KEY")
    def validate_api_key(cls, v: str) -> str:
        """Validate OpenAI API key"""
        if not v:
            raise ValueError("OPENAI_API_KEY must be set")
        return v
    
    @validator("CHROMA_PERSIST_DIRECTORY")
    def validate_persist_directory(cls, v: str) -> str:
        """Ensure persist directory exists"""
        path = Path(v)
        path.mkdir(parents=True, exist_ok=True)
        return str(path)
    
    @validator("CHUNK_OVERLAP")
    def validate_chunk_overlap(cls, v: int, values: dict) -> int:
        """Validate chunk overlap is less than chunk size"""
        if "CHUNK_SIZE" in values and v >= values["CHUNK_SIZE"]:
            raise ValueError("CHUNK_OVERLAP must be less than CHUNK_SIZE")
        return v

settings = Settings() 