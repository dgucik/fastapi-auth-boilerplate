from shared.application.exceptions import CommandHandlingException


class PasswordsDoNotMatchException(CommandHandlingException):
    """Password confirmation mismatch in command processing"""

    def __init__(self, message: str = "The provided passwords do not match."):
        super().__init__(message)


class AccountDoesNotExistException(CommandHandlingException):
    """Account not found during command execution"""

    def __init__(self, message: str = "The specified account does not exist."):
        super().__init__(message)


class PasswordMustBeDifferentException(CommandHandlingException):
    def __init__(
        self, message: str = "New password must be different from the old password."
    ):
        super().__init__(message)
