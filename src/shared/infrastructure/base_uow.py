from types import TracebackType

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from shared.application.event_handling import DomainEventBus
from shared.application.uow import UnitOfWork
from shared.domain.events import DomainEvent
from shared.infrastructure.exceptions import SessionNotInitializedException


class BaseSqlAlchemyUnitOfWork(UnitOfWork):
    def __init__(
        self,
        session_factory: async_sessionmaker[AsyncSession],
        event_bus: DomainEventBus,
    ):
        self._session_factory = session_factory
        self._session: AsyncSession | None = None
        self._event_bus = event_bus

    async def __aenter__(self) -> "BaseSqlAlchemyUnitOfWork":
        self._session = self._session_factory()
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: TracebackType | None,
    ) -> None:
        if exc_type:
            await self.rollback()

    async def commit(self) -> None:
        if not self._session:
            raise SessionNotInitializedException

        events = self._pull_events_from_models()

        await self._session.flush()

        for event in events:
            await self._event_bus.publish(event, only_async=False)

        await self._session.commit()

        for event in events:
            await self._event_bus.publish(event, only_async=True)

    async def rollback(self) -> None:
        if not self._session:
            raise SessionNotInitializedException

        await self._session.rollback()

    def _pull_events_from_models(self) -> list[DomainEvent]:
        if not self._session:
            return []

        objs = list(self._session.new) + list(self._session.dirty)

        events: list[DomainEvent] = []
        for obj in objs:
            model_events = getattr(obj, "domain_events", None)
            if model_events:
                events.extend(model_events)
                obj.domain_events = []

        return events
