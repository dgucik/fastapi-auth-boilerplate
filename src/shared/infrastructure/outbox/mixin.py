import uuid
from datetime import UTC, datetime
from enum import StrEnum
from typing import Any

from sqlalchemy import JSON, DateTime, Integer, String
from sqlalchemy.orm import Mapped, MappedAsDataclass, mapped_column


class OutboxStatus(StrEnum):
    """Enumeration of outbox message statuses."""

    PENDING = "PENDING"
    PROCESSED = "PROCESSED"
    FAILED = "FAILED"


class OutboxMixin(MappedAsDataclass):
    """Mixin for adding outbox functionality to SQLAlchemy models.

    Attributes:
        id: Unique identifier.
        event_type: Name of the event.
        payload: JSON payload of the event.
        status: Processing status.
        attempts: Number of processing attempts.
        scheduled_at: Next scheduled processing time.
        last_error: Error message if last attempt failed.
        occurred_at: Timestamp of event occurrence.
        processed_at: Timestamp of successful processing.
    """

    id: Mapped[uuid.UUID] = mapped_column(
        primary_key=True, default=uuid.uuid4, init=False
    )
    event_type: Mapped[str] = mapped_column(String(255))

    payload: Mapped[dict[str, Any]] = mapped_column(JSON)

    status: Mapped[OutboxStatus] = mapped_column(
        String(20), default=OutboxStatus.PENDING, index=True, init=False
    )

    attempts: Mapped[int] = mapped_column(Integer, default=0, init=False)

    scheduled_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
        index=True,
        init=False,
    )

    last_error: Mapped[str | None] = mapped_column(String, nullable=True, init=False)

    occurred_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(UTC), init=False
    )
    processed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True, index=True, init=False
    )
