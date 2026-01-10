import logging
from dataclasses import dataclass
from uuid import UUID

from auth.application.exceptions import (
    AccountDoesNotExistException,
    PasswordsDoNotMatchException,
)
from auth.application.uow import AuthUnitOfWork
from auth.domain.ports import PasswordHasher, TokenManager, TokenScope
from auth.domain.value_objects.plain_password import PlainPassword
from shared.application.ports import Command, Handler

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class ResetPasswordCommand(Command):
    """Command to reset password using a token."""

    token: str
    new_password: str
    confirm_new_password: str


class ResetPasswordHandler(Handler[ResetPasswordCommand, None]):
    """Handler for ResetPasswordCommand."""

    def __init__(
        self, uow: AuthUnitOfWork, token_manager: TokenManager, hasher: PasswordHasher
    ):
        self._uow = uow
        self._token_manager = token_manager
        self._hasher = hasher

    async def handle(self, command: ResetPasswordCommand) -> None:
        """Processes the password reset command.

        Args:
            command: The command data.

        Raises:
            PasswordsDoNotMatchException: If new passwords do not match.
            AccountDoesNotExistException: If account is not found.
        """
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

        logger.info(f"Password reset completed for account: {account_id}")
