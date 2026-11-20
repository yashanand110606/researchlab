"""Pydantic v2 schemas for experiments."""
from __future__ import annotations

from datetime import datetime
from typing import Any, Optional
from uuid import UUID

from pydantic import BaseModel, Field


class ExperimentCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    category: str = Field("general", max_length=100)
    configuration: dict[str, Any] = Field(default_factory=dict)


class ExperimentUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    category: Optional[str] = Field(None, max_length=100)
    configuration: Optional[dict[str, Any]] = None


class ExperimentOut(BaseModel):
    id: UUID
    name: str
    description: Optional[str]
    category: str
    configuration: dict[str, Any]
    configuration_version: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class TagAdd(BaseModel):
    tag: str = Field(..., min_length=1, max_length=50)


class ExperimentListParams(BaseModel):
    skip: int = 0
    limit: int = 20
    category: Optional[str] = None
    search: Optional[str] = None
    sort_by: str = "created_at"
    sort_order: str = "desc"


class PaginationMeta(BaseModel):
    total: int
    skip: int
    limit: int
