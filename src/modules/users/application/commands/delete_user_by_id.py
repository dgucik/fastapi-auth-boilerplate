import logging
from dataclasses import dataclass
from uuid import UUID

from users.application.uow import UsersUnitOfWork
from users.domain.exceptions import UserProfileNotFoundException

from shared.application.ports import Command, Handler
from shared.infrastructure.exceptions.exceptions import PermissionDeniedException

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class DeleteUserByIdCommand(Command):
    user_id: UUID
    is_superuser: bool


class DeleteUserByIdHandler(Handler[DeleteUserByIdCommand, None]):
    def __init__(self, uow: UsersUnitOfWork) -> None:
        self._uow = uow

    async def handle(self, command: DeleteUserByIdCommand) -> None:
        if not command.is_superuser:
            raise PermissionDeniedException

        async with self._uow:
            user = await self._uow.users.get_by_id(command.user_id)

            if not user:
                raise UserProfileNotFoundException

            await self._uow.users.delete(user)
            await self._uow.commit()

        logger.info("User deleted successfully.")
