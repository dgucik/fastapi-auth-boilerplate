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
class UpdateUserCommand(Command):
    username: str
    actor_account_id: UUID
    target_user_id: UUID | None = None
    is_superuser: bool = False


class UpdateUserHandler(Handler[UpdateUserCommand, None]):
    def __init__(self, uow: UsersUnitOfWork) -> None:
        self._uow = uow

    async def handle(self, command: UpdateUserCommand) -> None:
        new_username_vo = Username(command.username)

        # Check if superuser if not self update
        if command.target_user_id:
            if not command.is_superuser:
                raise PermissionDeniedException

        async with self._uow:
            if command.target_user_id:
                user = await self._uow.users.get_by_id(command.target_user_id)
            else:
                user = await self._uow.users.get_by_account_id(command.actor_account_id)

            if not user:
                raise UserProfileNotFoundException

            user.change_username(new_username_vo)

            await self._uow.users.update(user)

            await self._uow.commit()

        logger.info(f"User profile successfully updated for: {user.id}")
