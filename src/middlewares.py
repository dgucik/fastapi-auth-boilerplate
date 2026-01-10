import logging
import uuid
from collections.abc import Awaitable, Callable

from fastapi import Request, Response

from config.database import scoped_session_factory
from config.logging import request_id_var
from shared.application.exceptions import ApplicationException
from shared.domain.exceptions import DomainException

logger = logging.getLogger(__name__)


async def logging_middleware(
    request: Request, call_next: Callable[[Request], Awaitable[Response]]
) -> Response:
    """Middleware that logs exceptions.

    Args:
        request: The incoming request.
        call_next: Function to call the next middleware/handler.

    Returns:
        The response from the next handler.
    """
    try:
        response = await call_next(request)
        return response
    except (DomainException, ApplicationException) as e:
        logger.info(f"Domain Error: {type(e).__name__} - {e}")
        raise e
    except Exception as e:
        logger.error(f"Server Error: {e}", exc_info=True)
        raise e


async def request_id_middleware(
    request: Request, call_next: Callable[[Request], Awaitable[Response]]
) -> Response:
    """Middleware that manages Request ID.

    Args:
        request: The incoming request.
        call_next: Function to call the next middleware/handler.

    Returns:
        The response with X-Request-ID header.
    """
    request_id = request.headers.get("X-Request-ID", str(uuid.uuid4()))
    token = request_id_var.set(request_id)
    try:
        response = await call_next(request)
        response.headers["X-Request-ID"] = request_id
        return response
    finally:
        request_id_var.reset(token)


async def db_session_middleware(
    request: Request, call_next: Callable[[Request], Awaitable[Response]]
) -> Response:
    """Middleware that manages database session scope.

    Args:
        request: The incoming request.
        call_next: Function to call the next middleware/handler.

    Returns:
        The response from the next handler.
    """
    try:
        response = await call_next(request)
        logger.debug(
            f"Request completed: {request.method} {request.url.path} - {response.status_code}"  # noqa: E501
        )
        return response
    finally:
        await scoped_session_factory.remove()
