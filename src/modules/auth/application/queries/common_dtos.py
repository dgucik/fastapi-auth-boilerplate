from dataclasses import dataclass
from uuid import UUID

from shared.application.ports import Dto


@dataclass(frozen=True)
class AccountDto(Dto):
    id: UUID
    email: str
