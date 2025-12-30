import uuid
from datetime import UTC, datetime
from enum import StrEnum
from typing import Any

from sqlalchemy import JSON, DateTime, Integer, String
from sqlalchemy.orm import Mapped, MappedAsDataclass, mapped_column


class OutboxStatus(StrEnum):
    PENDING = "PENDING"
    PROCESSED = "PROCESSED"
    FAILED = "FAILED"


class OutboxMixin(MappedAsDataclass):
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
