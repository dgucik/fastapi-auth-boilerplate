# ruff: noqa: B008
from uuid import UUID

from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends, status
from users.api.dependencies import get_current_account_from_header
from users.api.permissions import require_superuser
from users.api.responses import GetUserByIdResponse, MeResponse
from users.api.schemas import UpdateMeRequest
from users.application.commands.update_user import UpdateUserCommand
from users.application.queries.get_user_by_account_id import GetUserByAccountIdQuery
from users.application.queries.get_user_by_id import GetUserByIdQuery
from users.containers.users import UsersContainer

from auth.contracts.dtos import AuthAccountDto
from shared.infrastructure.cqrs.buses import CommandBus, QueryBus

router = APIRouter(tags=["Users v1"])


@router.get("/me")
@inject
async def read_me(
    current_account: AuthAccountDto = Depends(get_current_account_from_header),
    query_bus: QueryBus = Depends(Provide[UsersContainer.query_bus]),
) -> MeResponse:
    query = GetUserByAccountIdQuery(account_id=current_account.id)
    result = await query_bus.dispatch(query)
    return MeResponse(
        id=result.id,
        email=current_account.email,
        username=result.username,
    )


@router.patch("/me", status_code=status.HTTP_204_NO_CONTENT)
@inject
async def update_me(
    request: UpdateMeRequest,
    current_account: AuthAccountDto = Depends(get_current_account_from_header),
    command_bus: CommandBus = Depends(Provide[UsersContainer.command_bus]),
) -> None:
    cmd = UpdateUserCommand(account_id=current_account.id, username=request.username)
    await command_bus.dispatch(cmd)


@router.get("/{id}", status_code=status.HTTP_200_OK)
@inject
async def read_by_id(
    id: UUID,
    _: AuthAccountDto = Depends(require_superuser()),
    query_bus: QueryBus = Depends(Provide[UsersContainer.query_bus]),
) -> GetUserByIdResponse:
    query = GetUserByIdQuery(id=id)
    result = await query_bus.dispatch(query)
    return GetUserByIdResponse(
        id=result.id,
        username=result.username,
    )
