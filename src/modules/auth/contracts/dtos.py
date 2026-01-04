from dataclasses import dataclass
from uuid import UUID


@dataclass(frozen=True)
class AuthAccountDto:
    id: UUID
    email: str
