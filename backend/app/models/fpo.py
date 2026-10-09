"""SQLAlchemy models for FPOs and member farmer affiliations."""

from datetime import datetime
from typing import Optional
import uuid
from sqlalchemy import DateTime, Enum as SQLEnum, ForeignKey, String, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.models.base import Base, TimestampMixin, UUIDPrimaryKeyMixin
from app.models.enums import FPOMembershipStatus


class FPO(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    """Registered Farmer Producer Organization entity (Architecture Section 6.1 Item 3)."""

    __tablename__ = "fpos"

    name: Mapped[str] = mapped_column(String(200), nullable=False)
    registration_number: Mapped[str] = mapped_column(
        String(100),
        unique=True,
        index=True,
        nullable=False,
        doc="Official incorporation / cooperative society registration ID",
    )
    district: Mapped[str] = mapped_column(String(100), index=True, nullable=False)
    state: Mapped[str] = mapped_column(String(100), nullable=False)
    created_by_user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="RESTRICT"),
        nullable=False,
        doc="FPO Representative administrator account that registered this organization",
    )

    created_by_user: Mapped["User"] = relationship("User")  # type: ignore[name-defined] # noqa: F821
    memberships: Mapped[list["FPOMembership"]] = relationship(
        "FPOMembership",
        back_populates="fpo",
        cascade="all, delete-orphan",
    )
    managed_lots: Mapped[list["Lot"]] = relationship(  # type: ignore[name-defined] # noqa: F821
        "Lot",
        back_populates="fpo",
        foreign_keys="[Lot.fpo_id]",
    )


class FPOMembership(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    """Affiliation record binding a Farmer to an FPO (Architecture Section 6.1 Item 4)."""

    __tablename__ = "fpo_memberships"

    fpo_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("fpos.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )
    farmer_user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )
    status: Mapped[FPOMembershipStatus] = mapped_column(
        SQLEnum(FPOMembershipStatus, name=FPOMembershipStatus.__pg_enum_name__, native_enum=True),
        default=FPOMembershipStatus.PENDING,
        nullable=False,
    )
    joined_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        doc="Timestamp when membership was formally approved by the FPO representative",
    )

    __table_args__ = (
        UniqueConstraint("fpo_id", "farmer_user_id", name="uq_fpo_membership_farmer"),
    )

    fpo: Mapped["FPO"] = relationship("FPO", back_populates="memberships")
    farmer_user: Mapped["User"] = relationship(  # type: ignore[name-defined] # noqa: F821
        "User",
        back_populates="fpo_memberships",
    )
