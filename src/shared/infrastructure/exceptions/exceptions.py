class InfrastructureException(Exception):
    """Base exception for all infrastructure layer errors"""

    pass


class BusException(InfrastructureException):
    """Exception for bus-related errors (command/query/event bus)"""

    def __init__(self, message: str = "No handler found for this query or command."):
        super().__init__(message)


class SessionNotInitializedException(InfrastructureException):
    """Exception for uninitialized database sessions"""

    def __init__(self, message: str = "Session not initialized."):
        super().__init__(message)


class DatabaseConnectionException(InfrastructureException):
    """Base exception for database connection errors"""

    def __init__(self, message: str = "Database connection error."):
        super().__init__(message)


class ExternalServiceException(InfrastructureException):
    """Base exception for external service integration errors"""

    def __init__(self, message: str = "External service error."):
        super().__init__(message)


class ConsumerNotStartedException(InfrastructureException):
    """Exception for consumer not started."""

    def __init__(self, message: str = "Consumer not started."):
        super().__init__(message)


class ProducerNotStartedException(InfrastructureException):
    """Exception for producer not started."""

    def __init__(self, message: str = "Producer not started."):
        super().__init__(message)


class PermissionDeniedException(InfrastructureException):
    """Raised when actor has no permission to perform action."""

    def __init__(self, message: str = "No permission to perform this action."):
        super().__init__(message)
