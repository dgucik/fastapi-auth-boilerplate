from uuid import UUID

from pydantic import BaseModel


class RegisterResponse(BaseModel):
    account_id: UUID


class LoginResponse(BaseModel):
    access_token: str
    refresh_token: str
    refresh_token_expires_in_seconds: int


class RequestVerificationTokenResponse(BaseModel):
    message: str


class VerifyEmailResponse(BaseModel):
    message: str


class RequestPasswordResetResponse(BaseModel):
    message: str


class ResetPasswordResponse(BaseModel):
    message: str


class ChangePasswordResponse(BaseModel):
    message: str
