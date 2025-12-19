import asyncio
from collections.abc import AsyncGenerator, Awaitable, Callable
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request, Response

from auth import auth_router, auth_routes
from config import close_db_connection, scoped_session_factory, settings
from container import AppContainer


async def db_session_middleware(
    request: Request, call_next: Callable[[Request], Awaitable[Response]]
) -> Response:
    try:
        response = await call_next(request)
        return response
    finally:
        await scoped_session_factory.remove()


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    container: AppContainer = app.state.container

    outbox_tasks = []

    auth_processor = container.auth().outbox_processor()
    outbox_tasks.append(
        asyncio.create_task(
            auth_processor.run_forever(interval=0.5), name="auth_outbox"
        )
    )

    yield

    for task in outbox_tasks:
        task.cancel()

    if outbox_tasks:
        await asyncio.gather(*outbox_tasks, return_exceptions=True)

    await close_db_connection()


def create_app() -> FastAPI:
    app_container = AppContainer(session_factory=scoped_session_factory)
    app_container.settings.from_pydantic(settings)

    app_container.auth().wire(modules=auth_routes)

    # --- Application Setup ---
    app = FastAPI(lifespan=lifespan)

    app.state.container = app_container

    app.include_router(auth_router, prefix="/v1/auth")

    # --- Middleware ---
    app.middleware("http")(db_session_middleware)

    return app


app = create_app()
