import logging
from dataclasses import dataclass
from uuid import UUID

from users.application.queries.common_dtos import UserDto
from users.application.uow import UsersUnitOfWork
from users.domain.exceptions import UserProfileNotFoundException

from shared.application.ports import Handler, Query
from shared.infrastructure.exceptions.exceptions import PermissionDeniedException

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class GetUserProfileByIdQuery(Query):
    user_id: UUID
    is_superuser: bool


class GetUserProfileByIdHandler(Handler[GetUserProfileByIdQuery, UserDto]):
    def __init__(self, uow: UsersUnitOfWork) -> None:
        self._uow = uow

    async def handle(self, query: GetUserProfileByIdQuery) -> UserDto:
        if not query.is_superuser:
            raise PermissionDeniedException

        async with self._uow:
            user = await self._uow.users.get_by_id(query.user_id)

            if not user:
                raise UserProfileNotFoundException

        logger.info("User profile read successfully.")
        return UserDto(
            id=user.id,
            username=user.username.value,
        )
