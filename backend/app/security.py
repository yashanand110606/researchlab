"""Security middleware: rate limiting, security headers, input sanitization."""
from __future__ import annotations

import hashlib
import hmac
import logging
import time
from collections import defaultdict
from typing import Any

from fastapi import Request, Response
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

logger = logging.getLogger(__name__)


class RateLimiter:
    """Simple in-memory rate limiter (sliding window)."""

    def __init__(self, max_requests: int = 100, window_seconds: int = 60):
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self._requests: dict[str, list[float]] = defaultdict(list)

    def check(self, key: str) -> bool:
        now = time.time()
        window_start = now - self.window_seconds
        self._requests[key] = [t for t in self._requests[key] if t > window_start]
        if len(self._requests[key]) >= self.max_requests:
            return False
        self._requests[key].append(now)
        return True


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """Add security headers to all responses."""

    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response.headers["Permissions-Policy"] = "geolocation=(), microphone=(), camera=()"
        response.headers["Cache-Control"] = "no-store, max-age=0"
        response.headers["Content-Security-Policy"] = "default-src 'self'; script-src 'self'; style-src 'self' 'unsafe-inline'"
        return response


class RateLimitMiddleware(BaseHTTPMiddleware):
    """Rate limiting middleware."""

    def __init__(self, app, limiter: RateLimiter):
        super().__init__(app)
        self.limiter = limiter

    async def dispatch(self, request: Request, call_next):
        # Skip rate limiting for health endpoints
        if request.url.path in ("/api/v1/health", "/api/v1/ready", "/docs", "/redoc", "/openapi.json"):
            return await call_next(request)

        client_ip = request.client.host if request.client else "unknown"
        if not self.limiter.check(client_ip):
            return JSONResponse(
                status_code=429,
                content={"detail": "Too many requests. Please try again later."},
                headers={"Retry-After": "60"},
            )
        return await call_next(request)


def sanitize_input(value: Any) -> Any:
    """Recursively sanitize input strings to prevent XSS."""
    if isinstance(value, str):
        # Remove dangerous characters
        cleaned = value.replace("<", "").replace(">", "").replace("&", "").replace('"', "").replace("'", "")
        return cleaned.strip()
    if isinstance(value, dict):
        return {k: sanitize_input(v) for k, v in value.items()}
    if isinstance(value, list):
        return [sanitize_input(v) for v in value]
    return value


def verify_password_hash(password: str, stored_hash: str) -> bool:
    """Verify a password against a stored hash."""
    return hmac.compare_digest(
        hashlib.sha256(password.encode()).hexdigest(),
        stored_hash,
    )


def hash_password(password: str) -> str:
    """Hash a password for storage."""
    return hashlib.sha256(password.encode()).hexdigest()