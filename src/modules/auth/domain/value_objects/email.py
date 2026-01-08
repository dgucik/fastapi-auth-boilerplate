from dataclasses import dataclass

from email_validator import validate_email

from auth.domain.exceptions import InvalidEmailException
from shared.domain.primitives import ValueObject


@dataclass(frozen=True)
class Email(ValueObject):
    value: str

    def __post_init__(self) -> None:
        try:
            validate_email(self.value, check_deliverability=False)
        except Exception as e:
            raise InvalidEmailException from e

    def __str__(self) -> str:
        return self.value

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Email):
            return False
        return self.value == other.value

    def __hash__(self) -> int:
        return hash(self.value)
