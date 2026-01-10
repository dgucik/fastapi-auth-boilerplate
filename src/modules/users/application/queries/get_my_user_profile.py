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
    """Query to get current user's profile.

    Attributes:
        account_id: Account UUID.
    """

    account_id: UUID


class GetMyUserProfileHandler(Handler[GetMyUserProfileQuery, UserDto]):
    """Handler for GetMyUserProfileQuery.

    Args:
        uow: Unit of Work for users module.
    """

    def __init__(self, uow: UsersUnitOfWork) -> None:
        """Initializes the handler.

        Args:
            uow: Users Unit of Work.
        """
        self._uow = uow

    async def handle(self, query: GetMyUserProfileQuery) -> UserDto:
        """Handles the query to get current user profile.

        Args:
            query: The query instance.

        Returns:
            UserDto: User profile data.

        Raises:
            UserProfileNotFoundException: If user profile is not found.
        """
        async with self._uow:
            user = await self._uow.users.get_by_account_id(query.account_id)

            if not user:
                raise UserProfileNotFoundException

        logger.info("User profile read successfully.")
        return UserDto(
            id=user.id,
            username=user.username.value,
        )
