class AuthModuleContractException(Exception):
    """Base exception for Auth module contract violations."""

    pass


class ContractAccountNotFoundException(AuthModuleContractException):
    """Raised when account is not found via contract."""

    def __init__(self, message: str = "Account not found."):
        super().__init__(message)


class ContractTokenExpiredException(AuthModuleContractException):
    """Raised when token is expired via contract."""

    def __init__(self, message: str = "Token has expired."):
        super().__init__(message)


class ContractInvalidTokenException(AuthModuleContractException):
    """Raised when token is invalid via contract."""

    def __init__(self, message: str = "Invalid token."):
        super().__init__(message)
