import logging
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from app_container import AppContainer
from fastapi import FastAPI
from middlewares import db_session_middleware, logging_middleware, request_id_middleware
from users import users_router, users_routes

from auth import auth_router, auth_routes
from config.database import close_db_connection, scoped_session_factory
from config.env import settings
from config.logging import setup_logging

logger = logging.getLogger(__name__)


def create_container() -> AppContainer:
    container = AppContainer(session_factory=scoped_session_factory)
    container.settings.from_pydantic(settings)
    return container


def wire_container(container: AppContainer) -> None:
    container.auth().wire(modules=auth_routes)
    container.users().wire(modules=users_routes)


def setup_middlewares(app: FastAPI) -> None:
    app.middleware("http")(db_session_middleware)
    app.middleware("http")(logging_middleware)
    app.middleware("http")(request_id_middleware)


def setup_routers(app: FastAPI) -> None:
    app.include_router(auth_router, prefix="/v1/auth")
    app.include_router(users_router, prefix="/v1/users")


def setup_exc_handlers(
    app: FastAPI,
    container: AppContainer,
) -> None:
    exc_handler = container.exc_handler()
    app.add_exception_handler(Exception, exc_handler)


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

    container = create_container()

    app = FastAPI(lifespan=lifespan)

    app.state.container = container

    wire_container(container)
    setup_middlewares(app)
    setup_routers(app)
    setup_exc_handlers(app, container)

    return app


app = create_app()
