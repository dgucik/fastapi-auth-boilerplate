from dataclasses import dataclass

from auth.domain.exceptions import PasswordTooWeakException
from shared.domain.primitives import ValueObject


@dataclass(frozen=True)
class PlainPassword(ValueObject):
    """Value object representing a plain text password (validated)."""

    value: str

    def __post_init__(self) -> None:
        if len(self.value) < 8:
            raise PasswordTooWeakException(
                "Password must be at least 8 characters long."
            )

    def __str__(self) -> str:
        return self.value

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, PlainPassword):
            return False
        return self.value == other.value

    def __hash__(self) -> int:
        return hash(self.value)
