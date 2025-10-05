
from __future__ import annotations
from fastapi import FastAPI, HTTPException, Depends
from sqlmodel import select
from .models import Item
from .db import init_db, get_session
from sqlmodel import Session

app = FastAPI(title="Green DevOps FastAPI Baseline")

@app.on_event("startup")
def on_startup():
    init_db()
    
@app.on_event("startup")
def ensure_db():
    from .db import init_db
    init_db()
    
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
