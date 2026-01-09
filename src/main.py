import logging
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from di import AppContainer
from fastapi import FastAPI
from middlewares import db_session_middleware, logging_middleware, request_id_middleware

from auth import auth_router, auth_routes
from config.database import close_db_connection, scoped_session_factory
from config.env import settings
from config.logging import setup_logging

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    logger.info("Starting application...")
    container: AppContainer = app.state.container

    if init_task := container.init_resources():
        await init_task

    yield

    if shutdown_task := container.shutdown_resources():
        await shutdown_task

    await close_db_connection()
    logger.info("Application shutdown complete.")


def create_app() -> FastAPI:
    setup_logging(settings.LOG_LEVEL)

    app_container = AppContainer(session_factory=scoped_session_factory)
    app_container.settings.from_pydantic(settings)

    app_container.auth().wire(modules=auth_routes)

    app = FastAPI(lifespan=lifespan)

    app.state.container = app_container

    # --- Middlewares ---
    app.middleware("http")(db_session_middleware)
    app.middleware("http")(logging_middleware)
    app.middleware("http")(request_id_middleware)

    # --- Routers ---
    app.include_router(auth_router, prefix="/v1/auth")

    # -- Exception Handlers ---
    exc_handler = app_container.exc_handler()
    app.add_exception_handler(Exception, exc_handler)

    return app


app = create_app()
