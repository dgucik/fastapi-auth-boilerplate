from typing import Any
from uuid import UUID

from sqlalchemy import Result, Select, select
from sqlalchemy.ext.asyncio import AsyncSession

from auth.domain.entities.account import Account
from auth.domain.repositories import AccountRepository
from auth.domain.value_objects import Email
from auth.infrastructure.database.models import AccountModel
from shared.infrastructure.repositories import BaseSqlAlchemyRepository


class SqlAlchemyAccountRepository(AccountRepository, BaseSqlAlchemyRepository[Account]):
    def __init__(self, session: AsyncSession):
        self._session = session

    async def get_by_email(self, email: Email) -> Account | None:
        stmt = select(AccountModel).where(AccountModel.email == email.value)
        return await self._execute(stmt)

    async def get_by_id(self, id: UUID) -> Account | None:
        stmt = select(AccountModel).where(AccountModel.id == id)
        return await self._execute(stmt)

    async def add(self, account: Account) -> None:
        self._register(account)
        account_model = self._to_model(account)
        self._session.add(account_model)

    async def update(self, account: Account) -> None:
        self._register(account)
        account_model = self._to_model(account)
        await self._session.merge(account_model)

    def _to_domain(self, account_model: AccountModel) -> Account:
        account = Account(
            id=account_model.id,
            email=Email(value=account_model.email),
            _password_hash=account_model.password_hash,
            is_verified=account_model.is_verified,
            is_superuser=account_model.is_superuser,
        )
        return self._register(account)

    def _to_model(self, account: Account) -> AccountModel:
        return AccountModel(
            id=account.id,
            email=account.email.value,
            password_hash=account._password_hash,
            is_verified=account.is_verified,
            is_superuser=account.is_superuser,
        )

    async def _execute(self, stmt: Select[Any]) -> Account | None:
        result: Result[Any] = await self._session.execute(stmt)
        account_model = result.scalar_one_or_none()
        return self._to_domain(account_model) if account_model else None
