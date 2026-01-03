import logging
from dataclasses import dataclass
from uuid import UUID

from auth.application.exceptions import (
    AccountDoesNotExistException,
    PasswordMustBeDifferentException,
    PasswordsDoNotMatchException,
)
from auth.application.uow import AuthUnitOfWork
from auth.domain.interfaces import PasswordHasher
from auth.domain.value_objects import PlainPassword
from shared.application.cqrs import Command, Handler

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class ChangePasswordCommand(Command):
    account_id: UUID
    old_password: str
    new_password: str
    confirm_new_password: str


class ChangePasswordHandler(Handler[ChangePasswordCommand, None]):
    def __init__(self, uow: AuthUnitOfWork, hasher: PasswordHasher):
        self._uow = uow
        self._hasher = hasher

    async def handle(self, command: ChangePasswordCommand) -> None:
        if command.old_password == command.new_password:
            raise PasswordMustBeDifferentException

        if command.new_password != command.confirm_new_password:
            raise PasswordsDoNotMatchException

        old_password_vo = PlainPassword(command.old_password)
        new_password_vo = PlainPassword(command.new_password)

        async with self._uow:
            account = await self._uow.accounts.get_by_id(command.account_id)
            if not account:
                raise AccountDoesNotExistException

            account.change_password(old_password_vo, new_password_vo, self._hasher)

            await self._uow.accounts.update(account)

            await self._uow.commit()

        logger.info(f"Password changed for account: {command.account_id}")
