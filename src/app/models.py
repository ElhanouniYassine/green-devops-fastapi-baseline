from __future__ import annotations
from typing import Optional

from sqlmodel import Field, SQLModel
from sqlalchemy import UniqueConstraint


class Item(SQLModel, table=True):
    __tablename__ = "items"
    __table_args__ = (UniqueConstraint("name", name="uq_items_name"),)

    id: Optional[int] = Field(default=None, primary_key=True)
    # Keep a DB-level unique constraint via __table_args__ above.
    # Add an index to speed up name searches.
    name: str = Field(index=True, min_length=1, max_length=128)
    # Validation on price is enforced at the schema level too; DB stores a float.
    price: float = Field(ge=0)
