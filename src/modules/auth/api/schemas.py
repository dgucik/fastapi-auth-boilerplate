from pydantic import BaseModel, EmailStr, Field


class RegisterRequest(BaseModel):
    email: EmailStr
    password: str = Field(
        min_length=8, description="Password must be at least 8 characters long."
    )
    confirm_password: str = Field(
        min_length=8, description="Password confirmation must match the password."
    )


class LoginRequest(BaseModel):
    email: EmailStr
    password: str
