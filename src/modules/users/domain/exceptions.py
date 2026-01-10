from shared.domain.exceptions import DomainException


class UsernameIsAlreadyTakenException(DomainException):
    """Exception raised when a username is already occupied."""

    def __init__(self, message: str = "Username is already taken."):
        super().__init__(message)


class UsernameIsTooShortException(DomainException):
    """Exception raised when a username is too short."""

    def __init__(
        self, message: str = "Username is too short. Minimum length is 3 characters."
    ):
        super().__init__(message)


class UserAlreadyExistsForAccountException(DomainException):
    """Exception raised when a user profile already exists for an account."""

    def __init__(self, message: str = "User already exists for this account."):
        super().__init__(message)


class UserProfileNotFoundException(DomainException):
    """Exception raised when a user profile is not found."""

    def __init__(self, message: str = "User profile not found."):
        super().__init__(message)
