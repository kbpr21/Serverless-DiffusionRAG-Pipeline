from fastapi.testclient import TestClient
import io

from app.main import app

client = TestClient(app)

def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}

def test_upload_document_empty():
    response = client.post("/upload")
    # Missing file should trigger 422 Unprocessable Entity by FastAPI
    assert response.status_code == 422

def test_upload_document_txt():
    # Simulate a valid txt file upload
    file_bytes = b"Hello world! This is a test."
    files = {"file": ("test.txt", io.BytesIO(file_bytes), "text/plain")}
    
    response = client.post("/upload", files=files)
    assert response.status_code == 200
    data = response.json()
    assert "document_id" in data
    assert data["filename"] == "test.txt"
    assert data["page_count"] == 1
    assert data["message"] == "Document indexed successfully."

    # Return doc ID for query test
    return data["document_id"]

def test_query_no_api_key(monkeypatch):
    """
    Test the query endpoint, simulating no API key present.
    It should return a 500 error per the application logic.
    """
    # Temporarily remove API key to test the missing key error path reliably
    monkeypatch.delenv("MERCURY_API_KEY", raising=False)
    
    # First upload a doc
    doc_id = test_upload_document_txt()

    # Then query
    payload = {
        "question": "What is this?",
        "document_id": doc_id
    }
    response = client.post("/query", json=payload)
    assert response.status_code == 500
    assert "MERCURY_API_KEY is not set" in response.json()["detail"]

def test_query_invalid_doc_id():
    """Querying with a doc_id that doesn't exist should yield a 404."""
    payload = {
        "question": "What is this?",
        "document_id": "invalid12345"
    }
    response = client.post("/query", json=payload)
    assert response.status_code == 404
    assert "invalid12345" in response.json()["detail"]
