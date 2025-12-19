import asyncio
from datetime import UTC, datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from shared.application.event_handling import EventBus, EventRegistry
from shared.infrastructure.outbox_mixin import OutboxMixin


class OutboxProcessor:
    def __init__(
        self,
        session_factory: async_sessionmaker[AsyncSession],
        bus: EventBus,
        registry: EventRegistry,
        outbox_model: type[OutboxMixin],
        batch_size: int = 20,
    ):
        self._session_factory = session_factory
        self._bus = bus
        self._registry = registry
        self._outbox_model = outbox_model
        self._batch_size = batch_size

    async def _process_batch(self) -> int:
        async with self._session_factory() as session:
            stmt = (
                select(self._outbox_model)
                .where(self._outbox_model.processed_at.is_(None))
                .order_by(self._outbox_model.occurred_at.asc())
                .limit(self._batch_size)
                .with_for_update(skip_locked=True)
            )

            records = (await session.execute(stmt)).scalars().all()
            if not records:
                return 0

            for record in records:
                event_cls = self._registry.get_class(record.event_type)

                event = event_cls.from_dict(record.payload)

                await self._bus.publish(event)

                record.processed_at = datetime.now(UTC)
            await session.commit()
            return len(records)

    async def run_forever(self, interval: float = 0.5) -> None:
        while True:
            count = await self._process_batch()
            if count == 0:
                await asyncio.sleep(interval)
