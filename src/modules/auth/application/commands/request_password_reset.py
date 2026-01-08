import logging
from dataclasses import dataclass

from auth.application.exceptions import AccountDoesNotExistException
from auth.application.uow import AuthUnitOfWork
from auth.domain.interfaces import TokenManager
from auth.domain.value_objects.email import Email
from shared.application.ports import Command, Handler

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class RequestPasswordResetCommand(Command):
    email: str


class RequestPasswordResetHandler(Handler[RequestPasswordResetCommand, None]):
    def __init__(self, uow: AuthUnitOfWork, token_manager: TokenManager) -> None:
        self._uow = uow
        self._token_manager = token_manager

    async def handle(self, command: RequestPasswordResetCommand) -> None:
        email_vo = Email(command.email)

        async with self._uow:
            account = await self._uow.accounts.get_by_email(email_vo)
            if not account:
                raise AccountDoesNotExistException

            token = self._token_manager.create_password_reset_token(
                subject=str(account.id)
            )
            account.request_password_reset(token)

            await self._uow.commit()

        logger.info(f"Password reset requested for email: {command.email}")
