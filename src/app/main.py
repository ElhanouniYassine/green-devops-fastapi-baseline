from __future__ import annotations
from fastapi import FastAPI, HTTPException, Depends
from sqlmodel import select, Session
from .models import Item
from .db import init_db, get_session

# Ensure DB is created at import time — covers both server & tests
init_db()

app = FastAPI(title="Green DevOps FastAPI Baseline")

@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/items", response_model=Item)
def create_item(item: Item, session: Session = Depends(get_session)):
    session.add(item)
    session.commit()
    session.refresh(item)
    return item

@app.get("/items", response_model=list[Item])
def list_items(session: Session = Depends(get_session)):
    return session.exec(select(Item)).all()

@app.get("/items/{item_id}", response_model=Item)
def get_item(item_id: int, session: Session = Depends(get_session)):
    item = session.get(Item, item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    return item
