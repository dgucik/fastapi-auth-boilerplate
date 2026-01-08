import logging
from dataclasses import dataclass, field
from uuid import UUID, uuid4

from auth.application.exceptions import PasswordsDoNotMatchException
from auth.application.uow import AuthUnitOfWork
from auth.domain.ports import TokenManager
from auth.domain.services.account_registration import AccountRegistrationService
from auth.domain.value_objects.email import Email
from auth.domain.value_objects.plain_password import PlainPassword
from shared.application.ports import Command, Handler

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class RegisterCommand(Command):
    email: str
    password: str
    confirm_password: str
    account_id: UUID = field(default_factory=uuid4)


class RegisterHandler(Handler[RegisterCommand, None]):
    def __init__(
        self,
        uow: AuthUnitOfWork,
        service: AccountRegistrationService,
        token_manager: TokenManager,
    ):
        self._uow = uow
        self._service = service
        self._token_manager = token_manager

    async def handle(self, command: RegisterCommand) -> None:
        if command.password != command.confirm_password:
            raise PasswordsDoNotMatchException

        email_vo = Email(value=command.email)
        plain_password_vo = PlainPassword(value=command.password)

        async with self._uow:
            account = await self._service.register(
                repo=self._uow.accounts,
                account_id=command.account_id,
                email=email_vo,
                password=plain_password_vo,
            )

            await self._uow.accounts.add(account)

            token = self._token_manager.create_verification_token(
                subject=str(account.id)
            )
            account.request_verification(token)

            await self._uow.commit()

        logger.info(f"Registration successful for email: {command.email}")
