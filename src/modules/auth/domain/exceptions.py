from shared.domain.exceptions import (
    BusinessRuleViolationException,
    EntityAlreadyExistsException,
    ValidationException,
)


class EmailAlreadyExistsException(EntityAlreadyExistsException):
    """Email already exists in the system"""

    def __init__(self, message: str = "An account with this email already exists."):
        super().__init__(message)


class InvalidEmailException(ValidationException):
    """Invalid email format"""

    def __init__(self, message: str = "Invalid email address format."):
        super().__init__(message)


class PasswordTooWeakException(ValidationException):
    """Password does not meet requirements"""

    def __init__(self, message: str = "Password is too weak."):
        super().__init__(message)


class AccountNotVerifiedException(BusinessRuleViolationException):
    """Account verification required"""

    def __init__(self, message: str = "Email address is not verified."):
        super().__init__(message)


class InvalidPasswordException(BusinessRuleViolationException):
    """Invalid credentials"""

    def __init__(self, message: str = "Invalid email or password."):
        super().__init__(message)


class AccountAlreadyVerifiedException(BusinessRuleViolationException):
    """Account already verified"""

    def __init__(self, message: str = "Account already verified."):
        super().__init__(message)
