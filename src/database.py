from asyncio import current_task
from typing import Any

from sqlalchemy.ext.asyncio import (
    AsyncAttrs,
    AsyncEngine,
    async_scoped_session,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import DeclarativeBase

from settings import settings

connect_args: dict[str, Any] = {}

engine: AsyncEngine = create_async_engine(
    settings.db.sqlalchemy_database_url,
    echo=settings.DB_ECHO,
    connect_args=connect_args,
)


_async_session_factory = async_sessionmaker(
    bind=engine, autoflush=False, expire_on_commit=False
)

scoped_session_factory = async_scoped_session(
    session_factory=_async_session_factory,
    scopefunc=current_task,
)


# Base class for ORM models
class Base(AsyncAttrs, DeclarativeBase):
    pass


# Function to close the database connection
async def close_db_connection() -> None:
    await engine.dispose()
