# ruff: noqa: B008

from dependency_injector.wiring import Provide, inject
from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from users.containers.users import UsersContainer

from auth.contracts.dtos import AuthAccountDto
from auth.contracts.module_port import AuthModulePort

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/v1/auth/login")


@inject
async def get_current_account_from_header(
    token: str = Depends(oauth2_scheme),
    contract: AuthModulePort = Depends(Provide[UsersContainer.auth_contract]),
) -> AuthAccountDto:
    """Gets current user account from JWT token header.

    Args:
        token: JWT access token.
        contract: Auth module contract for token validation.

    Returns:
        AuthAccountDto: Current user account data.
    """
    account_dto = await contract.get_account_by_token(token)
    return account_dto
