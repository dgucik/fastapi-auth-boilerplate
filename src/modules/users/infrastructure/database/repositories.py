from typing import Any
from uuid import UUID

from sqlalchemy import Result, Select, select
from sqlalchemy.ext.asyncio import AsyncSession
from users.domain.entities.user import User
from users.domain.repositories import UserRepository
from users.domain.value_objects.username import Username
from users.infrastructure.database.models import UserModel

from shared.infrastructure.database.base_repository import BaseSqlAlchemyRepository


class SqlAlchemyUserRepository(UserRepository, BaseSqlAlchemyRepository[User]):
    def __init__(self, session: AsyncSession):
        self._session = session

    async def get_by_id(self, id: UUID) -> User | None:
        stmt = select(UserModel).where(UserModel.id == id)
        return await self._execute(stmt)

    async def get_by_account_id(self, account_id: UUID) -> User | None:
        stmt = select(UserModel).where(UserModel.account_id == account_id)
        return await self._execute(stmt)

    async def get_by_username(self, username: Username) -> User | None:
        stmt = select(UserModel).where(UserModel.username == username.value)
        return await self._execute(stmt)

    async def add(self, user: User) -> None:
        self._register(user)
        user_model = UserModel(
            id=user.id,
            account_id=user.account_id,
            username=user.username.value,
        )
        self._session.add(user_model)

    def _to_domain(self, user_model: UserModel) -> User:
        user = User(
            id=user_model.id,
            account_id=user_model.account_id,
            username=Username(user_model.username),
        )
        return self._register(user)

    async def _execute(self, stmt: Select[Any]) -> User | None:
        result: Result[Any] = await self._session.execute(stmt)
        user_model = result.scalar_one_or_none()
        return self._to_domain(user_model) if user_model else None
