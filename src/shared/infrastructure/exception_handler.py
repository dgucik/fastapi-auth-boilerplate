from dataclasses import dataclass

from fastapi import HTTPException, Request
from fastapi.responses import JSONResponse
from starlette import status


@dataclass(frozen=True)
class ExceptionMetadata:
    status_code: int
    error_code: str


class ExceptionRegistry:
    def __init__(
        self,
        mappings_list: list[dict[type[Exception], ExceptionMetadata]] | None = None,
    ) -> None:
        self._mappings: dict[type[Exception], ExceptionMetadata] = {}
        if mappings_list:
            for mapping in mappings_list:
                self._mappings.update(mapping)

    def get_metadata(self, exc: Exception) -> ExceptionMetadata | None:
        for cls in type(exc).mro():
            if cls in self._mappings:
                return self._mappings[cls]
        return None


class GlobalExceptionHandler:
    def __init__(self, registry: ExceptionRegistry) -> None:
        self.registry = registry

    async def __call__(self, request: Request, exc: Exception) -> JSONResponse:
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
