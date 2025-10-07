from __future__ import annotations
import pytest

@pytest.mark.parametrize(
    "payload,expected_status",
    [
        ({"name": "", "price": 1}, 422),
        ({"name": "ok", "price": -0.01}, 422),
        ({"name": "ok", "price": 0}, 201),
        ({"name": "x" * 129, "price": 1}, 422),
    ],
)
def test_create_validation_parametrized(client, auth_headers, payload, expected_status):
    r = client.post("/api/v1/items", json=payload, headers=auth_headers)
    assert r.status_code == expected_status

def test_pagination_and_sorting_parametrized(client, auth_headers):
    for n, p in [("banana", 0.9), ("carrot", 2.0), ("avocado", 1.8), ("blueberry", 3.2)]:
        client.post("/api/v1/items", json={"name": n, "price": p}, headers=auth_headers)
    r = client.get("/api/v1/items?limit=2&offset=0&order_by=name&direction=asc", headers=auth_headers)
    assert r.status_code == 200
    first = [i["name"] for i in r.json()]
    r2 = client.get("/api/v1/items?limit=2&offset=2&order_by=name&direction=asc", headers=auth_headers)
    second = [i["name"] for i in r2.json()]
    assert set(first).isdisjoint(second)
