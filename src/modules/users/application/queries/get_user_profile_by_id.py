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
    """Query to get a user profile by ID.

    Attributes:
        user_id: Target user UUID.
        is_superuser: Flag indicating if the requester is a superuser.
    """

    user_id: UUID
    is_superuser: bool


class GetUserProfileByIdHandler(Handler[GetUserProfileByIdQuery, UserDto]):
    """Handler for GetUserProfileByIdQuery.

    Args:
        uow: Unit of Work for users module.
    """

    def __init__(self, uow: UsersUnitOfWork) -> None:
        """Initializes the handler.

        Args:
            uow: Users Unit of Work.
        """
        self._uow = uow

    async def handle(self, query: GetUserProfileByIdQuery) -> UserDto:
        """Handles the query to get a user profile by ID.

        Args:
            query: The query instance.

        Returns:
            UserDto: User profile data.

        Raises:
            PermissionDeniedException: If requester is not superuser.
            UserProfileNotFoundException: If user profile is not found.
        """
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
