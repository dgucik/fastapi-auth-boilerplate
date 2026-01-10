import logging
from dataclasses import dataclass
from uuid import UUID

from users.application.uow import UsersUnitOfWork
from users.domain.exceptions import UserProfileNotFoundException
from users.domain.value_objects.username import Username

from shared.application.ports import Command, Handler
from shared.infrastructure.exceptions.exceptions import PermissionDeniedException

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class UpdateUserProfileByIdCommand(Command):
    """Command to update a user profile by ID.

    Attributes:
        username: New username.
        user_id: Target user UUID.
        is_superuser: Flag indicating if the requester is a superuser.
    """

    username: str
    user_id: UUID
    is_superuser: bool


class UpdateUserProfileByIdHandler(Handler[UpdateUserProfileByIdCommand, None]):
    """Handler for UpdateUserProfileByIdCommand.

    Args:
        uow: Unit of Work for users module.
    """

    def __init__(self, uow: UsersUnitOfWork) -> None:
        """Initializes the handler.

        Args:
            uow: Users Unit of Work.
        """
        self._uow = uow

    async def handle(self, command: UpdateUserProfileByIdCommand) -> None:
        """Handles the command to update a user profile by ID.

        Args:
            command: The command instance.

        Raises:
            PermissionDeniedException: If requester is not superuser.
            UserProfileNotFoundException: If user profile is not found.
        """
        new_username_vo = Username(command.username)

        if not command.is_superuser:
            raise PermissionDeniedException

        async with self._uow:
            user = await self._uow.users.get_by_id(command.user_id)

            if not user:
                raise UserProfileNotFoundException

            user.change_username(new_username_vo)

            await self._uow.users.update(user)

            await self._uow.commit()

        logger.info(f"User profile successfully updated for: {user.id}")
