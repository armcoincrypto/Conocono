from fastapi.testclient import TestClient

from app_fastapi import app

client = TestClient(app)


def test_chat_minimal():
    r = client.post("/chat", json={"message": "Say hi"})
    assert r.status_code == 200
    data = r.json()
    assert "message" in data and isinstance(data["message"], str)
