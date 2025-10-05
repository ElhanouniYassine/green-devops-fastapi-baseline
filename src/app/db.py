# src/app/db.py
from __future__ import annotations
from sqlmodel import SQLModel, create_engine, Session

# File-backed DB avoids "separate memory per connection" issues
DATABASE_URL = "sqlite:///./app.db"

engine = create_engine(
    DATABASE_URL,
    echo=False,
    connect_args={"check_same_thread": False},  # allow usage across threads in tests
)

def init_db() -> None:
    SQLModel.metadata.create_all(engine)

def get_session() -> Session:
    return Session(engine)
