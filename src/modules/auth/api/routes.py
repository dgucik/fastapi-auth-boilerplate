# ruff: noqa: B008

from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends, HTTPException, Response, status

from auth.api.responses import (
    LoginResponse,
    RegisterResponse,
    RequestVerificationTokenResponse,
)
from auth.api.schemas import (
    LoginRequest,
    RegisterRequest,
    RequestVerificationTokenRequest,
)
from auth.application.commands.login import LoginCommand, LoginDto
from auth.application.commands.register import RegisterCommand
from auth.application.commands.request_verification_token import (
    RequestVerificationTokenCommand,
)
from auth.container import AuthContainer
from auth.domain.exceptions import InvalidPasswordException
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


@router.post("/jwt/login", response_model=LoginResponse, status_code=status.HTTP_200_OK)
@inject
async def login(
    request: LoginRequest,
    response: Response,
    command_bus: CommandBus = Depends(Provide[AuthContainer.command_bus]),
) -> LoginResponse:
    cmd = LoginCommand(email=request.email, password=request.password)

    try:
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
    except InvalidPasswordException as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e)
        ) from e


@router.post(
    "/request-verify-token",
    response_model=RequestVerificationTokenResponse,
    status_code=status.HTTP_200_OK,
)
@inject
async def request_verification_token(
    request: RequestVerificationTokenRequest,
    response: Response,
    command_bus: CommandBus = Depends(Provide[AuthContainer.command_bus]),
) -> RequestVerificationTokenResponse:
    command = RequestVerificationTokenCommand(email=request.email)

    await command_bus.dispatch(command)

    return RequestVerificationTokenResponse(
        message="Verification email sent successfully."
    )
