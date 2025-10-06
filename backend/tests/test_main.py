from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_health():
    """Test health check endpoint."""
    response = client.get("/healthz")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_demo_endpoint():
    """Test demo endpoint structure (mocking not required for structure test)."""
    # This test verifies the endpoint exists
    # For full testing, mock the OpenAI client
    assert "/v1/chat/demo" in [route.path for route in app.routes]
