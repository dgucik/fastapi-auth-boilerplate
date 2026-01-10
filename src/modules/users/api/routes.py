# ruff: noqa: B008
from uuid import UUID

from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends, status
from users.api.dependencies import get_current_account_from_header
from users.api.responses import GetUserByIdResponse, MeResponse
from users.api.schemas import UpdateMeRequest, UpdateUserIdRequest
from users.application.commands.delete_user_by_id import DeleteUserByIdCommand
from users.application.commands.update_user import UpdateUserCommand
from users.application.queries.get_my_user_profile import GetMyUserProfileQuery
from users.application.queries.get_user_profile_by_id import GetUserProfileByIdQuery
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
    query = GetMyUserProfileQuery(account_id=current_account.id)
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
    cmd = UpdateUserCommand(
        actor_account_id=current_account.id, username=request.username
    )
    await command_bus.dispatch(cmd)


@router.get("/{id}", status_code=status.HTTP_200_OK)
@inject
async def read_by_id(
    id: UUID,
    current_account: AuthAccountDto = Depends(get_current_account_from_header),
    query_bus: QueryBus = Depends(Provide[UsersContainer.query_bus]),
) -> GetUserByIdResponse:
    query = GetUserProfileByIdQuery(
        user_id=id,
        is_superuser=current_account.is_superuser,
    )
    result = await query_bus.dispatch(query)
    return GetUserByIdResponse(
        id=result.id,
        username=result.username,
    )


@router.patch("/{id}", status_code=status.HTTP_204_NO_CONTENT)
@inject
async def update_by_id(
    request: UpdateUserIdRequest,
    id: UUID,
    current_account: AuthAccountDto = Depends(get_current_account_from_header),
    command_bus: CommandBus = Depends(Provide[UsersContainer.command_bus]),
) -> None:
    cmd = UpdateUserCommand(
        username=request.username,
        actor_account_id=current_account.id,
        target_user_id=id,
        is_superuser=current_account.is_superuser,
    )
    await command_bus.dispatch(cmd)


@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
@inject
async def delete_by_id(
    id: UUID,
    current_account: AuthAccountDto = Depends(get_current_account_from_header),
    command_bus: CommandBus = Depends(Provide[UsersContainer.command_bus]),
) -> None:
    cmd = DeleteUserByIdCommand(user_id=id, is_superuser=current_account.is_superuser)
    await command_bus.dispatch(cmd)
