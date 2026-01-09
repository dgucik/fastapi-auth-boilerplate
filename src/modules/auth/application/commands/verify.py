import logging
from dataclasses import dataclass
from uuid import UUID

from auth.application.exceptions import AccountDoesNotExistException
from auth.application.uow import AuthUnitOfWork
from auth.domain.ports import TokenManager, TokenScope
from shared.application.ports import Command, Handler

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class VerifyEmailCommand(Command):
    token: str


class VerifyEmailHandler(Handler[VerifyEmailCommand, None]):
    def __init__(self, uow: AuthUnitOfWork, token_manager: TokenManager) -> None:
        self._uow = uow
        self._token_manager = token_manager

    async def handle(self, command: VerifyEmailCommand) -> None:
        account_id_str = self._token_manager.decode_token(
            command.token, expected_type=TokenScope.VERIFICATION
        )
        account_id = UUID(account_id_str)

        async with self._uow:
            account = await self._uow.accounts.get_by_id(account_id)
            if not account:
                raise AccountDoesNotExistException
            account.verify_email()

            await self._uow.accounts.update(account)

            await self._uow.commit()

        logger.info(f"Email verified for account: {account_id}")
