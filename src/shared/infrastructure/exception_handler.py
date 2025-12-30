from fastapi import HTTPException, Request
from fastapi.responses import JSONResponse
from starlette.status import (
    HTTP_400_BAD_REQUEST,
    HTTP_404_NOT_FOUND,
    HTTP_409_CONFLICT,
    HTTP_500_INTERNAL_SERVER_ERROR,
    HTTP_503_SERVICE_UNAVAILABLE,
)

from shared.application.exceptions import (
    ApplicationException,
    CommandHandlingException,
    EventReconstructionException,
    QueryExecutionException,
    UnitOfWorkException,
)
from shared.domain.exceptions import (
    BusinessRuleViolationException,
    DomainException,
    EntityAlreadyExistsException,
    EntityNotFoundException,
    ValidationException,
)
from shared.infrastructure.exceptions import (
    BusException,
    DatabaseConnectionException,
    ExternalServiceException,
    InfrastructureException,
    SessionNotInitializedException,
)


class GlobalExceptionHandler:
    def __init__(self) -> None:
        # Map exceptions to HTTP status codes
        self.status_code_mapping = {
            # Domain layer - typically 4xx (client errors)
            ValidationException: HTTP_400_BAD_REQUEST,
            EntityNotFoundException: HTTP_404_NOT_FOUND,
            EntityAlreadyExistsException: HTTP_409_CONFLICT,
            BusinessRuleViolationException: HTTP_409_CONFLICT,
            # Application layer - typically 500 (internal error)
            CommandHandlingException: HTTP_500_INTERNAL_SERVER_ERROR,
            QueryExecutionException: HTTP_500_INTERNAL_SERVER_ERROR,
            EventReconstructionException: HTTP_500_INTERNAL_SERVER_ERROR,
            UnitOfWorkException: HTTP_500_INTERNAL_SERVER_ERROR,
            DatabaseConnectionException: HTTP_503_SERVICE_UNAVAILABLE,
            ExternalServiceException: HTTP_503_SERVICE_UNAVAILABLE,
        }

        # Map exceptions to error types
        self.error_type_mapping = {
            ValidationException: "validation_error",
            EntityNotFoundException: "entity_not_found",
            EntityAlreadyExistsException: "entity_already_exists",
            BusinessRuleViolationException: "business_rule_violation",
            CommandHandlingException: "command_handling_error",
            QueryExecutionException: "query_execution_error",
            EventReconstructionException: "event_reconstruction_error",
            UnitOfWorkException: "unit_of_work_error",
            DatabaseConnectionException: "database_connection_error",
            ExternalServiceException: "external_service_error",
        }

    async def __call__(self, request: Request, exc: Exception) -> JSONResponse:
        if isinstance(exc, SHARED_EXCEPTIONS):
            return await self._handle_shared_exception(exc)
        elif isinstance(exc, HTTPException):
            return await self._handle_http_exception(exc)
        else:
            return await self._handle_unexpected_exception(exc)

    async def _handle_shared_exception(self, exc: Exception) -> JSONResponse:
        status_code = HTTP_500_INTERNAL_SERVER_ERROR
        error_type = "shared_layer_error"

        for mapped_exc_type, mapped_status_code in self.status_code_mapping.items():
            if isinstance(exc, mapped_exc_type):
                status_code = mapped_status_code
                break

        for mapped_exc_type, mapped_error_type in self.error_type_mapping.items():
            if isinstance(exc, mapped_exc_type):
                error_type = mapped_error_type
                break

        return JSONResponse(
            status_code=status_code,
            content={
                "error": error_type,
                "detail": str(exc),
                "exception_type": type(exc).__name__,
            },
        )

    async def _handle_http_exception(self, exc: HTTPException) -> JSONResponse:
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "error": "http_error",
                "detail": exc.detail,
            },
        )

    async def _handle_unexpected_exception(self, exc: Exception) -> JSONResponse:
        return JSONResponse(
            status_code=HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "error": "internal_server_error",
                "detail": "An unexpected error occurred",
            },
        )


# Collection of all shared layer exceptions for fast checking
SHARED_EXCEPTIONS = (
    ValidationException,
    BusinessRuleViolationException,
    EntityNotFoundException,
    EntityAlreadyExistsException,
    CommandHandlingException,
    QueryExecutionException,
    EventReconstructionException,
    UnitOfWorkException,
    DatabaseConnectionException,
    ExternalServiceException,
    BusException,
    SessionNotInitializedException,
    InfrastructureException,
    DomainException,
    ApplicationException,
)
