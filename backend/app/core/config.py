"""Application configuration and environment settings.

Provides strongly typed settings using Pydantic, with support for local
environment variables and an optional .env file.
"""

from functools import lru_cache
import json
import os
from pathlib import Path
from typing import Any, List, Union
from pydantic import BaseModel, Field, field_validator


def _load_env_file() -> None:
    """Load key-value pairs from an optional local .env file if present.

    Avoids external dependencies like python-dotenv during early scaffolding,
    while allowing standard environment variable configuration.
    """
    candidates = [
        Path.cwd() / ".env",
        Path.cwd() / "backend" / ".env",
        Path(__file__).resolve().parent.parent.parent / ".env",
    ]
    for env_path in candidates:
        if env_path.is_file():
            try:
                with open(env_path, "r", encoding="utf-8") as f:
                    for line in f:
                        line = line.strip()
                        if not line or line.startswith("#") or "=" not in line:
                            continue
                        key, val = line.split("=", 1)
                        key = key.strip()
                        val = val.strip().strip("'\"")
                        if key and key not in os.environ:
                            os.environ[key] = val
                break
            except Exception:
                # If reading fails, fallback gracefully to existing environment
                pass


_load_env_file()


class Settings(BaseModel):
    """Application settings schema with sensible local development defaults."""

    PROJECT_NAME: str = Field(
        default="Kisan BhavSaathi API",
        description="Application title shown in documentation",
    )
    VERSION: str = Field(
        default="0.1.0",
        description="Semantic application version",
    )
    DESCRIPTION: str = Field(
        default="Backend API for Kisan BhavSaathi — SIH 2026 agricultural market platform",
        description="High-level API description",
    )
    ENVIRONMENT: str = Field(
        default="development",
        description="Deployment environment: 'development', 'staging', or 'production'",
    )
    DEBUG: bool = Field(
        default=True,
        description="Enable debug mode and verbose logging in development",
    )
    HOST: str = Field(
        default="127.0.0.1",
        description="Server bind address for local execution",
    )
    PORT: int = Field(
        default=8000,
        description="Server bind port",
    )
    API_V1_PREFIX: str = Field(
        default="/api/v1",
        description="URL prefix for version 1 API routes",
    )
    LOG_LEVEL: str = Field(
        default="INFO",
        description="Logging level: DEBUG, INFO, WARNING, ERROR, CRITICAL",
    )

    # CORS configuration
    # Conservative local development defaults. In production, exact domain origins
    # (e.g. 'https://admin.kisanbhavsaathi.in') must be specified in the environment.
    CORS_ORIGINS: List[str] = Field(
        default=[
            "http://localhost:3000",
            "http://localhost:5173",
            "http://127.0.0.1:3000",
            "http://127.0.0.1:5173",
        ],
        description="Allowed Cross-Origin Resource Sharing (CORS) origins",
    )

    # Database configuration (PostgreSQL)
    # Default is a local development placeholder; production must provide a real DATABASE_URL.
    DATABASE_URL: str = Field(
        default="postgresql+psycopg2://postgres:postgres@localhost:5432/kisan_bhavsaathi_dev",
        description="PostgreSQL database connection URL (postgresql+psycopg2://...)",
    )
    DB_POOL_SIZE: int = Field(
        default=5,
        description="Persistent connection pool size for SQLAlchemy",
    )
    DB_MAX_OVERFLOW: int = Field(
        default=10,
        description="Maximum temporary connections allowed beyond pool_size",
    )
    DB_POOL_TIMEOUT: int = Field(
        default=30,
        description="Seconds to wait before raising pool timeout error",
    )
    DB_POOL_RECYCLE: int = Field(
        default=1800,
        description="Seconds before recycling persistent connections (30 minutes)",
    )
    DB_POOL_PRE_PING: bool = Field(
        default=True,
        description="Verify connection liveness with a ping before handing out",
    )

    @property
    def masked_database_url(self) -> str:
        """Return the database URL with the password sanitized for safe logging."""
        try:
            from sqlalchemy.engine import make_url
            url = make_url(self.DATABASE_URL)
            return url.render_as_string(hide_password=True)
        except Exception:
            return "postgresql+psycopg2://***"

    @field_validator("CORS_ORIGINS", mode="before")
    @classmethod
    def parse_cors_origins(cls, value: Any) -> List[str]:
        """Support comma-separated strings or JSON arrays from environment variables."""
        if isinstance(value, str):
            value = value.strip()
            if value.startswith("[") and value.endswith("]"):
                try:
                    return json.loads(value)
                except Exception:
                    pass
            return [origin.strip() for origin in value.split(",") if origin.strip()]
        if isinstance(value, list):
            return [str(v).strip() for v in value if str(v).strip()]
        return value

    @classmethod
    def load_from_env(cls) -> "Settings":
        """Instantiate Settings reading overrides from os.environ."""
        kwargs: dict[str, Any] = {}
        if "PROJECT_NAME" in os.environ:
            kwargs["PROJECT_NAME"] = os.environ["PROJECT_NAME"]
        if "VERSION" in os.environ:
            kwargs["VERSION"] = os.environ["VERSION"]
        if "DESCRIPTION" in os.environ:
            kwargs["DESCRIPTION"] = os.environ["DESCRIPTION"]
        if "ENVIRONMENT" in os.environ:
            kwargs["ENVIRONMENT"] = os.environ["ENVIRONMENT"]
        if "DEBUG" in os.environ:
            kwargs["DEBUG"] = os.environ["DEBUG"].lower() in ("true", "1", "yes")
        if "HOST" in os.environ:
            kwargs["HOST"] = os.environ["HOST"]
        if "PORT" in os.environ:
            kwargs["PORT"] = int(os.environ["PORT"])
        if "API_V1_PREFIX" in os.environ:
            kwargs["API_V1_PREFIX"] = os.environ["API_V1_PREFIX"]
        if "LOG_LEVEL" in os.environ:
            kwargs["LOG_LEVEL"] = os.environ["LOG_LEVEL"].upper()
        if "CORS_ORIGINS" in os.environ:
            kwargs["CORS_ORIGINS"] = os.environ["CORS_ORIGINS"]
        if "DATABASE_URL" in os.environ:
            kwargs["DATABASE_URL"] = os.environ["DATABASE_URL"]
        if "DB_POOL_SIZE" in os.environ:
            kwargs["DB_POOL_SIZE"] = int(os.environ["DB_POOL_SIZE"])
        if "DB_MAX_OVERFLOW" in os.environ:
            kwargs["DB_MAX_OVERFLOW"] = int(os.environ["DB_MAX_OVERFLOW"])
        if "DB_POOL_TIMEOUT" in os.environ:
            kwargs["DB_POOL_TIMEOUT"] = int(os.environ["DB_POOL_TIMEOUT"])
        if "DB_POOL_RECYCLE" in os.environ:
            kwargs["DB_POOL_RECYCLE"] = int(os.environ["DB_POOL_RECYCLE"])
        if "DB_POOL_PRE_PING" in os.environ:
            kwargs["DB_POOL_PRE_PING"] = os.environ["DB_POOL_PRE_PING"].lower() in ("true", "1", "yes")

        return cls(**kwargs)



@lru_cache
def get_settings() -> Settings:
    """Return cached application settings singleton."""
    return Settings.load_from_env()
