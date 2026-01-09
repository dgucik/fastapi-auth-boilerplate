from dataclasses import dataclass
from uuid import UUID

from users.application.uow import UsersUnitOfWork
from users.domain.exceptions import UserProfileNotFoundException

from shared.application.ports import Handler, Query


@dataclass(frozen=True)
class GetUserByAccountIdQuery(Query):
    account_id: UUID


@dataclass(frozen=True)
class UserDto:
    id: UUID
    username: str


class GetUserByAccountIdHandler(Handler[GetUserByAccountIdQuery, UserDto]):
    def __init__(self, uow: UsersUnitOfWork) -> None:
        self._uow = uow

    async def handle(self, query: GetUserByAccountIdQuery) -> UserDto:
        async with self._uow:
            user = await self._uow.users.get_by_account_id(query.account_id)

        if not user:
            raise UserProfileNotFoundException(
                f"User for account id {query.account_id} not found."
            )

        return UserDto(
            id=user.id,
            username=user.username.value,
        )
