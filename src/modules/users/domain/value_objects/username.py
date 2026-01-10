from dataclasses import dataclass

from users.domain.exceptions import UsernameIsTooShortException


@dataclass(frozen=True)
class Username:
    """Username value object.

    Attributes:
        value: The username string.
    """

    value: str

    def __post_init__(self) -> None:
        """Validates the username on initialization.

        Raises:
            UsernameIsTooShortException: If username is shorter than 3 chars.
        """
        if not self.value or len(self.value) < 3:
            raise UsernameIsTooShortException

    def __str__(self) -> str:
        return self.value
