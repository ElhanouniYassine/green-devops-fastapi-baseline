from __future__ import annotations
from pydantic import BaseModel, Field


class ItemBase(BaseModel):
    name: str = Field(min_length=1, max_length=128)
    price: float = Field(ge=0)


class ItemCreate(ItemBase):
    """Payload for creating an item."""
    pass


class ItemRead(ItemBase):
    """Response model for reading an item."""
    id: int


class ItemUpdate(BaseModel):
    """Partial update payload."""
    name: str | None = Field(default=None, min_length=1, max_length=128)
    price: float | None = Field(default=None, ge=0)
