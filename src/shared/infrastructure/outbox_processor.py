import asyncio
from datetime import UTC, datetime, timedelta

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from shared.application.event_handling import DomainEventBus, DomainEventRegistry
from shared.infrastructure.outbox_mixin import OutboxMixin, OutboxStatus


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

            for record in records:
                try:
                    event_cls = self._registry.get_class(record.event_type)
                    event = event_cls.from_dict(record.payload)

                    await self._event_bus.publish(event)

                    record.status = OutboxStatus.PROCESSED
                    record.processed_at = datetime.now(UTC)

                except Exception as e:
                    record.attempts += 1
                    record.last_error = str(e)

                    if record.attempts >= self.MAX_ATTEMPTS:
                        record.status = OutboxStatus.FAILED
                    else:
                        delay = (2**record.attempts) * 10
                        record.scheduled_at = datetime.now(UTC) + timedelta(
                            seconds=delay
                        )

            await session.commit()
            return len(records)

    async def run_forever(self, interval: float = 0.5) -> None:
        while True:
            count = await self._process_batch()
            if count == 0:
                await asyncio.sleep(interval)
