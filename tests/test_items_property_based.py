from __future__ import annotations
from hypothesis import given, strategies as st

name_strat = st.text(min_size=1, max_size=64).filter(lambda s: not s.isspace())
price_strat = st.floats(min_value=0, max_value=1e6, allow_nan=False, allow_infinity=False)

@given(name=name_strat, price=price_strat)
def test_create_property_based(client, auth_headers, name, price):
    r = client.post("/api/v1/items", json={"name": name, "price": price}, headers=auth_headers)
    # Some names could collide with existing ones → allow 201 or 409
    assert r.status_code in (201, 409)
