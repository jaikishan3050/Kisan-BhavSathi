"""SQLAlchemy models for buyer procurement demands, compatibility matches, offers, and negotiations."""

from datetime import date
from decimal import Decimal
from typing import Any, Optional
import uuid
from sqlalchemy import (
    CheckConstraint,
    Date,
    Enum as SQLEnum,
    ForeignKey,
    Numeric,
    String,
    UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.models.base import Base, TimestampMixin, UUIDPrimaryKeyMixin
from app.models.enums import BuyerDemandStatus, OfferStatus


class BuyerDemand(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    """Purchase request / Request For Quote (RFQ) from a verified buyer (Architecture Section 6.1 Item 11)."""

    __tablename__ = "buyer_demands"

    buyer_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="RESTRICT"),
        index=True,
        nullable=False,
    )
    crop_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("crops.id", ondelete="RESTRICT"),
        index=True,
        nullable=False,
    )
    required_quantity: Mapped[Decimal] = mapped_column(
        Numeric(12, 2),
        nullable=False,
        doc="Procurement volume required in crop standard units (Quintals/Kg)",
    )
    acceptable_grades: Mapped[list[Any] | dict[str, Any]] = mapped_column(
        JSONB,
        nullable=False,
        doc="PostgreSQL JSONB array of acceptable QualityGrade values e.g. ['GRADE_A', 'GRADE_B']",
    )
    max_budget_price: Mapped[Decimal] = mapped_column(
        Numeric(12, 2),
        nullable=False,
        doc="Maximum price ceiling per unit buyer is willing to spend",
    )
    delivery_destination_pincode: Mapped[str] = mapped_column(
        String(6),
        index=True,
        nullable=False,
    )
    required_by_date: Mapped[date] = mapped_column(
        Date,
        nullable=False,
    )
    status: Mapped[BuyerDemandStatus] = mapped_column(
        SQLEnum(BuyerDemandStatus, name=BuyerDemandStatus.__pg_enum_name__, native_enum=True),
        default=BuyerDemandStatus.OPEN,
        nullable=False,
    )

    __table_args__ = (
        CheckConstraint("required_quantity > 0", name="chk_buyer_demand_quantity_positive"),
        CheckConstraint("max_budget_price > 0", name="chk_buyer_demand_budget_positive"),
    )

    # Relationships
    buyer: Mapped["User"] = relationship("User")  # type: ignore[name-defined] # noqa: F821
    crop: Mapped["Crop"] = relationship("Crop")  # type: ignore[name-defined] # noqa: F821
    matches: Mapped[list["Match"]] = relationship(
        "Match",
        back_populates="buyer_demand",
        cascade="all, delete-orphan",
    )


class Match(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    """Algorithmic compatibility association between a buyer demand and a sale intent (Architecture Section 6.1 Item 12)."""

    __tablename__ = "matches"

    buyer_demand_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("buyer_demands.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )
    sale_intent_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("sale_intents.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )
    compatibility_score: Mapped[Decimal] = mapped_column(
        Numeric(5, 2),
        nullable=False,
        doc="Algorithmic match score (0.00 to 100.00)",
    )
    distance_km: Mapped[Decimal] = mapped_column(
        Numeric(8, 2),
        nullable=False,
        doc="Haversine distance in kilometers between origin lot and destination pincode",
    )

    __table_args__ = (
        UniqueConstraint("buyer_demand_id", "sale_intent_id", name="uq_match_demand_intent"),
        CheckConstraint("compatibility_score >= 0 AND compatibility_score <= 100", name="chk_match_score_range"),
        CheckConstraint("distance_km >= 0", name="chk_match_distance_positive"),
    )

    # Relationships
    buyer_demand: Mapped["BuyerDemand"] = relationship("BuyerDemand", back_populates="matches")
    sale_intent: Mapped["SaleIntent"] = relationship("SaleIntent", back_populates="matches")  # type: ignore[name-defined] # noqa: F821
    offers: Mapped[list["Offer"]] = relationship("Offer", back_populates="match")


class Offer(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    """Formal commercial bid placed on a Sale Intent or Bulk Lot (Architecture Section 6.1 Item 13)."""

    __tablename__ = "offers"

    match_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("matches.id", ondelete="SET NULL"),
        index=True,
        nullable=True,
        doc="Optional link to algorithm match; NULL for direct unsolicited marketplace bids",
    )
    sale_intent_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("sale_intents.id", ondelete="RESTRICT"),
        index=True,
        nullable=False,
    )
    buyer_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="RESTRICT"),
        index=True,
        nullable=False,
    )
    seller_user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="RESTRICT"),
        index=True,
        nullable=False,
        doc="Seller user: farmer or FPO representative",
    )
    proposed_price_per_unit: Mapped[Decimal] = mapped_column(
        Numeric(12, 2),
        nullable=False,
        doc="Proposed price per unit in INR",
    )
    proposed_quantity: Mapped[Decimal] = mapped_column(
        Numeric(12, 2),
        nullable=False,
        doc="Proposed transaction volume in crop standard units",
    )
    status: Mapped[OfferStatus] = mapped_column(
        SQLEnum(OfferStatus, name=OfferStatus.__pg_enum_name__, native_enum=True),
        default=OfferStatus.PENDING,
        nullable=False,
    )

    __table_args__ = (
        CheckConstraint("proposed_price_per_unit > 0", name="chk_offer_price_positive"),
        CheckConstraint("proposed_quantity > 0", name="chk_offer_quantity_positive"),
    )

    # Relationships
    match: Mapped[Optional["Match"]] = relationship("Match", back_populates="offers")
    sale_intent: Mapped["SaleIntent"] = relationship("SaleIntent", back_populates="offers")  # type: ignore[name-defined] # noqa: F821
    buyer: Mapped["User"] = relationship("User", foreign_keys=[buyer_id])  # type: ignore[name-defined] # noqa: F821
    seller: Mapped["User"] = relationship("User", foreign_keys=[seller_user_id])  # type: ignore[name-defined] # noqa: F821
    negotiations: Mapped[list["Negotiation"]] = relationship(
        "Negotiation",
        back_populates="offer",
        cascade="all, delete-orphan",
    )
    order: Mapped[Optional["Order"]] = relationship(  # type: ignore[name-defined] # noqa: F821
        "Order",
        back_populates="offer",
        uselist=False,
    )


class Negotiation(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    """Counter-offer audit trail between buyer and seller (Architecture Section 6.1 Item 14)."""

    __tablename__ = "negotiations"

    offer_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("offers.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )
    sender_user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="RESTRICT"),
        index=True,
        nullable=False,
        doc="User ID who submitted this counter-proposal (buyer or seller)",
    )
    counter_price_per_unit: Mapped[Decimal] = mapped_column(
        Numeric(12, 2),
        nullable=False,
        doc="Counter-offered price per unit",
    )
    remarks: Mapped[Optional[str]] = mapped_column(
        String(500),
        nullable=True,
        doc="Optional note accompanying the counter-offer",
    )

    __table_args__ = (
        CheckConstraint("counter_price_per_unit > 0", name="chk_negotiation_price_positive"),
    )

    # Relationships
    offer: Mapped["Offer"] = relationship("Offer", back_populates="negotiations")
    sender: Mapped["User"] = relationship("User")  # type: ignore[name-defined] # noqa: F821
