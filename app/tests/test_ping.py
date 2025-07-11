from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_ping():
    response = client.get("/api/v1/ping")
    assert response.status_code == 200
    assert response.json() == {"msg": "pong"}
