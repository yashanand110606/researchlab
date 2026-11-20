"""Dataset management endpoints."""
from __future__ import annotations

import hashlib
import logging
import os
import uuid
from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from app.core.config import DATA_DIR
from app.db.models import Dataset
from app.db.session import get_session

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/datasets", tags=["datasets"])

STORAGE_PATH = Path(os.environ.get("RESEARCHLAB_STORAGE", str(DATA_DIR / "storage")))
MAX_SIZE = int(os.environ.get("RESEARCHLAB_MAX_UPLOAD_MB", "100")) * 1024 * 1024


@router.get("", response_model=dict)
async def list_datasets(skip: int = 0, limit: int = 50, db: AsyncSession = Depends(get_session)) -> dict:
    total = (await db.execute(select(func.count()).select_from(Dataset))).scalar_one()
    stmt = select(Dataset).order_by(Dataset.created_at.desc()).offset(skip).limit(limit)
    result = await db.execute(stmt)
    items = result.scalars().all()
    return {
        "items": [{
            "id": str(i.id),
            "name": i.name,
            "description": i.description,
            "filename": i.filename,
            "file_format": i.file_format,
            "checksum": i.checksum,
            "size_bytes": i.size_bytes,
            "created_at": i.created_at.isoformat() if i.created_at else None,
        } for i in items],
        "total": total,
        "skip": skip,
        "limit": limit,
    }


@router.post("", response_model=dict, status_code=201)
async def upload_dataset(
    name: str,
    file_format: str,
    description: str | None = None,
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_session),
) -> dict:
    if file.filename is None:
        raise HTTPException(status_code=400, detail="Filename is required")

    content = await file.read()
    if len(content) > MAX_SIZE:
        raise HTTPException(status_code=413, detail=f"File exceeds maximum size of {MAX_SIZE // 1024 // 1024} MB")

    checksum = hashlib.sha256(content).hexdigest()
    STORAGE_PATH.mkdir(parents=True, exist_ok=True)
    safe_name = Path(file.filename).name.replace("/", "_").replace("\\", "_")
    dest = STORAGE_PATH / f"{uuid.uuid4().hex}_{safe_name}"
    dest.write_bytes(content)

    dataset = Dataset(
        name=name,
        description=description,
        filename=safe_name,
        file_format=file_format,
        checksum=checksum,
        size_bytes=len(content),
    )
    db.add(dataset)
    await db.commit()
    await db.refresh(dataset)
    return {
        "id": str(dataset.id),
        "name": dataset.name,
        "filename": dataset.filename,
        "checksum": dataset.checksum,
        "size_bytes": dataset.size_bytes,
    }


@router.delete("/{dataset_id}", status_code=204)
async def delete_dataset(dataset_id: uuid.UUID, db: AsyncSession = Depends(get_session)) -> None:
    stmt = select(Dataset).where(Dataset.id == dataset_id)
    result = await db.execute(stmt)
    ds = result.scalar_one_or_none()
    if not ds:
        raise HTTPException(status_code=404, detail="Dataset not found")
    (STORAGE_PATH / ds.filename).unlink(missing_ok=True)
    await db.delete(ds)
    await db.commit()
