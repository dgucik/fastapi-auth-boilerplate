from types import TracebackType

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from shared.application.event_handling import DomainEventBus
from shared.application.uow import UnitOfWork
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

        await self._session.commit()

    async def rollback(self) -> None:
        if not self._session:
            raise SessionNotInitializedException

        await self._session.rollback()
