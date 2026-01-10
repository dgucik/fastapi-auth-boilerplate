from functools import lru_cache

from pydantic import BaseModel
from pydantic_settings import BaseSettings, SettingsConfigDict


class KafkaSettings(BaseModel):
    """Configuration settings for Kafka."""

    BOOTSTRAP_SERVERS: str


class MailSettings(BaseModel):
    """Configuration settings for Email service."""

    USERNAME: str
    PASSWORD: str
    FROM: str
    PORT: int = 587
    SERVER: str
    STARTTLS: bool = True
    SSL_TLS: bool = False
    USE_CREDENTIALS: bool = True


class DatabaseSettings(BaseModel):
    """Configuration settings for Database."""

    USER: str
    PASSWORD: str
    HOST: str
    PORT: int = 5432
    NAME: str

    @property
    def sqlalchemy_database_url(self) -> str:
        """Constructs the SQLAlchemy URL from individual settings."""
        return (
            f"postgresql+asyncpg://"
            f"{self.USER}:{self.PASSWORD}@"
            f"{self.HOST}:{self.PORT}/"
            f"{self.NAME}"
        )


class TokenSettings(BaseModel):
    """Configuration settings for JWT tokens."""

    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 15
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    VERIFICATION_TOKEN_EXPIRE_MINUTES: int = 15
    PASSWORD_RESET_EXPIRE_MINUTES: int = 15


class Settings(BaseSettings):
    """Main application configuration settings."""

    LOG_LEVEL: str = "INFO"
    APP_BASE_URL: str
    DB_ECHO: bool = False
    mail: MailSettings
    db: DatabaseSettings
    token: TokenSettings
    kafka: KafkaSettings

    # Pydantic Configuration
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=False,
        env_nested_delimiter="__",
    )


@lru_cache
def get_settings() -> Settings:
    """Returns cached application settings."""
    return Settings()


settings = get_settings()
