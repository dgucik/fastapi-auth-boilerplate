import asyncio
import logging
import uuid
from collections.abc import AsyncGenerator, Awaitable, Callable
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request, Response

from auth import auth_router, auth_routes
from config.container import AppContainer
from config.database import close_db_connection, scoped_session_factory
from config.env import settings
from config.logging import request_id_var, setup_logging
from shared.application.exceptions import ApplicationException
from shared.domain.exceptions import DomainException

logger = logging.getLogger(__name__)


async def logging_middleware(
    request: Request, call_next: Callable[[Request], Awaitable[Response]]
) -> Response:
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
    try:
        response = await call_next(request)
        logger.debug(
            f"Request completed: {request.method} {request.url.path} - {response.status_code}"  # noqa: E501
        )
        return response
    finally:
        await scoped_session_factory.remove()


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    logger.info("Starting application...")
    container: AppContainer = app.state.container

    outbox_tasks = []

    auth_processor = container.auth().outbox_processor()
    outbox_tasks.append(
        asyncio.create_task(
            auth_processor.run_forever(interval=0.5), name="auth_outbox"
        )
    )
    logger.info("Outbox processor started")

    logger.info("Application started successfully")
    yield

    logger.info("Shutting down application...")
    for task in outbox_tasks:
        task.cancel()

    if outbox_tasks:
        await asyncio.gather(*outbox_tasks, return_exceptions=True)

    await close_db_connection()
    logger.info("Application shutdown complete")


def create_app() -> FastAPI:
    setup_logging(settings.LOG_LEVEL)

    app_container = AppContainer(session_factory=scoped_session_factory)
    app_container.settings.from_pydantic(settings)

    app_container.auth().wire(modules=auth_routes)

    app = FastAPI(lifespan=lifespan)

    app.state.container = app_container

    # --- Middleware ---
    app.middleware("http")(db_session_middleware)
    app.middleware("http")(logging_middleware)
    app.middleware("http")(request_id_middleware)

    # --- Routers ---
    app.include_router(auth_router, prefix="/v1/auth")

    # -- Exception Handlers ---
    exc_handler = app_container.exception_handler()
    app.add_exception_handler(Exception, exc_handler)

    return app


app = create_app()
