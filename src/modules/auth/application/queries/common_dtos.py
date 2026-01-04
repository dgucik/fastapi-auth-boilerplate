from dataclasses import dataclass
from uuid import UUID

from shared.application.cqrs import Dto


@dataclass(frozen=True)
class AccountDto(Dto):
    id: UUID
    email: str
