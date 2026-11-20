"""Pydantic v2 schemas for datasets."""
from __future__ import annotations

from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field


class DatasetCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    file_format: str = Field(..., max_length=50)


class DatasetOut(BaseModel):
    id: UUID
    name: str
    description: Optional[str]
    filename: str
    file_format: str
    checksum: str
    size_bytes: int
    created_at: datetime

    class Config:
        from_attributes = True
