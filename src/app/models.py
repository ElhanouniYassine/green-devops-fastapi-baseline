
from __future__ import annotations
from typing import Optional
from sqlmodel import SQLModel, Field

class Item(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    price: float
