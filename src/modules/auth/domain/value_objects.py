from dataclasses import dataclass

from email_validator import validate_email
from shared.domain.primitives import ValueObject

from auth.domain.exceptions import InvalidEmailException, PasswordTooWeakException


@dataclass(frozen=True)
class Email(ValueObject):
    value: str

    def __post_init__(self) -> None:
        try:
            validate_email(self.value, check_deliverability=False)
        except Exception as err:
            raise InvalidEmailException from err

    def __str__(self) -> str:
        return self.value

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Email):
            return False
        return self.value == other.value

    def __hash__(self) -> int:
        return hash(self.value)


@dataclass(frozen=True)
class PlainPassword(ValueObject):
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
