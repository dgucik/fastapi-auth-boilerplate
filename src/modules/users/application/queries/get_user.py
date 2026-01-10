from dataclasses import dataclass
from uuid import UUID

from users.application.uow import UsersUnitOfWork
from users.domain.exceptions import UserProfileNotFoundException

from shared.application.ports import Handler, Query
from shared.infrastructure.exceptions.exceptions import PermissionDeniedException


@dataclass(frozen=True)
class GetUserQuery(Query):
    actor_account_id: UUID
    target_user_id: UUID | None = None
    is_superuser: bool = False


@dataclass(frozen=True)
class UserDto:
    id: UUID
    username: str


class GetUserHandler(Handler[GetUserQuery, UserDto]):
    def __init__(self, uow: UsersUnitOfWork) -> None:
        self._uow = uow

    async def handle(self, query: GetUserQuery) -> UserDto:
        # Check if superuser if not self read
        if query.target_user_id:
            if not query.is_superuser:
                raise PermissionDeniedException

        async with self._uow:
            if query.target_user_id:
                user = await self._uow.users.get_by_id(query.target_user_id)
            else:
                user = await self._uow.users.get_by_account_id(query.actor_account_id)

            if not user:
                raise UserProfileNotFoundException

        return UserDto(
            id=user.id,
            username=user.username.value,
        )
