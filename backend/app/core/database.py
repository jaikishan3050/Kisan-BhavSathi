"""SQLAlchemy 2.0 database engine, session factory, and connectivity verification.

Step 4A Foundation: Configures the PostgreSQL connection pool and provides
the FastAPI dependency for managing session lifecycles.
"""

from typing import Any, Dict, Generator
import time
from sqlalchemy import create_engine, text
from sqlalchemy.orm import Session, sessionmaker
from app.core.config import get_settings
from app.core.logging import get_logger

logger = get_logger("app.core.database")


def get_engine():
    """Create and return a configured SQLAlchemy 2.0 Engine."""
    settings = get_settings()
    return create_engine(
        settings.DATABASE_URL,
        pool_size=settings.DB_POOL_SIZE,
        max_overflow=settings.DB_MAX_OVERFLOW,
        pool_timeout=settings.DB_POOL_TIMEOUT,
        pool_recycle=settings.DB_POOL_RECYCLE,
        pool_pre_ping=settings.DB_POOL_PRE_PING,
    )


# Module-level engine and sessionmaker
# Note: SQLAlchemy does NOT connect to PostgreSQL at engine initialization time.
# Connection occurs only when a session or connection is explicitly checked out.
engine = get_engine()

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)


def get_db() -> Generator[Session, None, None]:
    """FastAPI dependency for obtaining and safely closing a database session.

    Yields:
        Session: Active SQLAlchemy session instance.

    Guarantees:
        The session is guaranteed to close upon completion of the request.
    """
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()


def check_db_connectivity(timeout_seconds: float = 3.0) -> Dict[str, Any]:
    """Perform a safe, non-destructive check of database connectivity.

    Executes a simple 'SELECT 1' test query.
    Never exposes passwords or sensitive credentials in the result.

    Args:
        timeout_seconds: Maximum time to wait for a response.

    Returns:
        dict: Summary containing connection status, latency, dialect, and sanitized URL.
    """
    settings = get_settings()
    masked_url = settings.masked_database_url
    result: Dict[str, Any] = {
        "connected": False,
        "database_url": masked_url,
        "dialect": engine.dialect.name,
    }

    try:
        start_time = time.perf_counter()
        # Connect and execute a trivial query with timeout
        with engine.connect() as conn:
            conn.execution_options(timeout=timeout_seconds).execute(text("SELECT 1"))
        elapsed_ms = (time.perf_counter() - start_time) * 1000.0

        result["connected"] = True
        result["latency_ms"] = round(elapsed_ms, 2)
        result["message"] = "PostgreSQL connection successfully verified."
        logger.info("Database connectivity check passed (%s ms) [%s]", result["latency_ms"], masked_url)
    except Exception as exc:
        result["connected"] = False
        # Sanitize error message to ensure no connection credentials leak
        raw_msg = str(exc)
        # Strip potential password strings if embedded in raw exception text
        safe_msg = raw_msg.split("@")[-1] if "@" in raw_msg else raw_msg
        result["error"] = f"Connection failed: {safe_msg.strip()}"
        logger.warning("Database connectivity check failed for [%s]: %s", masked_url, result["error"])

    return result


if __name__ == "__main__":
    import json

    print("Running explicit database connectivity check...")
    report = check_db_connectivity()
    print(json.dumps(report, indent=2))
