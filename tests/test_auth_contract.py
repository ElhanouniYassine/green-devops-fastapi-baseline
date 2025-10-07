from __future__ import annotations

def test_requires_auth_for_v1(client):
    r = client.get("/api/v1/items")
    assert r.status_code == 401

def test_issue_and_use_token(client):
    # "Obtain" the token (demo endpoint)
    t = client.post("/auth/token").json()["access_token"]
    r = client.get("/api/v1/items", headers={"Authorization": f"Bearer {t}"})
    assert r.status_code == 200

def test_wrong_token(client):
    r = client.get("/api/v1/items", headers={"Authorization": "Bearer nope"})
    assert r.status_code == 401
