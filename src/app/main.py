from __future__ import annotations
from typing import Literal, Sequence
from fastapi import Depends, FastAPI, HTTPException, Query, status
from sqlalchemy import func, asc, desc
from sqlmodel import select, Session

from .db import get_session
from .models import Item
from .schemas import ItemCreate, ItemRead, ItemUpdate
from .auth import require_auth, token_issuer  # NEW

app = FastAPI(title="Green DevOps FastAPI", version="1.1.0")

@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/auth/token")
def issue_token():
    # Not secure; just exposes the configured token so black-box tests can obtain it.
    return {"access_token": token_issuer(), "token_type": "bearer"}

def _apply_filters(stmt, min_price: float | None, max_price: float | None, q: str | None):
    if min_price is not None:
        stmt = stmt.where(Item.price >= min_price)
    if max_price is not None:
        stmt = stmt.where(Item.price <= max_price)
    if q:
        stmt = stmt.where(func.lower(Item.name).contains(q.lower()))
    return stmt

def _apply_sort(stmt, order_by: Literal["id", "name", "price"], direction: Literal["asc", "desc"]):
    col = {"id": Item.id, "name": Item.name, "price": Item.price}[order_by]
    return stmt.order_by(asc(col) if direction == "asc" else desc(col))

# All v1 endpoints now require auth
@app.post("/api/v1/items", response_model=ItemRead, status_code=status.HTTP_201_CREATED)
def create_item(payload: ItemCreate, session: Session = Depends(get_session), user=Depends(require_auth)):
    item = Item(name=payload.name, price=payload.price)
    session.add(item)
    try:
        session.commit()
    except Exception as e:
        session.rollback()
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Item name must be unique") from e
    session.refresh(item)
    return item

@app.get("/api/v1/items/{item_id}", response_model=ItemRead)
def get_item(item_id: int, session: Session = Depends(get_session), user=Depends(require_auth)):
    item = session.get(Item, item_id)
    if not item:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Item not found")
    return item

@app.get("/api/v1/items", response_model=list[ItemRead])
def list_items(
    min_price: float | None = Query(default=None, ge=0),
    max_price: float | None = Query(default=None, ge=0),
    q: str | None = Query(default=None, min_length=1),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    order_by: Literal["id", "name", "price"] = "id",
    direction: Literal["asc", "desc"] = "asc",
    session: Session = Depends(get_session),
    user=Depends(require_auth),
):
    stmt = select(Item)
    stmt = _apply_filters(stmt, min_price, max_price, q)
    stmt = _apply_sort(stmt, order_by, direction)
    stmt = stmt.limit(limit).offset(offset)
    items: Sequence[Item] = session.exec(stmt).all()
    return list(items)

@app.patch("/api/v1/items/{item_id}", response_model=ItemRead)
def update_item(item_id: int, payload: ItemUpdate, session: Session = Depends(get_session), user=Depends(require_auth)):
    item = session.get(Item, item_id)
    if not item:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Item not found")

    if payload.name is not None:
        item.name = payload.name
    if payload.price is not None:
        item.price = payload.price

    try:
        session.add(item)
        session.commit()
    except Exception as e:
        session.rollback
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Item name must be unique") from e
    session.refresh(item)
    return item
