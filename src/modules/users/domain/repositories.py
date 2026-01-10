from abc import ABC, abstractmethod
from uuid import UUID

from users.domain.entities.user import User
from users.domain.value_objects.username import Username


class UserRepository(ABC):
    """Abstract base class for User repository."""

    @abstractmethod
    async def get_by_id(self, user_id: UUID) -> User | None:
        """Retrieve a user by their unique identifier."""
        pass

    @abstractmethod
    async def get_by_account_id(self, account_id: UUID) -> User | None:
        """Retrieve a user by their account ID."""
        pass

    @abstractmethod
    async def get_by_username(self, username: Username) -> User | None:
        """Retrieve a user by their username."""
        pass

    @abstractmethod
    async def add(self, user: User) -> None:
        """Add a new user to the repository."""
        pass

    @abstractmethod
    async def update(self, user: User) -> None:
        """Updates user in repository."""
        pass

    @abstractmethod
    async def delete(self, user: User) -> None:
        "Deletes user from repository."
        pass
