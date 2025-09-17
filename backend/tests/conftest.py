import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.core.config import settings
import tempfile

@pytest.fixture
def test_client():
    """Create a test client"""
    return TestClient(app)

@pytest.fixture
def test_env():
    """Set up test environment variables"""
    # Save original environment
    original_env = dict(os.environ)
    
    # Set test environment
    os.environ["OPENAI_API_KEY"] = "test_api_key"
    os.environ["DEBUG"] = "True"
    os.environ["RATE_LIMIT_PER_MINUTE"] = "60"
    
    yield
    
    # Restore original environment
    os.environ.clear()
    os.environ.update(original_env)

@pytest.fixture
def temp_db_dir():
    """Create a temporary directory for the vector store"""
    with tempfile.TemporaryDirectory() as temp_dir:
        original_dir = settings.CHROMA_PERSIST_DIRECTORY
        settings.CHROMA_PERSIST_DIRECTORY = temp_dir
        yield temp_dir
        settings.CHROMA_PERSIST_DIRECTORY = original_dir

@pytest.fixture
def mock_openai(monkeypatch):
    """Mock OpenAI API calls"""
    def mock_create(*args, **kwargs):
        return {
            "choices": [
                {
                    "message": {
                        "content": "This is a mock response"
                    }
                }
            ]
        }
    
    monkeypatch.setattr("openai.ChatCompletion.create", mock_create)
    return mock_create 