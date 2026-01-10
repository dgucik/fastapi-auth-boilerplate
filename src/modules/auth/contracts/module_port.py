from abc import ABC, abstractmethod
from uuid import UUID

from auth.contracts.dtos import AuthAccountDto


class AuthModulePort(ABC):
    """Public interface for the Auth module."""

    @abstractmethod
    async def get_account_by_token(self, token: str) -> AuthAccountDto:
        """Retrieves account details using an access token."""
        pass

    @abstractmethod
    async def get_account_by_id(self, id: UUID) -> AuthAccountDto:
        """Retrieves account details by ID."""
        pass
