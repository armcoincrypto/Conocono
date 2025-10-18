from fastapi.testclient import TestClient

from app_fastapi import app

client = TestClient(app)


def test_chat_minimal():
    r = client.post("/chat", json={"message": "Hi"})
    assert r.status_code == 200
    data = r.json()
    assert isinstance(data.get("message"), str)
