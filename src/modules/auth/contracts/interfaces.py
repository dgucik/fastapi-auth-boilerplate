from abc import ABC, abstractmethod
from uuid import UUID

from auth.contracts.dtos import AuthAccountDto


class AuthModuleContract(ABC):
    @abstractmethod
    async def get_account_by_token(self, token: str) -> AuthAccountDto:
        pass

    @abstractmethod
    async def get_account_by_id(self, id: UUID) -> AuthAccountDto:
        pass
