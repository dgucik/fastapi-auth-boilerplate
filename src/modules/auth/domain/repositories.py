from abc import ABC, abstractmethod
from uuid import UUID

from auth.domain.entities.account import Account
from auth.domain.value_objects.email import Email


class AccountRepository(ABC):
    """Interface for Account persistence."""

    @abstractmethod
    async def add(self, entity: Account) -> None:
        """Persists a new account."""
        pass

    @abstractmethod
    async def update(self, entity: Account) -> None:
        """Updates an existing account."""
        pass

    @abstractmethod
    async def get_by_email(self, email: Email) -> Account | None:
        """Retrieves an account by email."""
        pass

    @abstractmethod
    async def get_by_id(self, id: UUID) -> Account | None:
        """Retrieves an account by ID."""
        pass
