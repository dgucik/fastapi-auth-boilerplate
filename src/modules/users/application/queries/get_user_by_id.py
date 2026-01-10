from dataclasses import dataclass
from uuid import UUID

from users.application.uow import UsersUnitOfWork
from users.domain.exceptions import UserProfileNotFoundException

from shared.application.ports import Handler, Query
from shared.infrastructure.exceptions.exceptions import PermissionDeniedException


@dataclass(frozen=True)
class GetUserByIdQuery(Query):
    id: UUID
    is_superuser: bool


@dataclass(frozen=True)
class GetUserByIdDto:
    id: UUID
    username: str


class GetUserByIdHandler(Handler[GetUserByIdQuery, GetUserByIdDto]):
    def __init__(self, uow: UsersUnitOfWork) -> None:
        self._uow = uow

    async def handle(self, query: GetUserByIdQuery) -> GetUserByIdDto:
        if not query.is_superuser:
            raise PermissionDeniedException

        async with self._uow:
            user = await self._uow.users.get_by_id(query.id)

        if not user:
            raise UserProfileNotFoundException(f"User for id {query.id} not found.")

        return GetUserByIdDto(
            id=user.id,
            username=user.username.value,
        )
