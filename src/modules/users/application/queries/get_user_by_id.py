from dataclasses import dataclass
from uuid import UUID

from users.application.uow import UsersUnitOfWork
from users.domain.exceptions import UserProfileNotFoundException

from shared.application.ports import Handler, Query


@dataclass(frozen=True)
class GetUserByIdQuery(Query):
    id: UUID


@dataclass(frozen=True)
class GetUserByIdDto:
    id: UUID
    username: str


class GetUserByIdHandler(Handler[GetUserByIdQuery, GetUserByIdDto]):
    def __init__(self, uow: UsersUnitOfWork) -> None:
        self._uow = uow

    async def handle(self, query: GetUserByIdQuery) -> GetUserByIdDto:
        async with self._uow:
            user = await self._uow.users.get_by_id(query.id)

        if not user:
            raise UserProfileNotFoundException(f"User for id {query.id} not found.")

        return GetUserByIdDto(
            id=user.id,
            username=user.username.value,
        )
