"""SQLAlchemy 2.0 DeclarativeBase and reusable model mixins.

Step 4B.1 Foundation: Establishes the canonical Base class and standard mixins
for UUID primary keys and timezone-aware UTC timestamps.
"""

from datetime import datetime, timezone
import uuid
from sqlalchemy import DateTime, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


def utc_now() -> datetime:
    """Return the current timestamp with explicit UTC timezone."""
    return datetime.now(timezone.utc)


class Base(DeclarativeBase):
    """Canonical SQLAlchemy 2.0 DeclarativeBase for all domain models."""
    pass


class UUIDPrimaryKeyMixin:
    """Reusable mixin providing a UUIDv4 primary key.

    Uses PostgreSQL native UUID type with client-side default fallback.
    sort_order=-100 ensures the 'id' column appears first in generated DDL.
    """

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        sort_order=-100,
        doc="Surrogate UUIDv4 primary key identifier",
    )


class TimestampMixin:
    """Reusable mixin providing timezone-aware created_at and updated_at UTC timestamps.

    server_default=func.now() guarantees database-level timestamp assignment.
    default/onupdate provide application-level Python UTC fallbacks.
    """

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        default=utc_now,
        nullable=False,
        doc="Record creation timestamp with UTC timezone",
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=utc_now,
        default=utc_now,
        nullable=False,
        doc="Record last-modification timestamp with UTC timezone",
    )
