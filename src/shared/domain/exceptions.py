class DomainException(Exception):
    """Base exception for all domain-related errors"""

    pass


class ValidationException(DomainException):
    """Base exception for data validation errors"""

    pass


class BusinessRuleViolationException(DomainException):
    """Base exception for business rule violations"""

    pass


class EntityNotFoundException(DomainException):
    """Base exception for missing entities"""

    pass


class EntityAlreadyExistsException(DomainException):
    """Base exception for duplicate entities"""

    pass
