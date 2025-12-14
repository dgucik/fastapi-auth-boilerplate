from abc import ABC, abstractmethod
from uuid import UUID

from auth.domain.account import Account
from auth.domain.value_objects import Email


class AccountRepository(ABC):
    @abstractmethod
    async def add(self, entity: Account) -> None:
        pass

    @abstractmethod
    async def get_by_email(self, email: Email) -> Account | None:
        pass

    @abstractmethod
    async def get_by_id(self, id: UUID) -> Account | None:
        pass
