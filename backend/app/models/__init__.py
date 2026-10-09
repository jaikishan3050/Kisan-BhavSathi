"""SQLAlchemy models package for Kisan BhavSaathi.

Exports Base declarative metadata, mixins, all 22 domain enums,
and all 20 relational database models.
"""

from app.models.base import Base, TimestampMixin, UUIDPrimaryKeyMixin
from app.models.crop import Crop, Lot, SaleIntent
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
from app.models.fpo import FPO, FPOMembership
from app.models.market import MarketPrice, PincodeCoordinate, PricePrediction
from app.models.matching import BuyerDemand, Match, Negotiation, Offer
from app.models.order import (
    Grievance,
    Logistics,
    Order,
    OrderLotAllocation,
    PaymentRecord,
)
from app.models.user import BuyerProfile, FarmerProfile, User

__all__ = [
    # Base and Mixins
    "Base",
    "UUIDPrimaryKeyMixin",
    "TimestampMixin",
    # Enums
    "ALL_ENUMS",
    "UserRole",
    "FarmerKYCStatus",
    "BuyerVerificationStatus",
    "FPOMembershipStatus",
    "BuyerCategory",
    "VerificationDocType",
    "CropCategory",
    "StandardUnit",
    "QualityGrade",
    "LotStatus",
    "SaleIntentStatus",
    "DataSourceTier",
    "BuyerDemandStatus",
    "OfferStatus",
    "OrderStatus",
    "AllocationPayoutStatus",
    "LogisticsStatus",
    "PaymentStage",
    "PaymentMethod",
    "PaymentStatus",
    "GrievanceCategory",
    "GrievanceStatus",
    # Domain Models (20 Entities)
    "User",
    "FarmerProfile",
    "BuyerProfile",
    "FPO",
    "FPOMembership",
    "Crop",
    "Lot",
    "SaleIntent",
    "MarketPrice",
    "PricePrediction",
    "PincodeCoordinate",
    "BuyerDemand",
    "Match",
    "Offer",
    "Negotiation",
    "Order",
    "OrderLotAllocation",
    "Logistics",
    "PaymentRecord",
    "Grievance",
]
