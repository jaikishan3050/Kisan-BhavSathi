"""Focused unit tests for SQLAlchemy 2.0 Base, mixins, and PostgreSQL Enum definitions.

Step 4B.1 Verification: These tests execute purely in-memory, requiring no live
PostgreSQL instance and substituting zero SQLite databases.
"""

from datetime import datetime, timezone
import uuid
from sqlalchemy import Integer
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from app.models.base import Base, TimestampMixin, UUIDPrimaryKeyMixin, utc_now
from app.models.enums import (
    ALL_ENUMS,
    AllocationPayoutStatus,
    BuyerCategory,
    BuyerDemandStatus,
    BuyerVerificationStatus,
    CropCategory,
    DataSourceTier,
    FarmerKYCStatus,
    FPOMembershipStatus,
    GrievanceCategory,
    GrievanceStatus,
    LogisticsStatus,
    LotStatus,
    OfferStatus,
    OrderStatus,
    PaymentMethod,
    PaymentStage,
    PaymentStatus,
    QualityGrade,
    SaleIntentStatus,
    StandardUnit,
    UserRole,
    VerificationDocType,
)


def test_enum_inventory_count() -> None:
    """Verify that exactly 22 named PostgreSQL enum types are defined."""
    assert len(ALL_ENUMS) == 22


def test_user_role_values() -> None:
    """Verify UserRole enum values match Architecture Section 6.1 Item 1."""
    assert UserRole.__pg_enum_name__ == "user_role"
    expected = {"FARMER", "FPO_REPRESENTATIVE", "BUYER", "ADMIN"}
    assert {e.value for e in UserRole} == expected


def test_farmer_kyc_status_values() -> None:
    """Verify FarmerKYCStatus enum values match Architecture Section 5."""
    assert FarmerKYCStatus.__pg_enum_name__ == "farmer_kyc_status"
    expected = {"PENDING", "VERIFIED", "REJECTED"}
    assert {e.value for e in FarmerKYCStatus} == expected


def test_buyer_verification_status_values() -> None:
    """Verify BuyerVerificationStatus enum values match Architecture Section 6.1 Item 5."""
    assert BuyerVerificationStatus.__pg_enum_name__ == "buyer_verification_status"
    expected = {"PENDING", "VERIFIED", "REJECTED"}
    assert {e.value for e in BuyerVerificationStatus} == expected


def test_fpo_membership_status_values() -> None:
    """Verify FPOMembershipStatus enum values match Architecture Section 6.1 Item 4."""
    assert FPOMembershipStatus.__pg_enum_name__ == "fpo_membership_status"
    expected = {"PENDING", "ACTIVE", "REJECTED"}
    assert {e.value for e in FPOMembershipStatus} == expected


def test_buyer_category_values() -> None:
    """Verify BuyerCategory enum values match Architecture Section 6.1 Item 5."""
    assert BuyerCategory.__pg_enum_name__ == "buyer_category"
    expected = {
        "INSTITUTIONAL_PROCESSOR",
        "WHOLESALER",
        "COMMISSION_AGENT",
        "RETAILER_EXPORTER",
    }
    assert {e.value for e in BuyerCategory} == expected


def test_verification_doc_type_values() -> None:
    """Verify VerificationDocType enum values match Architecture Section 6.1 Item 5."""
    assert VerificationDocType.__pg_enum_name__ == "verification_doc_type"
    expected = {"GSTIN", "APMC_LICENSE", "FSSAI_REGISTRATION", "TRADE_LICENSE", "PAN"}
    assert {e.value for e in VerificationDocType} == expected


def test_crop_category_values() -> None:
    """Verify CropCategory enum values match Architecture Section 6.1 Item 6."""
    assert CropCategory.__pg_enum_name__ == "crop_category"
    expected = {"CEREALS", "PULSES", "OILSEEDS", "VEGETABLES", "FRUITS"}
    assert {e.value for e in CropCategory} == expected


def test_standard_unit_values() -> None:
    """Verify StandardUnit enum values match Architecture Section 6.1 Item 6."""
    assert StandardUnit.__pg_enum_name__ == "standard_unit"
    expected = {"QUINTAL", "KG"}
    assert {e.value for e in StandardUnit} == expected


def test_quality_grade_values() -> None:
    """Verify QualityGrade enum values match Architecture Section 6.1 Item 7."""
    assert QualityGrade.__pg_enum_name__ == "quality_grade"
    expected = {"GRADE_A", "GRADE_B", "GRADE_C"}
    assert {e.value for e in QualityGrade} == expected


def test_lot_status_values() -> None:
    """Verify LotStatus enum values match Architecture Section 6.1 Item 7 and Section 6.2."""
    assert LotStatus.__pg_enum_name__ == "lot_status"
    expected = {"DRAFT", "AVAILABLE", "AGGREGATED", "COMMITTED", "SOLD", "CANCELLED"}
    assert {e.value for e in LotStatus} == expected


def test_sale_intent_status_values() -> None:
    """Verify SaleIntentStatus enum values match Architecture Section 6.1 Item 8 and Section 6.2."""
    assert SaleIntentStatus.__pg_enum_name__ == "sale_intent_status"
    expected = {"ACTIVE", "SUSPENDED_POOLED", "MATCHED", "CLOSED", "CANCELLED"}
    assert {e.value for e in SaleIntentStatus} == expected


def test_data_source_tier_values() -> None:
    """Verify DataSourceTier enum values match Architecture Section 6.1 Item 10 and Section 9.1."""
    assert DataSourceTier.__pg_enum_name__ == "data_source_tier"
    expected = {"DISTRICT", "STATE", "NATIONAL_BASELINE"}
    assert {e.value for e in DataSourceTier} == expected


def test_buyer_demand_status_values() -> None:
    """Verify BuyerDemandStatus enum values match Architecture Section 6.1 Item 11."""
    assert BuyerDemandStatus.__pg_enum_name__ == "buyer_demand_status"
    expected = {"OPEN", "FULFILLED", "CANCELLED"}
    assert {e.value for e in BuyerDemandStatus} == expected


def test_offer_status_values() -> None:
    """Verify OfferStatus enum values match Architecture Section 6.1 Item 13."""
    assert OfferStatus.__pg_enum_name__ == "offer_status"
    expected = {"PENDING", "COUNTERED", "ACCEPTED", "REJECTED", "EXPIRED"}
    assert {e.value for e in OfferStatus} == expected


def test_order_status_values() -> None:
    """Verify OrderStatus enum values match Architecture Section 6.1 Item 15."""
    assert OrderStatus.__pg_enum_name__ == "order_status"
    expected = {"CONFIRMED", "DISPATCHED", "DELIVERED", "COMPLETED", "CANCELLED"}
    assert {e.value for e in OrderStatus} == expected


def test_allocation_payout_status_values() -> None:
    """Verify AllocationPayoutStatus enum values match Architecture Section 6.1 Item 16."""
    assert AllocationPayoutStatus.__pg_enum_name__ == "allocation_payout_status"
    expected = {"PENDING", "DISBURSED", "CONFIRMED_BY_FARMER"}
    assert {e.value for e in AllocationPayoutStatus} == expected


def test_logistics_status_values() -> None:
    """Verify LogisticsStatus enum values match Architecture Section 6.1 Item 17."""
    assert LogisticsStatus.__pg_enum_name__ == "logistics_status"
    expected = {"PENDING_PICKUP", "IN_TRANSIT", "DELIVERED"}
    assert {e.value for e in LogisticsStatus} == expected


def test_payment_stage_values() -> None:
    """Verify PaymentStage enum values match Architecture Section 6.1 Item 18."""
    assert PaymentStage.__pg_enum_name__ == "payment_stage"
    expected = {"ADVANCE", "FINAL_SETTLEMENT"}
    assert {e.value for e in PaymentStage} == expected


def test_payment_method_values() -> None:
    """Verify PaymentMethod enum values match Architecture Section 6.1 Item 18."""
    assert PaymentMethod.__pg_enum_name__ == "payment_method"
    expected = {"BANK_TRANSFER", "UPI", "OFFLINE_CASH", "FUTURE_RAZORPAY"}
    assert {e.value for e in PaymentMethod} == expected


def test_payment_status_values() -> None:
    """Verify PaymentStatus enum values match Architecture Section 6.1 Item 18."""
    assert PaymentStatus.__pg_enum_name__ == "payment_status"
    expected = {"SUBMITTED", "VERIFIED_BY_SELLER", "DISPUTED"}
    assert {e.value for e in PaymentStatus} == expected


def test_grievance_category_values() -> None:
    """Verify GrievanceCategory enum values match Architecture Section 6.1 Item 19."""
    assert GrievanceCategory.__pg_enum_name__ == "grievance_category"
    expected = {
        "QUALITY_DEFECT",
        "WEIGHT_SHORTAGE",
        "PAYMENT_DELAY",
        "TRANSIT_DAMAGE",
    }
    assert {e.value for e in GrievanceCategory} == expected


def test_grievance_status_values() -> None:
    """Verify GrievanceStatus enum values match Architecture Section 6.1 Item 19."""
    assert GrievanceStatus.__pg_enum_name__ == "grievance_status"
    expected = {"OPEN", "INVESTIGATING", "RESOLVED", "CLOSED"}
    assert {e.value for e in GrievanceStatus} == expected


def test_all_enums_are_string_instances() -> None:
    """Verify all enum members inherit from str and evaluate to their string values."""
    for enum_cls in ALL_ENUMS:
        for member in enum_cls:
            assert isinstance(member.value, str)
            assert str(member) == member.value
            assert hasattr(enum_cls, "__pg_enum_name__")


def test_declarative_base_class() -> None:
    """Verify Base is a valid DeclarativeBase instance with metadata."""
    assert issubclass(Base, DeclarativeBase)
    assert hasattr(Base, "metadata")


def test_uuid_primary_key_mixin() -> None:
    """Verify UUIDPrimaryKeyMixin configures UUID primary key with callable default."""
    class TestDeclarativeBase(DeclarativeBase):
        pass

    class DummyItem(TestDeclarativeBase, UUIDPrimaryKeyMixin):
        __tablename__ = "dummy_items"

    id_col = DummyItem.__table__.c.id
    assert id_col.primary_key is True
    assert isinstance(id_col.type, UUID)

    # Test default generator
    generated_uuid = id_col.default.arg(None)
    assert isinstance(generated_uuid, uuid.UUID)
    assert generated_uuid.version == 4


def test_timestamp_mixin() -> None:
    """Verify TimestampMixin configures created_at and updated_at with UTC timezone."""
    class TestDeclarativeBase(DeclarativeBase):
        pass

    class DummyRecord(TestDeclarativeBase, TimestampMixin):
        __tablename__ = "dummy_records"
        id: Mapped[int] = mapped_column(Integer, primary_key=True)

    created_col = DummyRecord.__table__.c.created_at
    updated_col = DummyRecord.__table__.c.updated_at

    assert created_col.type.timezone is True
    assert updated_col.type.timezone is True
    assert created_col.nullable is False
    assert updated_col.nullable is False

    now_val = utc_now()
    assert isinstance(now_val, datetime)
    assert now_val.tzinfo == timezone.utc
