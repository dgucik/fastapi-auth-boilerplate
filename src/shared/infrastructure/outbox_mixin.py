import uuid
from datetime import UTC, datetime
from typing import Any

from sqlalchemy import JSON, DateTime, String
from sqlalchemy.orm import Mapped, MappedAsDataclass, mapped_column


class OutboxMixin(MappedAsDataclass):
    id: Mapped[uuid.UUID] = mapped_column(
        primary_key=True, default=uuid.uuid4, init=False
    )
    event_type: Mapped[str] = mapped_column(String(255))

    payload: Mapped[dict[str, Any]] = mapped_column(JSON)

    occurred_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(UTC), init=False
    )
    processed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True, index=True, init=False
    )
