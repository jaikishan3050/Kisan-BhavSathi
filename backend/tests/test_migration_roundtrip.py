"""Automated PostgreSQL migration round-trip tests with strict safety guards.

Enforces that migration execution is strictly limited to the dedicated test database
'kisan_bhavsaathi_test', completely prohibiting execution against 'kisan_bhavsaathi_dev'
or any other database. Tests run offline if the dedicated test database is unavailable.
"""

import os
from pathlib import Path
from urllib.parse import urlparse, urlunparse
import pytest
from alembic import command
from alembic.config import Config
import psycopg2
from app.core.config import get_settings
from app.models.enums import ALL_ENUMS

BACKEND_DIR = Path(__file__).resolve().parent.parent
ALEMBIC_INI_PATH = BACKEND_DIR / "alembic.ini"
REQUIRED_TEST_DB_NAME = "kisan_bhavsaathi_test"

EXPECTED_TABLES = {
    "crops",
    "pincode_coordinates",
    "users",
    "buyer_demands",
    "buyer_profiles",
    "farmer_profiles",
    "fpos",
    "market_prices",
    "fpo_memberships",
    "lots",
    "price_predictions",
    "sale_intents",
    "matches",
    "offers",
    "negotiations",
    "orders",
    "grievances",
    "logistics",
    "order_lot_allocations",
    "payment_records",
}


def validate_and_mask_test_db_url(url: str | None) -> tuple[str, str]:
    """Validate that the target URL points strictly to kisan_bhavsaathi_test.

    Aborts immediately if the URL is missing, malformed, uses an unsupported
    dialect (e.g. SQLite), or targets any database other than kisan_bhavsaathi_test.
    Never prints or leaks credentials.
    """
    if not url:
        raise ValueError("Safety Guard Abort: Target database URL is empty or not configured.")

    parsed = urlparse(url)
    scheme = parsed.scheme.split("+")[0]
    if scheme != "postgresql":
        raise ValueError(
            f"Safety Guard Abort: Unsupported database dialect '{parsed.scheme}'. "
            "Only PostgreSQL is permitted; SQLite is strictly prohibited."
        )

    db_name = parsed.path.lstrip("/")
    if db_name != REQUIRED_TEST_DB_NAME:
        raise ValueError(
            f"Safety Guard Abort: Migration round-trip tests are strictly restricted to "
            f"'{REQUIRED_TEST_DB_NAME}'. Received '{db_name}'. "
            "Execution against the development database or any other database is blocked."
        )

    masked_url = (
        f"{parsed.scheme}://{parsed.username}:***@{parsed.hostname}:{parsed.port}/{db_name}"
    )
    return url, masked_url


def is_database_reachable(url: str) -> bool:
    """Check if the target database can accept connections without raising unhandled errors."""
    parsed = urlparse(url)
    try:
        conn = psycopg2.connect(
            dbname=parsed.path.lstrip("/"),
            user=parsed.username,
            password=parsed.password,
            host=parsed.hostname,
            port=parsed.port or 5432,
            connect_timeout=2,
        )
        conn.close()
        return True
    except (psycopg2.OperationalError, Exception):
        return False


def test_safety_guard_rejects_development_database():
    """Verify that the safety guard blocks execution against kisan_bhavsaathi_dev."""
    dev_url = "postgresql+psycopg2://postgres:secret@localhost:5432/kisan_bhavsaathi_dev"
    with pytest.raises(ValueError, match="Safety Guard Abort"):
        validate_and_mask_test_db_url(dev_url)


def test_safety_guard_rejects_arbitrary_databases():
    """Verify that the safety guard blocks execution against production or arbitrary databases."""
    prod_url = "postgresql+psycopg2://postgres:secret@localhost:5432/production_master"
    with pytest.raises(ValueError, match="Safety Guard Abort"):
        validate_and_mask_test_db_url(prod_url)


def test_safety_guard_rejects_sqlite():
    """Verify that the safety guard strictly prohibits SQLite."""
    sqlite_url = "sqlite:///kisan_bhavsaathi_test.db"
    with pytest.raises(ValueError, match="SQLite is strictly prohibited"):
        validate_and_mask_test_db_url(sqlite_url)


def test_safety_guard_accepts_exact_test_database():
    """Verify that the safety guard accepts the required test database URL."""
    valid_test_url = "postgresql+psycopg2://postgres:secret@localhost:5432/kisan_bhavsaathi_test"
    clean_url, masked_url = validate_and_mask_test_db_url(valid_test_url)
    assert clean_url == valid_test_url
    assert masked_url == "postgresql+psycopg2://postgres:***@localhost:5432/kisan_bhavsaathi_test"


def test_postgresql_migration_roundtrip():
    """Run migration round-trip test against dedicated kisan_bhavsaathi_test if reachable.

    Safely skips if kisan_bhavsaathi_test does not exist or is unreachable.
    """
    raw_test_url = os.environ.get("TEST_DATABASE_URL")
    if not raw_test_url:
        # Derive strictly by substituting the database name on the configured host
        settings = get_settings()
        parsed = urlparse(settings.DATABASE_URL)
        raw_test_url = urlunparse(parsed._replace(path=f"/{REQUIRED_TEST_DB_NAME}"))

    # Programmatic safety enforcement
    test_url, masked_url = validate_and_mask_test_db_url(raw_test_url)

    if not is_database_reachable(test_url):
        pytest.skip(
            f"Dedicated test database '{REQUIRED_TEST_DB_NAME}' [{masked_url}] "
            "is not available or does not exist on the PostgreSQL server. Preflight stopped execution."
        )

    # 1. Connect and verify clean initial state
    parsed = urlparse(test_url)
    conn = psycopg2.connect(
        dbname=REQUIRED_TEST_DB_NAME,
        user=parsed.username,
        password=parsed.password,
        host=parsed.hostname,
        port=parsed.port or 5432,
    )
    conn.autocommit = True
    cur = conn.cursor()

    cur.execute(
        "SELECT count(*) FROM information_schema.tables "
        "WHERE table_schema = 'public' AND table_type = 'BASE TABLE';"
    )
    initial_tables = cur.fetchone()[0]
    if initial_tables > 0:
        conn.close()
        pytest.fail(
            f"Preflight check failed: '{REQUIRED_TEST_DB_NAME}' already contains {initial_tables} "
            "tables. It must be in a clean empty state before running the round-trip test."
        )

    try:
        # 2. Upgrade to head
        alembic_cfg = Config(str(ALEMBIC_INI_PATH))
        alembic_cfg.set_main_option("sqlalchemy.url", test_url)
        command.upgrade(alembic_cfg, "head")

        # 3. Verify upgraded schema objects
        cur.execute(
            "SELECT table_name FROM information_schema.tables "
            "WHERE table_schema = 'public' AND table_type = 'BASE TABLE';"
        )
        created_tables = {row[0] for row in cur.fetchall()}
        assert created_tables.issuperset(EXPECTED_TABLES)
        assert "alembic_version" in created_tables

        # Verify all 22 native ENUMs exist
        cur.execute(
            "SELECT t.typname FROM pg_type t "
            "JOIN pg_namespace n ON n.oid = t.typnamespace "
            "WHERE n.nspname = 'public' AND t.typtype = 'e';"
        )
        created_enums = {row[0] for row in cur.fetchall()}
        for enum_cls in ALL_ENUMS:
            assert enum_cls.__pg_enum_name__ in created_enums

        # 4. Downgrade to base
        command.downgrade(alembic_cfg, "base")

        # 5. Verify downgrade cleanup
        cur.execute(
            "SELECT table_name FROM information_schema.tables "
            "WHERE table_schema = 'public' AND table_type = 'BASE TABLE';"
        )
        remaining_tables = {row[0] for row in cur.fetchall()}
        assert remaining_tables == set() or remaining_tables == {"alembic_version"}

        # Verify enums were dropped
        cur.execute(
            "SELECT t.typname FROM pg_type t "
            "JOIN pg_namespace n ON n.oid = t.typnamespace "
            "WHERE n.nspname = 'public' AND t.typtype = 'e';"
        )
        remaining_enums = {row[0] for row in cur.fetchall()}
        for enum_cls in ALL_ENUMS:
            assert enum_cls.__pg_enum_name__ not in remaining_enums

    finally:
        conn.close()
