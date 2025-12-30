from shared.infrastructure.exceptions import InfrastructureException


class TokenExpiredException(InfrastructureException):
    def __init__(self, message: str = "The provided token has expired."):
        super().__init__(message)


class InvalidTokenException(InfrastructureException):
    def __init__(self, message: str = "The provided token is invalid."):
        super().__init__(message)
