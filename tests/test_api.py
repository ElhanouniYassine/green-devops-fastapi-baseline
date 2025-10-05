
from __future__ import annotations
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_health():
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json()["status"] == "ok"

def test_create_and_get_item():
    payload = {"name": "widget", "price": 9.99}
    r = client.post("/items", json=payload)
    assert r.status_code == 200, r.text
    data = r.json()
    assert data["id"] == 1
    assert data["name"] == "widget"

    r2 = client.get("/items/1")
    assert r2.status_code == 200
    assert r2.json()["name"] == "widget"

def test_list_items():
    # create a couple
    client.post("/items", json={"name": "a", "price": 1.0})
    client.post("/items", json={"name": "b", "price": 2.0})
    r = client.get("/items")
    assert r.status_code == 200
    assert isinstance(r.json(), list)
    assert len(r.json()) >= 2
