"""Application configuration via environment variables."""
from __future__ import annotations

from functools import lru_cache
from pathlib import Path
from typing import Optional

from pydantic import BaseModel
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # Application
    app_name: str = "ResearchLab"
    debug: bool = False
    api_prefix: str = "/api/v1"

    # Database
    postgres_host: str = "localhost"
    postgres_port: int = 5432
    postgres_user: str = "researchlab"
    postgres_password: str = ""
    postgres_db: str = "researchlab"
    sqlalchemy_pool_size: int = 10
    sqlalchemy_max_overflow: int = 20

    # Redis / Celery
    redis_host: str = ""
    redis_port: int = 6379
    redis_db: int = 0
    celery_broker_url: str = ""
    celery_result_backend: str = ""

    # Storage
    storage_root: str = ""
    max_upload_size_mb: int = 100

    # CORS
    cors_origins: list[str] = []

    # Security
    secret_key: str = ""
    api_key: str = ""
    admin_password: str = ""
    rate_limit_enabled: bool = True
    rate_limit_requests: int = 100
    rate_limit_window: int = 60

    # Debug
    debug: bool = False

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"


class DatabaseURL(BaseModel):
    driver: str = "postgresql+psycopg"
    user: str = ""
    password: str = ""
    host: str = ""
    port: int = 5432
    dbname: str = ""

    def render(self) -> str:
        return (
            f"{self.driver}://"
            f"{self.user}:{self.password}"
            f"@{self.host}:{self.port}/{self.dbname}"
        )


@lru_cache
def get_settings() -> Settings:
    return Settings()


def get_database_url(settings: Settings | None = None) -> str:
    if settings is None:
        settings = get_settings()
    url = DatabaseURL(
        driver="postgresql+psycopg",
        user=settings.postgres_user,
        password=settings.postgres_password,
        host=settings.postgres_host,
        port=settings.postgres_port,
        dbname=settings.postgres_db,
    )
    return url.render()


DATA_DIR = Path(__file__).resolve().parents[2] / "data"
