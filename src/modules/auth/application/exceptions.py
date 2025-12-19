from shared.application.exceptions import ApplicationException


class PasswordsDoNotMatchException(ApplicationException):
    def __init__(self, message: str = "The provided passwords do not match."):
        super().__init__(message)


class AccountDoesNotExistException(ApplicationException):
    def __init__(self, message: str = "The specified account does not exist."):
        super().__init__(message)
