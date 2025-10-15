from fastapi.testclient import TestClient
from app_fastapi import app

def test_health():
    c = TestClient(app)
    r = c.get("/health")
    assert r.status_code == 200
    assert r.json().get("status") == "ok"

def test_sum():
    c = TestClient(app)
    r = c.get("/sum", params={"a": 2, "b": 3})
    assert r.status_code == 200
    data = r.json()
    assert data["sum"] == 5
