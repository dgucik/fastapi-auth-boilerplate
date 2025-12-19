from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from auth.application.uow import AuthUnitOfWork
from auth.domain.repositories import AccountRepository
from auth.infrastructure.database.models import AuthOutboxEvent
from auth.infrastructure.database.repositories import SqlAlchemyAccountRepository
from shared.application.event_handling import EventBus, EventRegistry
from shared.infrastructure.base_uow import BaseSqlAlchemyUnitOfWork


class SqlAlchemyUnitOfWork(BaseSqlAlchemyUnitOfWork, AuthUnitOfWork):
    def __init__(
        self,
        session_factory: async_sessionmaker[AsyncSession],
        event_bus: EventBus,
        event_registry: EventRegistry,
    ):
        super().__init__(session_factory, event_bus, event_registry)
        self.accounts: AccountRepository

    async def __aenter__(self) -> "SqlAlchemyUnitOfWork":
        await super().__aenter__()
        if self._session is not None:
            self.accounts = SqlAlchemyAccountRepository(self._session)
        return self

    def _get_outbox_model(self) -> type[AuthOutboxEvent]:
        return AuthOutboxEvent
