"""SQLAlchemy models for Orders, FPO lot allocations, Logistics, Payments, and Grievances."""

from datetime import datetime
from decimal import Decimal
from typing import Optional
import uuid
from sqlalchemy import (
    Boolean,
    CheckConstraint,
    DateTime,
    Enum as SQLEnum,
    ForeignKey,
    Numeric,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.models.base import Base, TimestampMixin, UUIDPrimaryKeyMixin
from app.models.enums import (
    AllocationPayoutStatus,
    GrievanceCategory,
    GrievanceStatus,
    LogisticsStatus,
    OrderStatus,
    PaymentMethod,
    PaymentStage,
    PaymentStatus,
)


class Order(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    """Binding sales contract created upon acceptance of an offer (Architecture Section 6.1 Item 15)."""

    __tablename__ = "orders"

    offer_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("offers.id", ondelete="RESTRICT"),
        unique=True,
        index=True,
        nullable=False,
    )
    buyer_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="RESTRICT"),
        index=True,
        nullable=False,
    )
    seller_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="RESTRICT"),
        index=True,
        nullable=False,
        doc="Seller user: farmer or FPO representative",
    )
    agreed_price_per_unit: Mapped[Decimal] = mapped_column(
        Numeric(12, 2),
        nullable=False,
        doc="Agreed price per unit in INR",
    )
    total_quantity: Mapped[Decimal] = mapped_column(
        Numeric(12, 2),
        nullable=False,
        doc="Final contract volume in crop standard units",
    )
    total_amount: Mapped[Decimal] = mapped_column(
        Numeric(14, 2),
        nullable=False,
        doc="Total transaction value (total_quantity * agreed_price_per_unit)",
    )
    is_fpo_bulk_order: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
        doc="True if this order fulfills an aggregated multi-farmer FPO bulk lot",
    )
    order_status: Mapped[OrderStatus] = mapped_column(
        SQLEnum(OrderStatus, name=OrderStatus.__pg_enum_name__, native_enum=True),
        default=OrderStatus.CONFIRMED,
        nullable=False,
    )

    __table_args__ = (
        CheckConstraint("agreed_price_per_unit > 0", name="chk_order_price_positive"),
        CheckConstraint("total_quantity > 0", name="chk_order_quantity_positive"),
        CheckConstraint("total_amount > 0", name="chk_order_amount_positive"),
    )

    # Relationships
    offer: Mapped["Offer"] = relationship("Offer", back_populates="order")  # type: ignore[name-defined] # noqa: F821
    buyer: Mapped["User"] = relationship("User", foreign_keys=[buyer_id])  # type: ignore[name-defined] # noqa: F821
    seller: Mapped["User"] = relationship("User", foreign_keys=[seller_id])  # type: ignore[name-defined] # noqa: F821
    allocations: Mapped[list["OrderLotAllocation"]] = relationship(
        "OrderLotAllocation",
        back_populates="order",
        cascade="all, delete-orphan",
    )
    logistics: Mapped[Optional["Logistics"]] = relationship(
        "Logistics",
        back_populates="order",
        uselist=False,
        cascade="all, delete-orphan",
    )
    payments: Mapped[list["PaymentRecord"]] = relationship(
        "PaymentRecord",
        back_populates="order",
        cascade="all, delete-orphan",
    )
    grievances: Mapped[list["Grievance"]] = relationship(
        "Grievance",
        back_populates="order",
        cascade="all, delete-orphan",
    )


class OrderLotAllocation(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    """Member payout and volume ledger for FPO bulk orders (Architecture Section 6.1 Item 16)."""

    __tablename__ = "order_lot_allocations"

    order_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("orders.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )
    lot_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("lots.id", ondelete="RESTRICT"),
        index=True,
        nullable=False,
    )
    farmer_user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="RESTRICT"),
        index=True,
        nullable=False,
    )
    allocated_quantity: Mapped[Decimal] = mapped_column(
        Numeric(12, 2),
        nullable=False,
        doc="Portion of the constituent farmer lot consumed by this order",
    )
    member_share_amount: Mapped[Decimal] = mapped_column(
        Numeric(14, 2),
        nullable=False,
        doc="Gross INR entitlement owed to the constituent farmer",
    )
    payout_status: Mapped[AllocationPayoutStatus] = mapped_column(
        SQLEnum(AllocationPayoutStatus, name=AllocationPayoutStatus.__pg_enum_name__, native_enum=True),
        default=AllocationPayoutStatus.PENDING,
        nullable=False,
    )
    disbursement_reference: Mapped[Optional[str]] = mapped_column(
        String(100),
        nullable=True,
        doc="Internal or banking transaction reference for FPO-to-farmer payout",
    )

    __table_args__ = (
        UniqueConstraint("order_id", "lot_id", name="uq_order_lot_allocation"),
        CheckConstraint("allocated_quantity > 0", name="chk_allocation_quantity_positive"),
        CheckConstraint("member_share_amount >= 0", name="chk_allocation_share_positive"),
    )

    # Relationships
    order: Mapped["Order"] = relationship("Order", back_populates="allocations")
    lot: Mapped["Lot"] = relationship("Lot")  # type: ignore[name-defined] # noqa: F821
    farmer: Mapped["User"] = relationship("User")  # type: ignore[name-defined] # noqa: F821


class Logistics(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    """Transportation dispatch and tracking record (Architecture Section 6.1 Item 17)."""

    __tablename__ = "logistics"

    order_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("orders.id", ondelete="RESTRICT"),
        unique=True,
        index=True,
        nullable=False,
    )
    transporter_name: Mapped[str] = mapped_column(String(150), nullable=False)
    vehicle_number: Mapped[str] = mapped_column(String(30), nullable=False)
    driver_phone: Mapped[str] = mapped_column(String(20), nullable=False)
    pickup_timestamp: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    delivery_timestamp: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    tracking_status: Mapped[LogisticsStatus] = mapped_column(
        SQLEnum(LogisticsStatus, name=LogisticsStatus.__pg_enum_name__, native_enum=True),
        default=LogisticsStatus.PENDING_PICKUP,
        nullable=False,
    )

    # Relationships
    order: Mapped["Order"] = relationship("Order", back_populates="logistics")


class PaymentRecord(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    """Financial payment audit record and UTR proof (Architecture Section 6.1 Item 18)."""

    __tablename__ = "payment_records"

    order_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("orders.id", ondelete="RESTRICT"),
        index=True,
        nullable=False,
    )
    payment_stage: Mapped[PaymentStage] = mapped_column(
        SQLEnum(PaymentStage, name=PaymentStage.__pg_enum_name__, native_enum=True),
        nullable=False,
    )
    amount: Mapped[Decimal] = mapped_column(
        Numeric(14, 2),
        nullable=False,
        doc="Transacted amount in INR",
    )
    payment_method: Mapped[PaymentMethod] = mapped_column(
        SQLEnum(PaymentMethod, name=PaymentMethod.__pg_enum_name__, native_enum=True),
        nullable=False,
    )
    transaction_reference: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        doc="Bank UTR number or payment verification reference string",
    )
    status: Mapped[PaymentStatus] = mapped_column(
        SQLEnum(PaymentStatus, name=PaymentStatus.__pg_enum_name__, native_enum=True),
        default=PaymentStatus.SUBMITTED,
        nullable=False,
    )

    __table_args__ = (
        CheckConstraint("amount > 0", name="chk_payment_amount_positive"),
    )

    # Relationships
    order: Mapped["Order"] = relationship("Order", back_populates="payments")


class Grievance(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    """Formal dispute ticket and resolution audit trail (Architecture Section 6.1 Item 19)."""

    __tablename__ = "grievances"

    order_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("orders.id", ondelete="RESTRICT"),
        index=True,
        nullable=False,
    )
    filed_by_user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="RESTRICT"),
        index=True,
        nullable=False,
    )
    issue_category: Mapped[GrievanceCategory] = mapped_column(
        SQLEnum(GrievanceCategory, name=GrievanceCategory.__pg_enum_name__, native_enum=True),
        nullable=False,
    )
    description: Mapped[str] = mapped_column(
        Text,
        nullable=False,
        doc="Detailed description of the issue or dispute",
    )
    status: Mapped[GrievanceStatus] = mapped_column(
        SQLEnum(GrievanceStatus, name=GrievanceStatus.__pg_enum_name__, native_enum=True),
        default=GrievanceStatus.OPEN,
        nullable=False,
    )
    admin_resolution_notes: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
        doc="Internal resolution notes and corrective actions recorded by admin",
    )

    # Relationships
    order: Mapped["Order"] = relationship("Order", back_populates="grievances")
    filed_by_user: Mapped["User"] = relationship("User", foreign_keys=[filed_by_user_id])  # type: ignore[name-defined] # noqa: F821
