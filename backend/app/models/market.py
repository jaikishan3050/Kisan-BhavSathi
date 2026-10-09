"""SQLAlchemy models for APMC market benchmarks, price advisories, and postal coordinates."""

from datetime import date, datetime
from decimal import Decimal
from typing import Optional
import uuid
from sqlalchemy import (
    CheckConstraint,
    Date,
    DateTime,
    Enum as SQLEnum,
    ForeignKey,
    Index,
    Integer,
    Numeric,
    String,
    Text,
    func,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.models.base import Base, TimestampMixin, UUIDPrimaryKeyMixin, utc_now
from app.models.enums import DataSourceTier


class MarketPrice(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    """Daily APMC mandi market benchmark prices (Architecture Section 6.1 Item 9)."""

    __tablename__ = "market_prices"

    crop_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("crops.id", ondelete="RESTRICT"),
        index=True,
        nullable=False,
    )
    mandi_name: Mapped[str] = mapped_column(String(150), nullable=False)
    district: Mapped[str] = mapped_column(String(100), index=True, nullable=False)
    state: Mapped[str] = mapped_column(String(100), index=True, nullable=False)
    min_price: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    max_price: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    modal_price: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    price_date: Mapped[date] = mapped_column(Date, index=True, nullable=False)

    __table_args__ = (
        CheckConstraint("min_price <= modal_price AND modal_price <= max_price", name="chk_market_price_spread"),
        CheckConstraint("min_price > 0", name="chk_market_price_positive"),
        Index("ix_market_prices_crop_district_date", "crop_id", "district", "price_date"),
    )

    crop: Mapped["Crop"] = relationship("Crop")  # type: ignore[name-defined] # noqa: F821


class PricePrediction(Base, UUIDPrimaryKeyMixin):
    """Explainable price intelligence advisory records (Architecture Section 6.1 Item 10, Section 9.1)."""

    __tablename__ = "price_predictions"

    crop_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("crops.id", ondelete="RESTRICT"),
        index=True,
        nullable=False,
    )
    lot_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("lots.id", ondelete="SET NULL"),
        index=True,
        nullable=True,
        doc="Optional link if advisory was computed for a specific registered harvest lot",
    )
    suggested_min_price: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    suggested_modal_price: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    suggested_max_price: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    confidence_score: Mapped[Decimal] = mapped_column(
        Numeric(5, 2),
        nullable=False,
        doc="Statistical advisory confidence score between 0.00 and 100.00",
    )
    data_source_tier: Mapped[DataSourceTier] = mapped_column(
        SQLEnum(DataSourceTier, name=DataSourceTier.__pg_enum_name__, native_enum=True),
        nullable=False,
        doc="Fallback hierarchy tier: DISTRICT, STATE, or NATIONAL_BASELINE",
    )
    data_freshness_days: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        doc="Age in days of the newest market arrival data used in the calculation",
    )
    explanation_summary: Mapped[str] = mapped_column(
        Text,
        nullable=False,
        doc="Human-readable explanation of estimated range and contributing grade/freight adjustments",
    )
    generated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        default=utc_now,
        nullable=False,
    )

    __table_args__ = (
        CheckConstraint(
            "suggested_min_price <= suggested_modal_price AND suggested_modal_price <= suggested_max_price",
            name="chk_price_prediction_spread",
        ),
        CheckConstraint("confidence_score >= 0 AND confidence_score <= 100", name="chk_prediction_confidence_range"),
    )

    crop: Mapped["Crop"] = relationship("Crop")  # type: ignore[name-defined] # noqa: F821
    lot: Mapped[Optional["Lot"]] = relationship("Lot")  # type: ignore[name-defined] # noqa: F821


class PincodeCoordinate(Base, TimestampMixin):
    """Reference lookup mapping Indian postal codes to centroid coordinates (Architecture Section 10.2)."""

    __tablename__ = "pincode_coordinates"

    pincode: Mapped[str] = mapped_column(
        String(6),
        primary_key=True,
        doc="Standard 6-digit Indian Postal PIN code",
    )
    latitude: Mapped[Decimal] = mapped_column(
        Numeric(9, 6),
        nullable=False,
        doc="Centroid latitude coordinate in decimal degrees",
    )
    longitude: Mapped[Decimal] = mapped_column(
        Numeric(9, 6),
        nullable=False,
        doc="Centroid longitude coordinate in decimal degrees",
    )
    district: Mapped[str] = mapped_column(String(100), index=True, nullable=False)
    state: Mapped[str] = mapped_column(String(100), nullable=False)
