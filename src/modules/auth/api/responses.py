from uuid import UUID

from pydantic import BaseModel


class RegisterResponse(BaseModel):
    """Response model for account registration."""

    account_id: UUID


class LoginResponse(BaseModel):
    """Response model for login."""

    access_token: str
    refresh_token: str
    refresh_token_expires_in_seconds: int


class RefreshTokenResponse(BaseModel):
    """Response model for token refresh."""

    access_token: str
    refresh_token: str
    refresh_token_expires_in_seconds: int
