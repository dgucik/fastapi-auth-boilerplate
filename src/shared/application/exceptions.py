class ApplicationException(Exception):
    """Base exception for all application layer errors"""

    pass


class CommandHandlingException(ApplicationException):
    """Base exception for command handling errors"""

    pass


class QueryExecutionException(ApplicationException):
    """Base exception for query execution errors"""

    pass


class EventReconstructionException(ApplicationException):
    """Base exception for event reconstruction errors"""

    pass


class UnitOfWorkException(ApplicationException):
    """Base exception for unit of work errors"""

    pass
