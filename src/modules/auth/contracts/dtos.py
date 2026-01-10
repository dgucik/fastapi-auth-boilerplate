from dataclasses import dataclass
from uuid import UUID


@dataclass(frozen=True)
class AuthAccountDto:
    """Public Data Transfer Object for account information."""

    id: UUID
    email: str
    is_superuser: bool
