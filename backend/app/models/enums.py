"""Canonical Python Enum definitions corresponding to PostgreSQL native ENUM types.

All 22 enum classes are strictly derived from docs/architecture.md.
Each enum inherits from (str, Enum) to ensure string serialization compatibility
with Pydantic schemas and standard JSON APIs.

PostgreSQL Mapping:
    When mapped in SQLAlchemy columns, each enum specifies native_enum=True
    and its designated __pg_enum_name__ to create clean, named PostgreSQL ENUM types:
        Column(Enum(UserRole, name=UserRole.__pg_enum_name__, native_enum=True))
"""

from enum import StrEnum


class UserRole(StrEnum):
    """User account primary actor role (Architecture Section 6.1 Item 1)."""
    __pg_enum_name__ = "user_role"

    FARMER = "FARMER"
    FPO_REPRESENTATIVE = "FPO_REPRESENTATIVE"
    BUYER = "BUYER"
    ADMIN = "ADMIN"


class FarmerKYCStatus(StrEnum):
    """Farmer identification verification status (Architecture Section 5, 6.1 Item 2)."""
    __pg_enum_name__ = "farmer_kyc_status"

    PENDING = "PENDING"
    VERIFIED = "VERIFIED"
    REJECTED = "REJECTED"


class BuyerVerificationStatus(StrEnum):
    """Commercial buyer credentials verification status (Architecture Section 6.1 Item 5)."""
    __pg_enum_name__ = "buyer_verification_status"

    PENDING = "PENDING"
    VERIFIED = "VERIFIED"
    REJECTED = "REJECTED"


class FPOMembershipStatus(StrEnum):
    """Farmer-to-FPO affiliation membership status (Architecture Section 6.1 Item 4)."""
    __pg_enum_name__ = "fpo_membership_status"

    PENDING = "PENDING"
    ACTIVE = "ACTIVE"
    REJECTED = "REJECTED"


class BuyerCategory(StrEnum):
    """Category of commercial produce buyer (Architecture Section 6.1 Item 5)."""
    __pg_enum_name__ = "buyer_category"

    INSTITUTIONAL_PROCESSOR = "INSTITUTIONAL_PROCESSOR"
    WHOLESALER = "WHOLESALER"
    COMMISSION_AGENT = "COMMISSION_AGENT"
    RETAILER_EXPORTER = "RETAILER_EXPORTER"


class VerificationDocType(StrEnum):
    """Statutory business registration document type (Architecture Section 6.1 Item 5)."""
    __pg_enum_name__ = "verification_doc_type"

    GSTIN = "GSTIN"
    APMC_LICENSE = "APMC_LICENSE"
    FSSAI_REGISTRATION = "FSSAI_REGISTRATION"
    TRADE_LICENSE = "TRADE_LICENSE"
    PAN = "PAN"


class CropCategory(StrEnum):
    """Broad agricultural crop category (Architecture Section 6.1 Item 6)."""
    __pg_enum_name__ = "crop_category"

    CEREALS = "CEREALS"
    PULSES = "PULSES"
    OILSEEDS = "OILSEEDS"
    VEGETABLES = "VEGETABLES"
    FRUITS = "FRUITS"


class StandardUnit(StrEnum):
    """Measurement unit for agricultural harvest volumes (Architecture Section 6.1 Item 6)."""
    __pg_enum_name__ = "standard_unit"

    QUINTAL = "QUINTAL"
    KG = "KG"


class QualityGrade(StrEnum):
    """Standardized harvest quality classification (Architecture Section 6.1 Item 7)."""
    __pg_enum_name__ = "quality_grade"

    GRADE_A = "GRADE_A"
    GRADE_B = "GRADE_B"
    GRADE_C = "GRADE_C"


class LotStatus(StrEnum):
    """Lifecycle status of a harvest lot (Architecture Section 6.1 Item 7, Section 6.2)."""
    __pg_enum_name__ = "lot_status"

    DRAFT = "DRAFT"
    AVAILABLE = "AVAILABLE"
    AGGREGATED = "AGGREGATED"
    COMMITTED = "COMMITTED"
    SOLD = "SOLD"
    CANCELLED = "CANCELLED"


class SaleIntentStatus(StrEnum):
    """Commercial listing intent status (Architecture Section 6.1 Item 8, Section 6.2)."""
    __pg_enum_name__ = "sale_intent_status"

    ACTIVE = "ACTIVE"
    SUSPENDED_POOLED = "SUSPENDED_POOLED"
    MATCHED = "MATCHED"
    CLOSED = "CLOSED"
    CANCELLED = "CANCELLED"


class DataSourceTier(StrEnum):
    """Price prediction advisory fallback data tier (Architecture Section 6.1 Item 10, Section 9.1)."""
    __pg_enum_name__ = "data_source_tier"

    DISTRICT = "DISTRICT"
    STATE = "STATE"
    NATIONAL_BASELINE = "NATIONAL_BASELINE"


class BuyerDemandStatus(StrEnum):
    """Buyer RFQ / demand posting lifecycle status (Architecture Section 6.1 Item 11)."""
    __pg_enum_name__ = "buyer_demand_status"

    OPEN = "OPEN"
    FULFILLED = "FULFILLED"
    CANCELLED = "CANCELLED"


class OfferStatus(StrEnum):
    """Bilateral bid / counter-proposal status (Architecture Section 6.1 Item 13)."""
    __pg_enum_name__ = "offer_status"

    PENDING = "PENDING"
    COUNTERED = "COUNTERED"
    ACCEPTED = "ACCEPTED"
    REJECTED = "REJECTED"
    EXPIRED = "EXPIRED"


class OrderStatus(StrEnum):
    """Binding sales contract execution status (Architecture Section 6.1 Item 15)."""
    __pg_enum_name__ = "order_status"

    CONFIRMED = "CONFIRMED"
    DISPATCHED = "DISPATCHED"
    DELIVERED = "DELIVERED"
    COMPLETED = "COMPLETED"
    CANCELLED = "CANCELLED"


class AllocationPayoutStatus(StrEnum):
    """FPO member bulk order share payout tracking status (Architecture Section 6.1 Item 16)."""
    __pg_enum_name__ = "allocation_payout_status"

    PENDING = "PENDING"
    DISBURSED = "DISBURSED"
    CONFIRMED_BY_FARMER = "CONFIRMED_BY_FARMER"


class LogisticsStatus(StrEnum):
    """Physical shipment tracking status (Architecture Section 6.1 Item 17)."""
    __pg_enum_name__ = "logistics_status"

    PENDING_PICKUP = "PENDING_PICKUP"
    IN_TRANSIT = "IN_TRANSIT"
    DELIVERED = "DELIVERED"


class PaymentStage(StrEnum):
    """Payment installment milestone (Architecture Section 6.1 Item 18)."""
    __pg_enum_name__ = "payment_stage"

    ADVANCE = "ADVANCE"
    FINAL_SETTLEMENT = "FINAL_SETTLEMENT"


class PaymentMethod(StrEnum):
    """Recorded payment settlement mechanism (Architecture Section 6.1 Item 18)."""
    __pg_enum_name__ = "payment_method"

    BANK_TRANSFER = "BANK_TRANSFER"
    UPI = "UPI"
    OFFLINE_CASH = "OFFLINE_CASH"
    FUTURE_RAZORPAY = "FUTURE_RAZORPAY"


class PaymentStatus(StrEnum):
    """Settlement audit verification status (Architecture Section 6.1 Item 18)."""
    __pg_enum_name__ = "payment_status"

    SUBMITTED = "SUBMITTED"
    VERIFIED_BY_SELLER = "VERIFIED_BY_SELLER"
    DISPUTED = "DISPUTED"


class GrievanceCategory(StrEnum):
    """Dispute complaint category (Architecture Section 6.1 Item 19)."""
    __pg_enum_name__ = "grievance_category"

    QUALITY_DEFECT = "QUALITY_DEFECT"
    WEIGHT_SHORTAGE = "WEIGHT_SHORTAGE"
    PAYMENT_DELAY = "PAYMENT_DELAY"
    TRANSIT_DAMAGE = "TRANSIT_DAMAGE"


class GrievanceStatus(StrEnum):
    """Administrative grievance resolution status (Architecture Section 6.1 Item 19)."""
    __pg_enum_name__ = "grievance_status"

    OPEN = "OPEN"
    INVESTIGATING = "INVESTIGATING"
    RESOLVED = "RESOLVED"
    CLOSED = "CLOSED"


ALL_ENUMS = (
    UserRole,
    FarmerKYCStatus,
    BuyerVerificationStatus,
    FPOMembershipStatus,
    BuyerCategory,
    VerificationDocType,
    CropCategory,
    StandardUnit,
    QualityGrade,
    LotStatus,
    SaleIntentStatus,
    DataSourceTier,
    BuyerDemandStatus,
    OfferStatus,
    OrderStatus,
    AllocationPayoutStatus,
    LogisticsStatus,
    PaymentStage,
    PaymentMethod,
    PaymentStatus,
    GrievanceCategory,
    GrievanceStatus,
)
