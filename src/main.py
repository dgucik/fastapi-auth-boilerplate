# --- Lifespan Management ---
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from fastapi import FastAPI

from config import close_db_connection


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    yield

    await close_db_connection()


def create_app() -> FastAPI:
    app = FastAPI(lifespan=lifespan)

    return app


app = create_app()
