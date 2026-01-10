from pydantic import BaseModel, EmailStr, Field


class RegisterRequest(BaseModel):
    """Request model for account registration."""

    email: EmailStr
    password: str = Field(
        min_length=8, description="Password must be at least 8 characters long."
    )
    confirm_password: str = Field(
        min_length=8, description="Password confirmation must match the password."
    )


class LoginRequest(BaseModel):
    """Request model for login."""

    email: EmailStr
    password: str


class RequestVerificationTokenRequest(BaseModel):
    """Request model for requesting verification token."""

    email: EmailStr


class VerifyEmailRequest(BaseModel):
    """Request model for verifying email."""

    token: str


class RequestPasswordResetRequest(BaseModel):
    """Request model for requesting password reset."""

    email: EmailStr


class ResetPasswordRequest(BaseModel):
    """Request model for resetting password."""

    token: str
    new_password: str
    confirm_new_password: str


class ChangePasswordRequest(BaseModel):
    """Request model for changing password."""

    old_password: str
    new_password: str
    confirm_new_password: str


class RefreshTokenRequest(BaseModel):
    """Request model for refreshing token."""

    refresh_token: str
