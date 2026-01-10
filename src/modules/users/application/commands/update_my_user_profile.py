import logging
from dataclasses import dataclass
from uuid import UUID

from users.application.uow import UsersUnitOfWork
from users.domain.exceptions import UserProfileNotFoundException
from users.domain.value_objects.username import Username

from shared.application.ports import Command, Handler

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class UpdateMyUserProfileCommand(Command):
    """Command to update current user's profile.

    Attributes:
        username: New username.
        account_id: Account UUID.
    """

    username: str
    account_id: UUID


class UpdateMyUserProfileHandler(Handler[UpdateMyUserProfileCommand, None]):
    """Handler for UpdateMyUserProfileCommand.

    Args:
        uow: Unit of Work for users module.
    """

    def __init__(self, uow: UsersUnitOfWork) -> None:
        """Initializes the handler.

        Args:
            uow: Users Unit of Work.
        """
        self._uow = uow

    async def handle(self, command: UpdateMyUserProfileCommand) -> None:
        """Handles the command to update current user's profile.

        Args:
            command: The command instance.

        Raises:
            UserProfileNotFoundException: If user profile is not found.
        """
        new_username_vo = Username(command.username)

        async with self._uow:
            user = await self._uow.users.get_by_account_id(command.account_id)

            if not user:
                raise UserProfileNotFoundException

            user.change_username(new_username_vo)

            await self._uow.users.update(user)

            await self._uow.commit()

        logger.info(f"User profile successfully updated for: {user.id}")
