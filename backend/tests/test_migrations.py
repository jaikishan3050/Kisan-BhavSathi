"""Offline unit tests for Alembic configuration and migration metadata.

Verifies that Alembic can load its configuration, resolve the migration script
directory, discover all 20 domain tables in target_metadata, and that the initial
migration revision defines the required tables, enums, constraints, and cascades
without opening a database connection or using SQLite.
"""

import importlib.util
from pathlib import Path
import pytest
from alembic.config import Config
from alembic.script import ScriptDirectory
from app.models import Base
from app.models.enums import ALL_ENUMS

BACKEND_DIR = Path(__file__).resolve().parent.parent
ALEMBIC_INI_PATH = BACKEND_DIR / "alembic.ini"
VERSIONS_DIR = BACKEND_DIR / "alembic" / "versions"
INITIAL_REVISION_FILE = VERSIONS_DIR / "711f7a9575e0_initial_relational_schema.py"

EXPECTED_TABLES = {
    "users",
    "farmer_profiles",
    "buyer_profiles",
    "fpos",
    "fpo_memberships",
    "crops",
    "lots",
    "sale_intents",
    "market_prices",
    "price_predictions",
    "pincode_coordinates",
    "buyer_demands",
    "matches",
    "offers",
    "negotiations",
    "orders",
    "order_lot_allocations",
    "logistics",
    "payment_records",
    "grievances",
}


def test_alembic_config_loads_and_finds_scripts():
    """Verify Alembic configuration file loads and locates the migration directory."""
    assert ALEMBIC_INI_PATH.is_file(), f"alembic.ini missing at {ALEMBIC_INI_PATH}"
    config = Config(str(ALEMBIC_INI_PATH))

    # Verify script directory resolution
    script_dir = ScriptDirectory.from_config(config)
    assert Path(script_dir.dir).resolve() == (BACKEND_DIR / "alembic").resolve()


def test_target_metadata_includes_all_20_tables():
    """Verify target_metadata contains all 20 canonical application tables."""
    metadata_tables = set(Base.metadata.tables.keys())
    assert metadata_tables == EXPECTED_TABLES
    assert len(metadata_tables) == 20


def test_initial_revision_metadata():
    """Verify initial revision exists, has valid revision ID, and no down_revision."""
    config = Config(str(ALEMBIC_INI_PATH))
    script_dir = ScriptDirectory.from_config(config)

    head_rev = script_dir.get_current_head()
    assert head_rev == "711f7a9575e0"

    script = script_dir.get_revision(head_rev)
    assert script is not None
    assert script.revision == "711f7a9575e0"
    assert script.down_revision is None
    assert "initial_relational_schema" in (script.doc or "")


def test_migration_module_import_and_callables():
    """Verify the migration module imports cleanly and exposes upgrade and downgrade."""
    assert INITIAL_REVISION_FILE.is_file()

    spec = importlib.util.spec_from_file_location("initial_migration", INITIAL_REVISION_FILE)
    assert spec is not None and spec.loader is not None

    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    assert hasattr(module, "upgrade") and callable(module.upgrade)
    assert hasattr(module, "downgrade") and callable(module.downgrade)
    assert module.revision == "711f7a9575e0"
    assert module.down_revision is None

    # Verify all 22 enum definitions exist on the module
    for enum_cls in ALL_ENUMS:
        enum_var_name = f"{enum_cls.__pg_enum_name__}_enum"
        assert hasattr(module, enum_var_name), f"Missing {enum_var_name} in migration"


def test_migration_content_verifies_tables_and_constraints():
    """Verify source code of initial migration includes all 20 tables, constraints, and cascades."""
    content = INITIAL_REVISION_FILE.read_text(encoding="utf-8")

    # 1. Verify all 20 tables are created
    for table_name in EXPECTED_TABLES:
        assert f"op.create_table(\n        '{table_name}'" in content or f"'{table_name}'" in content
        assert f"op.drop_table('{table_name}')" in content

    # 2. Verify all 22 enums are created in upgrade and dropped in downgrade
    for enum_cls in ALL_ENUMS:
        pg_name = enum_cls.__pg_enum_name__
        assert f"{pg_name}_enum.create(op.get_bind(), checkfirst=True)" in content
        assert f"{pg_name}_enum.drop(op.get_bind(), checkfirst=True)" in content

    # 3. Verify key constraints
    assert "chk_lot_ownership" in content
    assert "chk_lot_quantity_positive" in content
    assert "chk_sale_intent_price_bounds" in content
    assert "chk_buyer_demand_quantity_positive" in content
    assert "chk_match_score_range" in content
    assert "chk_offer_price_positive" in content
    assert "chk_order_price_positive" in content
    assert "chk_allocation_quantity_positive" in content

    # 4. Verify unique constraints
    assert "uq_fpo_membership_farmer" in content
    assert "uq_match_demand_intent" in content
    assert "uq_order_lot_allocation" in content

    # 5. Verify JSONB mapping
    assert "postgresql.JSONB" in content

    # 6. Verify RESTRICT and CASCADE on critical foreign keys
    assert "ondelete='RESTRICT'" in content
    assert "ondelete='CASCADE'" in content
    assert "ondelete='SET NULL'" in content
