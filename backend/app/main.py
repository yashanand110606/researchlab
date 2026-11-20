"""FastAPI application entry point."""
from __future__ import annotations

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.router import router as v1_router
from app.core.config import get_settings
from app.core.exceptions import ResearchLabError, validation_exception_handler, generic_exception_handler, researchlab_exception_handler  # noqa: F401
from app.core.logging import setup_logging
from app.security import RateLimiter, RateLimitMiddleware, SecurityHeadersMiddleware
from app.experiments.registry import list_experiment_types

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    settings = get_settings()
    setup_logging(debug=settings.debug)
    logger.info("ResearchLab starting — experiment types: %s", list_experiment_types())
    yield
    logger.info("ResearchLab shutting down")


app = FastAPI(
    title="ResearchLab",
    description="Scientific Experiment Orchestration Platform",
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    lifespan=lifespan,
)

settings = get_settings()

# Security headers middleware
app.add_middleware(SecurityHeadersMiddleware)

# CORS middleware - restrict to configured origins only
cors_origins = settings.cors_origins or ["http://localhost:5173"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PATCH", "DELETE"],
    allow_headers=["Content-Type", "Authorization"],
)

# Rate limiting middleware
if settings.rate_limit_enabled:
    limiter = RateLimiter(
        max_requests=settings.rate_limit_requests,
        window_seconds=settings.rate_limit_window,
    )
    app.add_middleware(RateLimitMiddleware, limiter=limiter)

app.include_router(v1_router)
app.add_exception_handler(ResearchLabError, researchlab_exception_handler)
app.add_exception_handler(Exception, generic_exception_handler)