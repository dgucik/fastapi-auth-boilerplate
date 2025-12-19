from dataclasses import dataclass

from auth.application.exceptions import AccountDoesNotExistException
from auth.application.uow import AuthUnitOfWork
from auth.domain.value_objects import Email
from shared.application.cqrs import Command, Handler


@dataclass(frozen=True)
class RequestVerificationTokenCommand(Command):
    email: str


class RequestVerificationTokenHandler(Handler[RequestVerificationTokenCommand, None]):
    def __init__(self, uow: AuthUnitOfWork):
        self._uow = uow

    async def handle(self, command: RequestVerificationTokenCommand) -> None:
        email_vo = Email(value=command.email)

        async with self._uow:
            account = await self._uow.accounts.get_by_email(email_vo)
            if account is None:
                raise AccountDoesNotExistException()

            account.request_verification()

            await self._uow.commit()
