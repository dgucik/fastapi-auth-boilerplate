import logging
from abc import abstractmethod
from types import TracebackType

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from shared.application.ports import DomainEventRegistry, UnitOfWork
from shared.domain.registry import AggregateRegistry
from shared.infrastructure.exceptions.exceptions import SessionNotInitializedException
from shared.infrastructure.outbox.mixin import OutboxMixin

logger = logging.getLogger(__name__)


class BaseSqlAlchemyUnitOfWork(UnitOfWork):
    def __init__(
        self,
        session_factory: async_sessionmaker[AsyncSession],
        event_registry: DomainEventRegistry,
    ):
        self._session_factory = session_factory
        self._session: AsyncSession | None = None
        self._registry = event_registry

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

        events = AggregateRegistry.pull_events()
        outbox_model = self._get_outbox_model()

        for event in events:
            event_name = self._registry.get_name(type(event))
            self._session.add(
                outbox_model(event_type=event_name, payload=event.to_dict())
            )

        await self._session.commit()
        AggregateRegistry.clear()
        logger.debug("UnitOfWork committed successfully")

    async def rollback(self) -> None:
        if not self._session:
            raise SessionNotInitializedException

        await self._session.rollback()
        logger.debug("UnitOfWork rolled back")

    @abstractmethod
    def _get_outbox_model(self) -> type[OutboxMixin]:
        pass
