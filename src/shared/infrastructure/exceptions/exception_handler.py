from fastapi import HTTPException, Request
from fastapi.responses import JSONResponse
from starlette import status

from shared.infrastructure.exceptions.exception_registry import ExceptionRegistry


class GlobalExceptionHandler:
    """Global exception handler for the application.

    Args:
        registry: Registry mapping exceptions to metadata.
    """

    def __init__(self, registry: ExceptionRegistry) -> None:
        """Initializes the handler."""
        self.registry = registry

    async def __call__(self, request: Request, exc: Exception) -> JSONResponse:
        """Handles exceptions and returns appropriate JSON response."""
        metadata = self.registry.get_metadata(exc)

        if metadata:
            return JSONResponse(
                status_code=metadata.status_code,
                content={
                    "error": metadata.error_code,
                    "detail": str(exc),
                    "exception_type": type(exc).__name__,
                },
            )

        if isinstance(exc, HTTPException):
            return JSONResponse(
                status_code=exc.status_code,
                content={"error": "http_error", "detail": exc.detail},
            )

        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "error": "internal_server_error",
                "detail": "An unexpected error occurred",
            },
        )
