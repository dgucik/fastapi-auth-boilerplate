from dataclasses import dataclass

from users.domain.exceptions import UsernameIsTooShortException


@dataclass(frozen=True)
class Username:
    value: str

    def __post_init__(self) -> None:
        if not self.value or len(self.value) < 3:
            raise UsernameIsTooShortException

    def __str__(self) -> str:
        return self.value
