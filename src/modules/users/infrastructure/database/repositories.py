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
    """SQLAlchemy implementation of UserRepository.

    Args:
        session: Async SQLAlchemy session.
    """

    def __init__(self, session: AsyncSession):
        """Initializes the repository.

        Args:
            session: Async SQLAlchemy session.
        """
        self._session = session

    async def get_by_id(self, id: UUID) -> User | None:
        """Retrieves user by ID.

        Args:
            id: User UUID.

        Returns:
            User: User entity or None.
        """
        stmt = select(UserModel).where(UserModel.id == id)
        return await self._execute(stmt)

    async def get_by_account_id(self, account_id: UUID) -> User | None:
        """Retrieves user by account ID.

        Args:
            account_id: Account UUID.

        Returns:
            User: User entity or None.
        """
        stmt = select(UserModel).where(UserModel.account_id == account_id)
        return await self._execute(stmt)

    async def get_by_username(self, username: Username) -> User | None:
        """Retrieves user by username.

        Args:
            username: Username value object.

        Returns:
            User: User entity or None.
        """
        stmt = select(UserModel).where(UserModel.username == username.value)
        return await self._execute(stmt)

    async def add(self, user: User) -> None:
        """Adds a new user.

        Args:
            user: User entity.
        """
        self._register(user)
        user_model = self._to_model(user)
        self._session.add(user_model)

    async def update(self, user: User) -> None:
        """Updates an existing user.

        Args:
            user: User entity.
        """
        self._register(user)
        user_model = self._to_model(user)
        await self._session.merge(user_model)

    async def delete(self, user: User) -> None:
        """Deletes a user.

        Args:
            user: User entity.
        """
        self._register(user)
        user_model = self._to_model(user)
        await self._session.delete(user_model)

    def _to_domain(self, user_model: UserModel) -> User:
        """Converts model to domain entity.

        Args:
            user_model: Database model.

        Returns:
            User: Domain entity.
        """
        user = User(
            id=user_model.id,
            account_id=user_model.account_id,
            username=Username(user_model.username),
        )
        return self._register(user)

    def _to_model(self, user: User) -> UserModel:
        """Converts domain entity to model.

        Args:
            user: Domain entity.

        Returns:
            UserModel: Database model.
        """
        return UserModel(
            id=user.id,
            account_id=user.account_id,
            username=user.username.value,
        )

    async def _execute(self, stmt: Select[Any]) -> User | None:
        """Executes selection query.

        Args:
            stmt: SQLAlchemy select statement.

        Returns:
            User: User entity or None from first result.
        """
        result: Result[Any] = await self._session.execute(stmt)
        user_model = result.scalar_one_or_none()
        return self._to_domain(user_model) if user_model else None
