from __future__ import annotations

def test_filtering_and_search(client, auth_headers):
    client.post("/api/v1/items", json={"name": "alpha", "price": 1.0}, headers=auth_headers)
    client.post("/api/v1/items", json={"name": "beta", "price": 2.0}, headers=auth_headers)
    client.post("/api/v1/items", json={"name": "alphabet", "price": 3.0}, headers=auth_headers)

    r = client.get("/api/v1/items?min_price=1.5&max_price=3.0", headers=auth_headers)
    assert r.status_code == 200
    assert all(1.5 <= i["price"] <= 3.0 for i in r.json())

    r = client.get("/api/v1/items?q=alpha", headers=auth_headers)
    names = [i["name"] for i in r.json()]
    assert "alpha" in names or "alphabet" in names
