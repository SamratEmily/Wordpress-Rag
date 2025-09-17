import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_health_check():
    """Test health check endpoint"""
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "version" in data
    assert "model" in data
    assert "uptime" in data

def test_ask_endpoint():
    """Test ask endpoint"""
    question = "How do I create a custom post type?"
    response = client.post(
        "/api/v1/ask",
        json={"question": question}
    )
    assert response.status_code == 200
    data = response.json()
    assert "answer" in data
    assert "sources" in data
    assert "confidence" in data

def test_ask_endpoint_with_context():
    """Test ask endpoint with context"""
    question = "How do I create a custom post type?"
    context = "I'm working on a plugin"
    response = client.post(
        "/api/v1/ask",
        json={
            "question": question,
            "context": context
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert "answer" in data
    assert "sources" in data
    assert "confidence" in data

def test_ask_endpoint_invalid_request():
    """Test ask endpoint with invalid request"""
    response = client.post(
        "/api/v1/ask",
        json={}  # Missing required field
    )
    assert response.status_code == 422

@pytest.mark.asyncio
async def test_rate_limiting():
    """Test rate limiting"""
    # Make requests up to the rate limit
    for _ in range(60):
        response = client.post(
            "/api/v1/ask",
            json={"question": "test"}
        )
        assert response.status_code in [200, 429]
    
    # Next request should be rate limited
    response = client.post(
        "/api/v1/ask",
        json={"question": "test"}
    )
    assert response.status_code == 429
    assert "Rate limit exceeded" in response.json()["detail"] 