import logging
from dataclasses import dataclass

from auth.application.exceptions import AccountDoesNotExistException
from auth.application.uow import AuthUnitOfWork
from auth.domain.ports import TokenManager
from auth.domain.value_objects.email import Email
from shared.application.ports import Command, Handler

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class RequestVerificationTokenCommand(Command):
    email: str


class RequestVerificationTokenHandler(Handler[RequestVerificationTokenCommand, None]):
    def __init__(self, uow: AuthUnitOfWork, token_manager: TokenManager):
        self._uow = uow
        self._token_manager = token_manager

    async def handle(self, command: RequestVerificationTokenCommand) -> None:
        email_vo = Email(value=command.email)

        async with self._uow:
            account = await self._uow.accounts.get_by_email(email_vo)
            if account is None:
                raise AccountDoesNotExistException()

            token = self._token_manager.create_verification_token(
                subject=str(account.id)
            )

            account.request_verification(token)

            await self._uow.commit()

        logger.info(f"Verification token requested for email: {command.email}")
