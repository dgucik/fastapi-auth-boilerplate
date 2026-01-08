import asyncio
import logging
import uuid
from datetime import UTC, datetime, timedelta
from enum import StrEnum
from typing import Any

from sqlalchemy import JSON, DateTime, Integer, String, select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker
from sqlalchemy.orm import Mapped, MappedAsDataclass, mapped_column

from shared.application.ports import DomainEventBus, DomainEventRegistry

logger = logging.getLogger(__name__)


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


class OutboxProcessor:
    MAX_ATTEMPTS = 5

    def __init__(
        self,
        session_factory: async_sessionmaker[AsyncSession],
        event_bus: DomainEventBus,
        registry: DomainEventRegistry,
        outbox_model: type[OutboxMixin],
        batch_size: int = 20,
    ):
        self._session_factory = session_factory
        self._event_bus = event_bus
        self._registry = registry
        self._outbox_model = outbox_model
        self._batch_size = batch_size

    async def _process_batch(self) -> int:
        async with self._session_factory() as session:
            stmt = (
                select(self._outbox_model)
                .where(
                    self._outbox_model.status == OutboxStatus.PENDING,
                    self._outbox_model.scheduled_at <= datetime.now(UTC),
                )
                .order_by(self._outbox_model.occurred_at.asc())
                .limit(self._batch_size)
                .with_for_update(skip_locked=True)
            )

            records = (await session.execute(stmt)).scalars().all()
            if not records:
                return 0

            processed_count = 0
            for record in records:
                try:
                    event_cls = self._registry.get_class(record.event_type)
                    event = event_cls.from_dict(record.payload)

                    await self._event_bus.publish(event)

                    record.status = OutboxStatus.PROCESSED
                    record.processed_at = datetime.now(UTC)
                    processed_count += 1
                    logger.debug(
                        f"Outbox event processed: {record.event_type} (id={record.id})"
                    )

                except Exception as e:
                    record.attempts += 1
                    record.last_error = str(e)

                    if record.attempts >= self.MAX_ATTEMPTS:
                        record.status = OutboxStatus.FAILED
                        logger.warning(
                            f"Outbox event failed permanently: {record.event_type} "
                            f"(id={record.id}, attempts={record.attempts})"
                        )
                    else:
                        delay = (2**record.attempts) * 10
                        record.scheduled_at = datetime.now(UTC) + timedelta(
                            seconds=delay
                        )
                        logger.debug(
                            f"Outbox event scheduled for retry: {record.event_type} "
                            f"(id={record.id}, attempt={record.attempts}, delay={delay}s)"  # noqa: E501
                        )

            await session.commit()
            if processed_count > 0:
                logger.info(f"Outbox batch processed: {processed_count} events")
            return len(records)

    async def run_forever(self, interval: float = 0.5) -> None:
        logger.info("Outbox processor started")
        while True:
            count = await self._process_batch()
            if count == 0:
                await asyncio.sleep(interval)
            else:
                logger.debug(f"Outbox processed {count} records, continuing...")
