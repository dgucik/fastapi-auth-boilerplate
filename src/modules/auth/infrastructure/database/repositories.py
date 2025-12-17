from typing import Any
from uuid import UUID

from sqlalchemy import Result, Select, select
from sqlalchemy.ext.asyncio import AsyncSession

from auth.domain.entities.account import Account
from auth.domain.repositories import AccountRepository
from auth.domain.value_objects import Email
from auth.infrastructure.database.models import AccountModel


class SqlAlchemyAccountRepository(AccountRepository):
    def __init__(self, session: AsyncSession):
        self._session = session

    async def get_by_email(self, email: Email) -> Account | None:
        stmt = select(AccountModel).where(AccountModel.email == email.value)
        return await self._execute(stmt)

    async def get_by_id(self, id: UUID) -> Account | None:
        stmt = select(AccountModel).where(AccountModel.id == id)
        return await self._execute(stmt)

    async def add(self, account: Account) -> None:
        account_model = self._to_model(account)
        account_model.domain_events = account.pull_events()
        self._session.add(account_model)

    def _to_domain(self, account_model: AccountModel) -> Account:
        return Account(
            id=account_model.id,
            email=Email(value=account_model.email),
            _password_hash=account_model.password_hash,
            is_verified=account_model.is_verified,
            is_superuser=account_model.is_superuser,
        )

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
