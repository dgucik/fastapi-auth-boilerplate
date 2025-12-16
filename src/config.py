from functools import lru_cache
from typing import Any

from pydantic_settings import BaseSettings, SettingsConfigDict
from sqlalchemy import event
from sqlalchemy.ext.asyncio import AsyncAttrs, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase


class Settings(BaseSettings):
    # Database
    DATABASE_URL: str
    DB_ECHO: bool = False

    # JWT
    SECRET_KEY: str
    ALGORITHM: str = "HS256"

    # Token Expiration
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 15
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # Pydantic
    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", extra="ignore", case_sensitive=True
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()

# --- Database Setup ---

connect_args = {}
# SQLite specific: Allow access from different threads in async mode
if "sqlite" in settings.DATABASE_URL:
    connect_args["check_same_thread"] = False

engine = create_async_engine(
    settings.DATABASE_URL, echo=settings.DB_ECHO, connect_args=connect_args
)

# SQLite specific: Enforce Foreign Key constraints (disabled by default in SQLite)
if "sqlite" in settings.DATABASE_URL:

    @event.listens_for(engine.sync_engine, "connect")
    def enable_sqlite_fks(dbapi_connection: Any, connection_record: Any) -> None:
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()


async_session_factory = async_sessionmaker(
    bind=engine, autoflush=False, expire_on_commit=False
)


# Base class for ORM models
class Base(AsyncAttrs, DeclarativeBase):
    pass


# Function to close the database connection
async def close_db_connection() -> None:
    await engine.dispose()
