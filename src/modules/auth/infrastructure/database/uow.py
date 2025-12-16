from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from auth.application.uow import AuthUnitOfWork
from auth.domain.repositories import AccountRepository
from auth.infrastructure.database.repositories import SqlAlchemyAccountRepository
from shared.infrastructure.base_uow import BaseSqlAlchemyUnitOfWork


class SqlAlchemyUnitOfWork(BaseSqlAlchemyUnitOfWork, AuthUnitOfWork):
    def __init__(self, session_factory: async_sessionmaker[AsyncSession]):
        super().__init__(session_factory)
        self.accounts: AccountRepository

    async def __aenter__(self) -> "SqlAlchemyUnitOfWork":
        await super().__aenter__()
        if self._session is not None:
            self.accounts = SqlAlchemyAccountRepository(self._session)
        return self
