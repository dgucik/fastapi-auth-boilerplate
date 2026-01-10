from shared.domain.exceptions import DomainException


class UsernameIsAlreadyTakenException(DomainException):
    def __init__(self, message: str = "Username is already taken."):
        super().__init__(message)


class UsernameIsTooShortException(DomainException):
    def __init__(
        self, message: str = "Username is too short. Minimum length is 3 characters."
    ):
        super().__init__(message)


class UserAlreadyExistsForAccountException(DomainException):
    def __init__(self, message: str = "User already exists for this account."):
        super().__init__(message)


class UserProfileNotFoundException(DomainException):
    def __init__(self, message: str = "User profile not found."):
        super().__init__(message)
