
from __future__ import annotations
from sqlmodel import SQLModel, create_engine, Session

# In-memory SQLite for simplicity
DATABASE_URL = "sqlite://"

engine = create_engine(DATABASE_URL, echo=False)

def init_db() -> None:
    SQLModel.metadata.create_all(engine)

def get_session() -> Session:
    return Session(engine)
