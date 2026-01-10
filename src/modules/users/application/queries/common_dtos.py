from dataclasses import dataclass
from uuid import UUID


@dataclass(frozen=True)
class UserDto:
    """Data Transfer Object for User information.

    Attributes:
        id: User UUID.
        username: User display name.
    """

    id: UUID
    username: str
