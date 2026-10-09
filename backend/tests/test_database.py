"""Unit tests for PostgreSQL settings, SQLAlchemy engine configuration, and session lifecycle.

These tests verify configuration and offline invariants without requiring a live
PostgreSQL instance and without substituting with SQLite.
"""

import pytest
from sqlalchemy.orm import Session
from app.core.config import Settings, get_settings
from app.core.database import SessionLocal, check_db_connectivity, engine, get_db


def test_database_settings_defaults() -> None:
    """Verify default PostgreSQL settings and connection pool parameters."""
    settings = get_settings()

    assert settings.DATABASE_URL.startswith("postgresql+psycopg2://")
    assert settings.DB_POOL_SIZE == 5
    assert settings.DB_MAX_OVERFLOW == 10
    assert settings.DB_POOL_TIMEOUT == 30
    assert settings.DB_POOL_RECYCLE == 1800
    assert settings.DB_POOL_PRE_PING is True


def test_masked_database_url_hides_password() -> None:
    """Verify that masked_database_url masks credentials properly."""
    custom_settings = Settings(
        DATABASE_URL="postgresql+psycopg2://custom_user:super_secret_password@localhost:5432/my_db"
    )
    masked = custom_settings.masked_database_url

    assert "super_secret_password" not in masked
    assert "custom_user:***" in masked or ":***@" in masked
    assert "localhost:5432/my_db" in masked


def test_engine_pool_configuration() -> None:
    """Verify SQLAlchemy 2.0 Engine is configured with conservative pool settings."""
    assert engine.dialect.name == "postgresql"
    assert engine.pool.size() == 5
    assert engine.pool._max_overflow == 10
    assert engine.pool._recycle == 1800
    assert engine.pool._pre_ping is True


def test_get_db_session_lifecycle() -> None:
    """Verify the get_db generator yields a Session and safely closes it on exit."""
    session_generator = get_db()
    session = next(session_generator)

    try:
        assert isinstance(session, Session)
        assert session.bind == engine
    finally:
        # Closing generator triggers finally block
        with pytest.raises(StopIteration):
            next(session_generator)


def test_check_db_connectivity_contract() -> None:
    """Verify check_db_connectivity returns a structured report without exposing secrets."""
    report = check_db_connectivity(timeout_seconds=0.5)

    assert "connected" in report
    assert isinstance(report["connected"], bool)
    assert "database_url" in report
    assert "dialect" in report
    assert report["dialect"] == "postgresql"
    assert "postgres:postgres" not in report["database_url"]  # Masked

    if not report["connected"]:
        assert "error" in report
        assert isinstance(report["error"], str)
