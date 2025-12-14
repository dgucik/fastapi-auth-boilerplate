from shared.domain.exceptions import DomainException


class EmailAlreadyExistsException(DomainException):
    def __init__(self, message: str = "An account with this email already exists."):
        super().__init__(message)


class PasswordTooWeakException(DomainException):
    def __init__(self, message: str = "Password is too weak.") -> None:
        super().__init__(message)


class InvalidEmailException(DomainException):
    def __init__(self, message: str = "Invalid email address format.") -> None:
        super().__init__(message)


class AccountNotVerifiedException(DomainException):
    def __init__(self, message: str = "Email address is not verified.") -> None:
        super().__init__(message)


class InvalidPasswordException(DomainException):
    def __init__(self, message: str = "Invalid email or password.") -> None:
        super().__init__(message)
