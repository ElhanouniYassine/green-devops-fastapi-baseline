from __future__ import annotations

def test_perf_create_and_list(benchmark, client, auth_headers):
    def _roundtrip():
        client.post("/api/v1/items", json={"name": "bm-item", "price": 1.23}, headers=auth_headers)
        client.get("/api/v1/items?limit=10&offset=0", headers=auth_headers)
    benchmark(_roundtrip)
