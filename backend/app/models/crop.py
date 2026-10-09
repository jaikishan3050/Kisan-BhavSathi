"""SQLAlchemy models for agricultural produce, harvest lots, and sale intents."""

from datetime import date
from decimal import Decimal
from typing import Optional
import uuid
from sqlalchemy import (
    Boolean,
    CheckConstraint,
    Date,
    Enum as SQLEnum,
    ForeignKey,
    Numeric,
    String,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.models.base import Base, TimestampMixin, UUIDPrimaryKeyMixin
from app.models.enums import (
    CropCategory,
    LotStatus,
    QualityGrade,
    SaleIntentStatus,
    StandardUnit,
)


class Crop(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    """Standardized master catalog of agricultural produce (Architecture Section 6.1 Item 6)."""

    __tablename__ = "crops"

    name: Mapped[str] = mapped_column(
        String(100),
        unique=True,
        index=True,
        nullable=False,
        doc="Commodity name (e.g., 'Wheat', 'Soybean', 'Chana')",
    )
    category: Mapped[CropCategory] = mapped_column(
        SQLEnum(CropCategory, name=CropCategory.__pg_enum_name__, native_enum=True),
        nullable=False,
    )
    standard_unit: Mapped[StandardUnit] = mapped_column(
        SQLEnum(StandardUnit, name=StandardUnit.__pg_enum_name__, native_enum=True),
        default=StandardUnit.QUINTAL,
        nullable=False,
    )

    lots: Mapped[list["Lot"]] = relationship("Lot", back_populates="crop")


class Lot(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    """Harvest lot batch owned by either a farmer or an FPO (Architecture Section 6.1 Item 7)."""

    __tablename__ = "lots"

    # Exactly one owner must be populated: either farmer_user_id OR fpo_id
    farmer_user_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="RESTRICT"),
        index=True,
        nullable=True,
        doc="Individual farmer owner ID (NULL if managed directly by FPO as a bulk lot)",
    )
    fpo_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("fpos.id", ondelete="RESTRICT"),
        index=True,
        nullable=True,
        doc="FPO organization owner ID (NULL if owned by an individual farmer)",
    )
    crop_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("crops.id", ondelete="RESTRICT"),
        index=True,
        nullable=False,
    )
    quantity: Mapped[Decimal] = mapped_column(
        Numeric(12, 2),
        nullable=False,
        doc="Harvest volume in crop standard units (Quintals/Kg)",
    )
    quality_grade: Mapped[QualityGrade] = mapped_column(
        SQLEnum(QualityGrade, name=QualityGrade.__pg_enum_name__, native_enum=True),
        nullable=False,
    )
    moisture_percentage: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(5, 2),
        nullable=True,
        doc="Moisture content percentage (optional for produce without moisture metrics)",
    )
    storage_location_pincode: Mapped[str] = mapped_column(
        String(6),
        index=True,
        nullable=False,
    )
    is_aggregated: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
        doc="True if this lot has been bundled into a parent FPO bulk lot",
    )
    parent_fpo_lot_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("lots.id", ondelete="RESTRICT"),
        index=True,
        nullable=True,
        doc="Self-referential link pointing to parent bulk lot when pooled",
    )
    status: Mapped[LotStatus] = mapped_column(
        SQLEnum(LotStatus, name=LotStatus.__pg_enum_name__, native_enum=True),
        default=LotStatus.DRAFT,
        nullable=False,
    )

    __table_args__ = (
        CheckConstraint(
            "((farmer_user_id IS NOT NULL AND fpo_id IS NULL) OR (farmer_user_id IS NULL AND fpo_id IS NOT NULL))",
            name="chk_lot_ownership",
        ),
        CheckConstraint("quantity > 0", name="chk_lot_quantity_positive"),
    )

    # Relationships
    farmer: Mapped[Optional["User"]] = relationship(  # type: ignore[name-defined] # noqa: F821
        "User",
        foreign_keys=[farmer_user_id],
    )
    fpo: Mapped[Optional["FPO"]] = relationship(  # type: ignore[name-defined] # noqa: F821
        "FPO",
        foreign_keys=[fpo_id],
        back_populates="managed_lots",
    )
    crop: Mapped["Crop"] = relationship("Crop", back_populates="lots")
    sale_intent: Mapped[Optional["SaleIntent"]] = relationship(
        "SaleIntent",
        back_populates="lot",
        uselist=False,
        cascade="all, delete-orphan",
    )
    parent_fpo_lot: Mapped[Optional["Lot"]] = relationship(
        "Lot",
        remote_side="Lot.id",
        foreign_keys=[parent_fpo_lot_id],
        backref="constituent_lots",
    )


class SaleIntent(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    """Commercial intent and pricing parameters to sell a lot (Architecture Section 6.1 Item 8)."""

    __tablename__ = "sale_intents"

    lot_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("lots.id", ondelete="RESTRICT"),
        unique=True,
        index=True,
        nullable=False,
    )
    expected_price_per_unit: Mapped[Decimal] = mapped_column(
        Numeric(12, 2),
        nullable=False,
        doc="Target asking price per quintal/kg",
    )
    minimum_acceptable_price: Mapped[Decimal] = mapped_column(
        Numeric(12, 2),
        nullable=False,
        doc="Reserve price floor below which offers cannot be auto-accepted",
    )
    available_from_date: Mapped[date] = mapped_column(Date, nullable=False)
    available_until_date: Mapped[date] = mapped_column(Date, nullable=False)
    allow_fpo_pooling: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
        doc="Farmer consent flag authorizing FPO representatives to aggregate this lot",
    )
    status: Mapped[SaleIntentStatus] = mapped_column(
        SQLEnum(SaleIntentStatus, name=SaleIntentStatus.__pg_enum_name__, native_enum=True),
        default=SaleIntentStatus.ACTIVE,
        nullable=False,
    )

    __table_args__ = (
        CheckConstraint(
            "expected_price_per_unit >= minimum_acceptable_price",
            name="chk_sale_intent_price_bounds",
        ),
        CheckConstraint("minimum_acceptable_price > 0", name="chk_sale_intent_min_price_positive"),
        CheckConstraint("available_until_date >= available_from_date", name="chk_sale_intent_date_bounds"),
    )

    lot: Mapped["Lot"] = relationship("Lot", back_populates="sale_intent")
    offers: Mapped[list["Offer"]] = relationship(  # type: ignore[name-defined] # noqa: F821
        "Offer",
        back_populates="sale_intent",
    )
    matches: Mapped[list["Match"]] = relationship(  # type: ignore[name-defined] # noqa: F821
        "Match",
        back_populates="sale_intent",
    )
