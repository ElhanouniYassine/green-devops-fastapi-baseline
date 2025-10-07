from __future__ import annotations
import pytest
from fastapi.testclient import TestClient

from src.app.main import app

client = TestClient(app)


def test_health():
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json()["status"] == "ok"


def test_create_and_get_item():
    # create
    r = client.post("/api/v1/items", json={"name": "apple", "price": 1.5})
    assert r.status_code == 201, r.text
    item = r.json()
    assert item["id"] > 0
    assert item["name"] == "apple"
    assert item["price"] == 1.5

    # get
    r = client.get(f"/api/v1/items/{item['id']}")
    assert r.status_code == 200
    assert r.json()["name"] == "apple"


def test_list_items_pagination_and_sorting():
    # seed a few
    names_prices = [("banana", 0.9), ("carrot", 2.0), ("avocado", 1.8), ("blueberry", 3.2)]
    for n, p in names_prices:
        client.post("/api/v1/items", json={"name": n, "price": p})

    # limit & offset
    r = client.get("/api/v1/items?limit=2&offset=0&order_by=name&direction=asc")
    assert r.status_code == 200
    first_page = [i["name"] for i in r.json()]
    assert len(first_page) == 2
    assert first_page == sorted(first_page)

    r2 = client.get("/api/v1/items?limit=2&offset=2&order_by=name&direction=asc")
    assert r2.status_code == 200
    second_page = [i["name"] for i in r2.json()]
    assert len(second_page) >= 1
    # ensure no overlap
    assert set(first_page).isdisjoint(second_page)

    # filter by min/max price
    r = client.get("/api/v1/items?min_price=1.0&max_price=2.0&order_by=price&direction=asc")
    assert r.status_code == 200
    prices = [i["price"] for i in r.json()]
    assert all(1.0 <= p <= 2.0 for p in prices)
    assert prices == sorted(prices)

    # query by substring
    r = client.get("/api/v1/items?q=berry")
    assert r.status_code == 200
    names = [i["name"] for i in r.json()]
    assert any("berry" in n for n in names)


def test_validation_errors_and_uniqueness():
    # invalid: empty name
    r = client.post("/api/v1/items", json={"name": "", "price": 1.0})
    assert r.status_code == 422

    # invalid: negative price
    r = client.post("/api/v1/items", json={"name": "badprice", "price": -1})
    assert r.status_code == 422

    # unique name constraint
    r1 = client.post("/api/v1/items", json={"name": "unique-1", "price": 1})
    assert r1.status_code == 201
    r2 = client.post("/api/v1/items", json={"name": "unique-1", "price": 2})
    assert r2.status_code == 409

    # PATCH validation & uniqueness
    r3 = client.post("/api/v1/items", json={"name": "unique-2", "price": 1})
    item2 = r3.json()
    # empty/too short name invalid
    r = client.patch(f"/api/v1/items/{item2['id']}", json={"name": ""})
    assert r.status_code == 422
    # conflict with existing name
    r = client.patch(f"/api/v1/items/{item2['id']}", json={"name": "unique-1"})
    assert r.status_code == 409
