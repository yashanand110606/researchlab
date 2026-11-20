"""Centralized exception definitions and handlers."""
from __future__ import annotations

import logging
from http import HTTPStatus
from typing import Any

from fastapi import Request
from fastapi.responses import JSONResponse
from pydantic import ValidationError

logger = logging.getLogger(__name__)


class ResearchLabError(Exception):
    """Base exception for all ResearchLab domain errors."""

    def __init__(self, message: str, status_code: int = HTTPStatus.BAD_REQUEST):
        super().__init__(message)
        self.message = message
        self.status_code = status_code


class NotFoundError(ResearchLabError):
    def __init__(self, resource: str, identifier: str):
        super().__init__(f"{resource} '{identifier}' not found", HTTPStatus.NOT_FOUND)


class ConflictError(ResearchLabError):
    def __init__(self, message: str):
        super().__init__(message, HTTPStatus.CONFLICT)


class ValidationErrorDetail(ResearchLabError):
    def __init__(self, detail: list[dict[str, Any]]):
        super().__init__("Configuration validation failed", HTTPStatus.UNPROCESSABLE_ENTITY)
        self.detail = detail


async def researchlab_exception_handler(_: Request, exc: ResearchLabError) -> JSONResponse:
    logger.warning("ResearchLab error: %s (status=%d)", exc.message, exc.status_code)
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.message},
    )


async def validation_exception_handler(_: Request, exc: ValidationError) -> JSONResponse:
    details = exc.errors()
    return JSONResponse(
        status_code=HTTPStatus.UNPROCESSABLE_ENTITY,
        content={"detail": "Validation error", "errors": details},
    )


async def generic_exception_handler(_: Request, exc: Exception) -> JSONResponse:
    logger.exception("Unhandled exception: %s", exc)
    return JSONResponse(
        status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
        content={"detail": "An internal server error occurred"},
    )
