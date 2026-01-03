# ruff: noqa: B008

from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends, Response, status

from auth.api.dependencies import get_current_account
from auth.api.responses import LoginResponse, RefreshTokenResponse, RegisterResponse
from auth.api.schemas import (
    ChangePasswordRequest,
    LoginRequest,
    RefreshTokenRequest,
    RegisterRequest,
    RequestPasswordResetRequest,
    RequestVerificationTokenRequest,
    ResetPasswordRequest,
    VerifyEmailRequest,
)
from auth.application.commands.change_password import ChangePasswordCommand
from auth.application.commands.login import LoginCommand, LoginDto
from auth.application.commands.refresh_token import RefreshTokenCommand, RefreshTokenDto
from auth.application.commands.register import RegisterCommand
from auth.application.commands.request_password_reset import RequestPasswordResetCommand
from auth.application.commands.request_verification_token import (
    RequestVerificationTokenCommand,
)
from auth.application.commands.reset_password import ResetPasswordCommand
from auth.application.commands.verify import VerifyEmailCommand
from auth.application.exceptions import AccountDoesNotExistException
from auth.container import AuthContainer
from auth.domain.entities.account import Account
from shared.api.responses import MessageResponse
from shared.infrastructure.buses import CommandBus

router = APIRouter(tags=["Auth"])


@router.post(
    "/register", response_model=RegisterResponse, status_code=status.HTTP_201_CREATED
)
@inject
async def register(
    request: RegisterRequest,
    command_bus: CommandBus = Depends(Provide[AuthContainer.command_bus]),
) -> RegisterResponse:
    cmd = RegisterCommand(
        email=request.email,
        password=request.password,
        confirm_password=request.confirm_password,
    )

    await command_bus.dispatch(cmd)
    return RegisterResponse(account_id=cmd.account_id)


@router.post("/login", response_model=LoginResponse, status_code=status.HTTP_200_OK)
@inject
async def login(
    request: LoginRequest,
    response: Response,
    command_bus: CommandBus = Depends(Provide[AuthContainer.command_bus]),
) -> LoginResponse:
    cmd = LoginCommand(email=request.email, password=request.password)

    result: LoginDto = await command_bus.dispatch(cmd)  # type: ignore
    response.set_cookie(
        key="refresh_token",
        value=result.refresh_token,
        httponly=True,
        secure=True,
        samesite="lax",
        max_age=result.refresh_token_expires_in_seconds,
    )

    return LoginResponse(
        access_token=result.access_token,
        refresh_token=result.refresh_token,
        refresh_token_expires_in_seconds=result.refresh_token_expires_in_seconds,
    )


@router.post(
    "/refresh-token",
    response_model=RefreshTokenResponse,
    status_code=status.HTTP_200_OK,
)
@inject
async def refresh_token(
    request: RefreshTokenRequest,
    response: Response,
    command_bus: CommandBus = Depends(Provide[AuthContainer.command_bus]),
) -> RefreshTokenResponse:
    cmd = RefreshTokenCommand(refresh_token=request.refresh_token)
    result: RefreshTokenDto = await command_bus.dispatch(cmd)  # type: ignore
    response.set_cookie(
        key="refresh_token",
        value=result.refresh_token,
        httponly=True,
        secure=True,
        samesite="lax",
        max_age=result.refresh_token_expires_in_seconds,
    )

    return RefreshTokenResponse(
        access_token=result.access_token,
        refresh_token=result.refresh_token,
        refresh_token_expires_in_seconds=result.refresh_token_expires_in_seconds,
    )


@router.post(
    "/logout",
    response_model=MessageResponse,
    status_code=status.HTTP_200_OK,
)
async def logout(
    response: Response, current_account: Account = Depends(get_current_account)
) -> MessageResponse:
    response.delete_cookie(
        key="refresh_token",
        httponly=True,
        secure=True,
        samesite="lax",
    )
    return MessageResponse(message="Logged out successfully.")


@router.post(
    "/request-verify-token",
    response_model=MessageResponse,
    status_code=status.HTTP_200_OK,
)
@inject
async def request_verification_token(
    request: RequestVerificationTokenRequest,
    response: Response,
    command_bus: CommandBus = Depends(Provide[AuthContainer.command_bus]),
) -> MessageResponse:
    cmd = RequestVerificationTokenCommand(email=request.email)

    await command_bus.dispatch(cmd)

    return MessageResponse(message="Verification email sent successfully.")


@router.post(
    "/verify",
    response_model=MessageResponse,
    status_code=status.HTTP_200_OK,
)
@inject
async def verify_email(
    request: VerifyEmailRequest,
    response: Response,
    command_bus: CommandBus = Depends(Provide[AuthContainer.command_bus]),
) -> MessageResponse:
    cmd = VerifyEmailCommand(token=request.token)

    await command_bus.dispatch(cmd)

    return MessageResponse(message="Email verified successfully.")


@router.post(
    "/request-password-reset",
    response_model=MessageResponse,
    status_code=status.HTTP_202_ACCEPTED,
)
@inject
async def request_password_reset(
    request: RequestPasswordResetRequest,
    command_bus: CommandBus = Depends(Provide[AuthContainer.command_bus]),
) -> MessageResponse:
    cmd = RequestPasswordResetCommand(email=request.email)

    try:
        await command_bus.dispatch(cmd)
    except AccountDoesNotExistException:
        pass

    return MessageResponse(message="A password reset link has been sent.")


@router.post(
    "/reset-password",
    response_model=MessageResponse,
    status_code=status.HTTP_200_OK,
)
@inject
async def reset_password(
    request: ResetPasswordRequest,
    command_bus: CommandBus = Depends(Provide[AuthContainer.command_bus]),
) -> MessageResponse:
    cmd = ResetPasswordCommand(
        token=request.token,
        new_password=request.new_password,
        confirm_new_password=request.confirm_new_password,
    )

    await command_bus.dispatch(cmd)

    return MessageResponse(message="Password has been successfully reset.")


@router.post(
    "/change-password",
    response_model=MessageResponse,
    status_code=status.HTTP_200_OK,
)
@inject
async def change_password(
    request: ChangePasswordRequest,
    command_bus: CommandBus = Depends(Provide[AuthContainer.command_bus]),
    current_account: Account = Depends(get_current_account),
) -> MessageResponse:
    cmd = ChangePasswordCommand(
        account_id=current_account.id,
        old_password=request.old_password,
        new_password=request.new_password,
        confirm_new_password=request.confirm_new_password,
    )

    await command_bus.dispatch(cmd)

    return MessageResponse(message="Your password has been changed successfully.")
