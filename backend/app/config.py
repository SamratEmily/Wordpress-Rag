from pydantic_settings import BaseSettings
from dotenv import load_dotenv
import os
from typing import Optional

# Load environment variables from .env file
load_dotenv()

class Settings(BaseSettings):
    # API Configuration
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    API_VERSION: str = "1.0.0"
    DEBUG: bool = os.getenv("DEBUG", "False").lower() == "true"
    
    # Vector Store Configuration
    CHROMA_PERSIST_DIRECTORY: str = "docs_db"
    CHUNK_SIZE: int = 500
    CHUNK_OVERLAP: int = 50
    
    # Model Configuration
    MODEL_NAME: str = "gpt-3.5-turbo"
    TEMPERATURE: float = 0.7
    MAX_TOKENS: Optional[int] = None
    
    # API Rate Limiting
    RATE_LIMIT_PER_MINUTE: int = 60
    
    class Config:
        env_file = ".env"
        case_sensitive = True

    def validate_settings(self) -> None:
        """Validate critical settings"""
        if not self.OPENAI_API_KEY:
            raise ValueError("OPENAI_API_KEY must be set")
        if not os.path.exists(self.CHROMA_PERSIST_DIRECTORY):
            os.makedirs(self.CHROMA_PERSIST_DIRECTORY)

settings = Settings()
settings.validate_settings() 