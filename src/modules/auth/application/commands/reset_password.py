from dataclasses import dataclass
from uuid import UUID

from auth.application.exceptions import (
    AccountDoesNotExistException,
    PasswordsDoNotMatchException,
)
from auth.application.uow import AuthUnitOfWork
from auth.domain.interfaces import PasswordHasher, TokenManager, TokenScope
from auth.domain.value_objects import PlainPassword
from shared.application.cqrs import Command, Handler


@dataclass(frozen=True)
class ResetPasswordCommand(Command):
    token: str
    new_password: str
    confirm_new_password: str


class ResetPasswordHandler(Handler[ResetPasswordCommand, None]):
    def __init__(
        self, uow: AuthUnitOfWork, token_manager: TokenManager, hasher: PasswordHasher
    ):
        self._uow = uow
        self._token_manager = token_manager
        self._hasher = hasher

    async def handle(self, command: ResetPasswordCommand) -> None:
        if command.new_password != command.confirm_new_password:
            raise PasswordsDoNotMatchException

        new_password_vo = PlainPassword(command.new_password)

        account_id_str = self._token_manager.decode_token(
            command.token, TokenScope.PASSWORD_RESET
        )
        account_id = UUID(account_id_str)

        async with self._uow:
            account = await self._uow.accounts.get_by_id(account_id)
            if not account:
                raise AccountDoesNotExistException

            account.reset_password(new_password_vo, self._hasher)

            await self._uow.accounts.update(account)

            await self._uow.commit()
