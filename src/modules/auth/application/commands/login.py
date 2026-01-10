import logging
from dataclasses import dataclass

from auth.application.uow import AuthUnitOfWork
from auth.domain.services.account_authentication import AccountAuthenticationService
from auth.domain.value_objects.email import Email
from auth.domain.value_objects.plain_password import PlainPassword
from shared.application.ports import Command, Dto, Handler

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class LoginCommand(Command):
    """Command to authenticate a user."""

    email: str
    password: str


@dataclass(frozen=True)
class LoginDto(Dto):
    """Data Transfer Object for login response."""

    access_token: str
    refresh_token: str
    refresh_token_expires_in_seconds: int


class LoginHandler(Handler[LoginCommand, LoginDto]):
    """Handler for LoginCommand."""

    def __init__(
        self, uow: AuthUnitOfWork, service: AccountAuthenticationService
    ) -> None:
        self._uow = uow
        self._service = service

    async def handle(self, command: LoginCommand) -> LoginDto:
        """Processes the login command.

        Args:
            command: The command data.

        Returns:
            LoginDto containing tokens.
        """
        email_vo = Email(value=command.email)
        plain_password_vo = PlainPassword(value=command.password)

        async with self._uow:
            response = await self._service.authenticate(
                self._uow.accounts, email_vo, plain_password_vo
            )

            await self._uow.commit()

        logger.info(f"Login successful for email: {command.email}")
        return LoginDto(
            response.access_token,
            response.refresh_token,
            response.refresh_token_expires_in_seconds,
        )
