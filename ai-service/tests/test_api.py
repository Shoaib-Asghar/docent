import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch

from main import app

client = TestClient(app)

def test_health_check():
    """Test the basic health endpoint of the FastAPI app."""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}

def test_chat_missing_query():
    """Test validation errors for missing query."""
    response = client.post("/api/chat", json={})
    assert response.status_code == 422 # Unprocessable Entity (FastAPI standard)

@patch("main.get_pipeline")
def test_chat_success(mock_get_pipeline):
    """Test successful chat response via mocked RAG pipeline."""
    # Create a fake pipeline that returns our test data
    mock_pipeline = mock_get_pipeline.return_value
    mock_pipeline.process_query.return_value = {
        "answer": "This is a test response.",
        "metadata": {"top_score": 0.95}
    }
    
    response = client.post("/api/chat", json={"query": "Test query"})
    assert response.status_code == 200
    data = response.json()
    assert data["answer"] == "This is a test response."
    assert data["metadata"]["top_score"] == 0.95
