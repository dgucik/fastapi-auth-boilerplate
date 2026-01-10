import logging
from dataclasses import dataclass
from uuid import UUID

from users.application.uow import UsersUnitOfWork
from users.domain.exceptions import UserProfileNotFoundException

from shared.application.ports import Command, Handler
from shared.infrastructure.exceptions.exceptions import PermissionDeniedException

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class DeleteUserProfileByIdCommand(Command):
    """Command to delete a user profile by ID.

    Attributes:
        user_id: UUID of the user to delete.
        is_superuser: Flag indicating if the requester is a superuser.
    """

    user_id: UUID
    is_superuser: bool


class DeleteUserProfileByIdHandler(Handler[DeleteUserProfileByIdCommand, None]):
    """Handler for DeleteUserProfileByIdCommand.

    Args:
        uow: Unit of Work for users module.
    """

    def __init__(self, uow: UsersUnitOfWork) -> None:
        """Initializes the handler.

        Args:
            uow: Users Unit of Work.
        """
        self._uow = uow

    async def handle(self, command: DeleteUserProfileByIdCommand) -> None:
        """Handles the command to delete a user profile.

        Args:
            command: The command instance.

        Raises:
            PermissionDeniedException: If handler is not superuser.
            UserProfileNotFoundException: If user profile is not found.
        """
        if not command.is_superuser:
            raise PermissionDeniedException

        async with self._uow:
            user = await self._uow.users.get_by_id(command.user_id)

            if not user:
                raise UserProfileNotFoundException

            await self._uow.users.delete(user)
            await self._uow.commit()

        logger.info("User deleted successfully.")
