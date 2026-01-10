from dataclasses import dataclass
from uuid import UUID


@dataclass(frozen=True)
class UserDto:
    id: UUID
    username: str
