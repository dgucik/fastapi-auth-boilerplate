# ruff: noqa: B008

from uuid import UUID

from dependency_injector.wiring import Provide, inject
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer

from auth.application.uow import AuthUnitOfWork
from auth.container import AuthContainer
from auth.domain.entities.account import Account
from auth.domain.interfaces import TokenManager, TokenScope

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/v1/auth/jwt/login")


@inject
async def get_current_account(
    token: str = Depends(oauth2_scheme),
    token_manager: TokenManager = Depends(Provide[AuthContainer.token_manager]),
    uow: AuthUnitOfWork = Depends(Provide[AuthContainer.uow]),
) -> Account:
    try:
        account_id_str = token_manager.decode_token(token, TokenScope.ACCESS)
        account_id = UUID(account_id_str)

        async with uow:
            account = await uow.accounts.get_by_id(account_id)

        if not account:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Account not found",
                headers={"WWW-Authenticate": "Bearer"},
            )

        return account

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        ) from e
