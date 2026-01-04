class AuthModuleContractException(Exception):
    pass


class ContractAccountNotFoundException(AuthModuleContractException):
    def __init__(self, message: str = "Account not found."):
        super().__init__(message)


class ContractTokenExpiredException(AuthModuleContractException):
    def __init__(self, message: str = "Token has expired."):
        super().__init__(message)


class ContractInvalidTokenException(AuthModuleContractException):
    def __init__(self, message: str = "Invalid token."):
        super().__init__(message)
