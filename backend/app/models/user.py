"""SQLAlchemy models for User accounts, Farmer profiles, and Buyer credentials."""

from decimal import Decimal
from typing import Optional
import uuid
from sqlalchemy import Boolean, Enum as SQLEnum, ForeignKey, Numeric, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.models.base import Base, TimestampMixin, UUIDPrimaryKeyMixin
from app.models.enums import (
    BuyerCategory,
    BuyerVerificationStatus,
    FarmerKYCStatus,
    UserRole,
    VerificationDocType,
)


class User(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    """Base user account for authentication and role boundaries (Architecture Section 6.1 Item 1)."""

    __tablename__ = "users"

    phone_number: Mapped[str] = mapped_column(
        String(20),
        unique=True,
        index=True,
        nullable=False,
        doc="Primary login identifier (10-digit mobile number with optional country code)",
    )
    hashed_password: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        doc="Bcrypt-hashed password string",
    )
    role: Mapped[UserRole] = mapped_column(
        SQLEnum(UserRole, name=UserRole.__pg_enum_name__, native_enum=True),
        nullable=False,
        doc="Single primary actor role for MVP: FARMER, FPO_REPRESENTATIVE, BUYER, ADMIN",
    )
    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
        doc="Account active flag for administrative deactivation",
    )

    # One-to-one profile relationships
    farmer_profile: Mapped[Optional["FarmerProfile"]] = relationship(
        "FarmerProfile",
        back_populates="user",
        uselist=False,
        cascade="all, delete-orphan",
    )
    buyer_profile: Mapped[Optional["BuyerProfile"]] = relationship(
        "BuyerProfile",
        back_populates="user",
        uselist=False,
        cascade="all, delete-orphan",
    )

    # Affiliations
    fpo_memberships: Mapped[list["FPOMembership"]] = relationship(  # type: ignore[name-defined] # noqa: F821
        "FPOMembership",
        back_populates="farmer_user",
        cascade="all, delete-orphan",
    )


class FarmerProfile(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    """Extended agrarian profile details for farmers (Architecture Section 6.1 Item 2)."""

    __tablename__ = "farmer_profiles"

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        unique=True,
        index=True,
        nullable=False,
    )
    full_name: Mapped[str] = mapped_column(String(150), nullable=False)
    state: Mapped[str] = mapped_column(String(100), nullable=False)
    district: Mapped[str] = mapped_column(String(100), index=True, nullable=False)
    pincode: Mapped[str] = mapped_column(String(6), index=True, nullable=False)
    land_holding_acres: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(10, 2),
        nullable=True,
        doc="Operational farmland holding size in acres",
    )
    kyc_status: Mapped[FarmerKYCStatus] = mapped_column(
        SQLEnum(FarmerKYCStatus, name=FarmerKYCStatus.__pg_enum_name__, native_enum=True),
        default=FarmerKYCStatus.PENDING,
        nullable=False,
    )

    user: Mapped["User"] = relationship("User", back_populates="farmer_profile")


class BuyerProfile(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    """Commercial produce buyer credentials and KYC documents (Architecture Section 6.1 Item 5)."""

    __tablename__ = "buyer_profiles"

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        unique=True,
        index=True,
        nullable=False,
    )
    company_name: Mapped[str] = mapped_column(String(200), nullable=False)
    buyer_category: Mapped[BuyerCategory] = mapped_column(
        SQLEnum(BuyerCategory, name=BuyerCategory.__pg_enum_name__, native_enum=True),
        nullable=False,
    )
    gstin: Mapped[Optional[str]] = mapped_column(
        String(15),
        nullable=True,
        doc="Optional for local commission agents and traders below GST threshold",
    )
    verification_doc_type: Mapped[VerificationDocType] = mapped_column(
        SQLEnum(VerificationDocType, name=VerificationDocType.__pg_enum_name__, native_enum=True),
        nullable=False,
    )
    verification_doc_number: Mapped[str] = mapped_column(String(50), nullable=False)
    verification_status: Mapped[BuyerVerificationStatus] = mapped_column(
        SQLEnum(BuyerVerificationStatus, name=BuyerVerificationStatus.__pg_enum_name__, native_enum=True),
        default=BuyerVerificationStatus.PENDING,
        nullable=False,
    )

    user: Mapped["User"] = relationship("User", back_populates="buyer_profile")
