from asyncio import current_task
from functools import lru_cache
from typing import Any

from pydantic_settings import BaseSettings, SettingsConfigDict
from sqlalchemy.ext.asyncio import (
    AsyncAttrs,
    AsyncEngine,
    async_scoped_session,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import DeclarativeBase


class Settings(BaseSettings):
    # Database Connection Params
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_HOST: str
    POSTGRES_PORT: int = 5432
    POSTGRES_DB: str

    DB_ECHO: bool = False

    # JWT
    SECRET_KEY: str
    ALGORITHM: str = "HS256"

    # Token Expiration
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 15
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # Pydantic Configuration
    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", extra="ignore", case_sensitive=True
    )

    @property
    def sqlalchemy_database_url(self) -> str:
        """Constructs the SQLAlchemy URL from individual settings."""
        return (
            f"postgresql+asyncpg://"
            f"{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@"
            f"{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/"
            f"{self.POSTGRES_DB}"
        )


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()

# --- Database Setup ---

connect_args: dict[str, Any] = {}

engine: AsyncEngine = create_async_engine(
    settings.sqlalchemy_database_url,
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
