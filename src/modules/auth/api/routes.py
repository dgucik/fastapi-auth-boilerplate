# ruff: noqa: B008

from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends, HTTPException, Response, status

from auth.api.responses import LoginResponse, RegisterResponse
from auth.api.schemas import LoginRequest, RegisterRequest
from auth.application.commands.login import LoginCommand, LoginDto
from auth.application.commands.register import RegisterCommand
from auth.container import AuthContainer
from auth.domain.exceptions import AccountNotVerifiedException, InvalidPasswordException
from shared.application.exceptions import ApplicationException
from shared.domain.exceptions import DomainException
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

    try:
        await command_bus.dispatch(cmd)
        return RegisterResponse(account_id=cmd.account_id)
    except (DomainException, ApplicationException) as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=str(e)
        ) from e


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
            max_age=result.refresh_token_expires_in,
        )

        return LoginResponse(
            access_token=result.access_token,
            refresh_token=result.refresh_token,
            refresh_token_expires_in=result.refresh_token_expires_in,
        )
    except InvalidPasswordException as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e)
        ) from e
    except AccountNotVerifiedException as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e)) from e
    except (DomainException, ApplicationException) as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=str(e)
        ) from e
