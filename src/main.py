# --- Lifespan Management ---
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from fastapi import FastAPI

from auth import auth_router, auth_routes
from config import async_session_factory, close_db_connection, settings
from container import AppContainer


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    yield

    await close_db_connection()


def create_app() -> FastAPI:
    app_container = AppContainer(session_factory=async_session_factory)
    app_container.settings.from_pydantic(settings)

    app_container.auth().wire(modules=auth_routes)

    # --- Application Setup ---
    app = FastAPI(lifespan=lifespan)

    app.state.container = app_container

    app.include_router(auth_router, prefix="/v1/auth")

    return app


app = create_app()
