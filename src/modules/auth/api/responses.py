from uuid import UUID

from pydantic import BaseModel


class RegisterResponse(BaseModel):
    account_id: UUID


class LoginResponse(BaseModel):
    access_token: str
    refresh_token: str
    refresh_token_expires_in_seconds: int


class RefreshTokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    refresh_token_expires_in_seconds: int
