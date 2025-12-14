class InfrastructureException(Exception):
    pass


class BusException(InfrastructureException):
    def __init__(self, message: str = "No handler found for this query or command."):
        super().__init__(message)


class SessionNotInitializedException(InfrastructureException):
    def __init__(self, message: str = "Session not initialized."):
        super().__init__(message)
