from dataclasses import dataclass
from uuid import UUID

from shared.application.ports import Dto


@dataclass(frozen=True)
class AccountDto(Dto):
    """Data Transfer Object for account information."""

    id: UUID
    email: str
    is_superuser: bool
