"""Offline metadata unit tests for SQLAlchemy 2.0 domain models.

Validates that all 20 domain models, their tables, columns, foreign keys,
constraints, JSONB columns, and ORM relationship mappings configure properly
in memory without requiring a live database or SQLite.
"""

import pytest
from sqlalchemy import CheckConstraint, UniqueConstraint
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import configure_mappers

from app.models import (
    Base,
    BuyerDemand,
    BuyerProfile,
    Crop,
    FarmerProfile,
    FPO,
    FPOMembership,
    Grievance,
    Logistics,
    Lot,
    MarketPrice,
    Match,
    Negotiation,
    Offer,
    Order,
    OrderLotAllocation,
    PaymentRecord,
    PincodeCoordinate,
    PricePrediction,
    SaleIntent,
    User,
)

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

ALL_MODELS = [
    User,
    FarmerProfile,
    BuyerProfile,
    FPO,
    FPOMembership,
    Crop,
    Lot,
    SaleIntent,
    MarketPrice,
    PricePrediction,
    PincodeCoordinate,
    BuyerDemand,
    Match,
    Offer,
    Negotiation,
    Order,
    OrderLotAllocation,
    Logistics,
    PaymentRecord,
    Grievance,
]


def test_mapper_configuration_succeeds():
    """Verify that SQLAlchemy mapper registry configures all 20 models without errors."""
    # configure_mappers() validates all relationships, backrefs, and FK targets
    configure_mappers()


def test_table_count_and_names():
    """Base.metadata must discover exactly 20 application domain tables."""
    registered_tables = set(Base.metadata.tables.keys())
    assert registered_tables == EXPECTED_TABLES
    assert len(registered_tables) == 20


def test_all_models_subclass_base():
    """Every domain entity must inherit from Base."""
    for model in ALL_MODELS:
        assert issubclass(model, Base), f"{model.__name__} does not subclass Base"


def test_primary_keys():
    """Verify primary key naming and structure across models."""
    for model in ALL_MODELS:
        table = model.__table__
        pk_cols = [c.name for c in table.primary_key.columns]
        if model is PincodeCoordinate:
            assert pk_cols == ["pincode"]
        else:
            assert pk_cols == ["id"]


def test_lot_ownership_check_constraint():
    """Verify that the Lot model contains the approved mutual exclusion check constraint."""
    table = Lot.__table__
    constraint_names = {c.name for c in table.constraints if isinstance(c, CheckConstraint)}
    assert "chk_lot_ownership" in constraint_names
    assert "chk_lot_quantity_positive" in constraint_names

    chk = next(c for c in table.constraints if c.name == "chk_lot_ownership")
    # Verify the check expression requires either farmer_user_id or fpo_id
    expr = str(chk.sqltext)
    assert "farmer_user_id IS NOT NULL" in expr
    assert "fpo_id IS NOT NULL" in expr


def test_buyer_demand_jsonb_and_constraints():
    """Verify BuyerDemand uses PostgreSQL JSONB for acceptable_grades and has quantity/budget checks."""
    table = BuyerDemand.__table__
    grade_col = table.c.acceptable_grades
    assert isinstance(grade_col.type, JSONB)

    constraint_names = {c.name for c in table.constraints if isinstance(c, CheckConstraint)}
    assert "chk_buyer_demand_quantity_positive" in constraint_names
    assert "chk_buyer_demand_budget_positive" in constraint_names


def test_fpo_membership_unique_constraint():
    """FPOMembership must enforce uniqueness on (fpo_id, farmer_user_id)."""
    table = FPOMembership.__table__
    unique_constraints = [c for c in table.constraints if isinstance(c, UniqueConstraint)]
    col_sets = [{col.name for col in uc.columns} for uc in unique_constraints]
    assert {"fpo_id", "farmer_user_id"} in col_sets


def test_match_unique_and_checks():
    """Match table must enforce uniqueness on (buyer_demand_id, sale_intent_id) and check constraints."""
    table = Match.__table__
    unique_constraints = [c for c in table.constraints if isinstance(c, UniqueConstraint)]
    col_sets = [{col.name for col in uc.columns} for uc in unique_constraints]
    assert {"buyer_demand_id", "sale_intent_id"} in col_sets

    check_names = {c.name for c in table.constraints if isinstance(c, CheckConstraint)}
    assert "chk_match_score_range" in check_names
    assert "chk_match_distance_positive" in check_names


def test_order_lot_allocation_constraints():
    """OrderLotAllocation must enforce composite unique constraint and positive allocations."""
    table = OrderLotAllocation.__table__
    unique_constraints = [c for c in table.constraints if isinstance(c, UniqueConstraint)]
    col_sets = [{col.name for col in uc.columns} for uc in unique_constraints]
    assert {"order_id", "lot_id"} in col_sets

    check_names = {c.name for c in table.constraints if isinstance(c, CheckConstraint)}
    assert "chk_allocation_quantity_positive" in check_names
    assert "chk_allocation_share_positive" in check_names


def test_cascade_delete_protection_on_critical_entities():
    """Verify RESTRICT on critical financial, lot, order, and grievance records."""
    # Lot: Restrict on farmer and crop
    lot_fks = {fk.column.table.name: fk.ondelete for fk in Lot.__table__.foreign_keys}
    assert lot_fks.get("users") == "RESTRICT"
    assert lot_fks.get("crops") == "RESTRICT"

    # Order: Restrict on buyer and seller
    order_fks = {fk.parent.name: (fk.column.table.name, fk.ondelete) for fk in Order.__table__.foreign_keys}
    assert order_fks["buyer_id"] == ("users", "RESTRICT")
    assert order_fks["seller_id"] == ("users", "RESTRICT")
    assert order_fks["offer_id"] == ("offers", "RESTRICT")

    # OrderLotAllocation: Restrict on lot and farmer, cascade on order
    alloc_fks = {fk.parent.name: (fk.column.table.name, fk.ondelete) for fk in OrderLotAllocation.__table__.foreign_keys}
    assert alloc_fks["order_id"] == ("orders", "CASCADE")
    assert alloc_fks["lot_id"] == ("lots", "RESTRICT")
    assert alloc_fks["farmer_user_id"] == ("users", "RESTRICT")

    # PaymentRecord: Restrict on order
    pmt_fks = {fk.parent.name: (fk.column.table.name, fk.ondelete) for fk in PaymentRecord.__table__.foreign_keys}
    assert pmt_fks["order_id"] == ("orders", "RESTRICT")

    # Grievance: Restrict on order and filed_by_user
    grievance_fks = {fk.parent.name: (fk.column.table.name, fk.ondelete) for fk in Grievance.__table__.foreign_keys}
    assert grievance_fks["order_id"] == ("orders", "RESTRICT")
    assert grievance_fks["filed_by_user_id"] == ("users", "RESTRICT")


def test_sale_intent_check_constraints():
    """Verify SaleIntent check constraints for price bounds, positive minimum price, and date order."""
    table = SaleIntent.__table__
    check_names = {c.name for c in table.constraints if isinstance(c, CheckConstraint)}
    assert "chk_sale_intent_price_bounds" in check_names
    assert "chk_sale_intent_min_price_positive" in check_names
    assert "chk_sale_intent_date_bounds" in check_names


def test_market_price_constraints():
    """Verify MarketPrice min/max spread and positive price constraints."""
    table = MarketPrice.__table__
    check_names = {c.name for c in table.constraints if isinstance(c, CheckConstraint)}
    assert "chk_market_price_spread" in check_names
    assert "chk_market_price_positive" in check_names
