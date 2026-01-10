import logging
from dataclasses import dataclass
from uuid import UUID

from users.application.queries.common_dtos import UserDto
from users.application.uow import UsersUnitOfWork
from users.domain.exceptions import UserProfileNotFoundException

from shared.application.ports import Handler, Query

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class GetMyUserProfileQuery(Query):
    account_id: UUID


class GetMyUserProfileHandler(Handler[GetMyUserProfileQuery, UserDto]):
    def __init__(self, uow: UsersUnitOfWork) -> None:
        self._uow = uow

    async def handle(self, query: GetMyUserProfileQuery) -> UserDto:
        async with self._uow:
            user = await self._uow.users.get_by_account_id(query.account_id)

            if not user:
                raise UserProfileNotFoundException

        logger.info("User profile read successfully.")
        return UserDto(
            id=user.id,
            username=user.username.value,
        )
