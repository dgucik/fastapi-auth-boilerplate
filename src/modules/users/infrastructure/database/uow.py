from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker
from users.application.uow import UsersUnitOfWork
from users.domain.repositories import UserRepository
from users.infrastructure.database.models import UsersOutboxEvent
from users.infrastructure.database.repositories import SqlAlchemyUserRepository

from shared.application.ports import DomainEventRegistry
from shared.infrastructure.database.base_uow import BaseSqlAlchemyUnitOfWork


class SqlAlchemyUsersUnitOfWork(BaseSqlAlchemyUnitOfWork, UsersUnitOfWork):
    def __init__(
        self,
        session_factory: async_sessionmaker[AsyncSession],
        event_registry: DomainEventRegistry,
    ):
        super().__init__(session_factory, event_registry)
        self.users: UserRepository

    async def __aenter__(self) -> "SqlAlchemyUsersUnitOfWork":
        await super().__aenter__()
        if self._session is not None:
            self.users = SqlAlchemyUserRepository(self._session)
        return self

    def _get_outbox_model(self) -> type[UsersOutboxEvent]:
        return UsersOutboxEvent
