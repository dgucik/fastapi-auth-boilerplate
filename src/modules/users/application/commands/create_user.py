import secrets
import string
from dataclasses import dataclass, field
from uuid import UUID, uuid4

from users.application.uow import UsersUnitOfWork
from users.domain.services.user_creation import UserCreationService
from users.domain.value_objects.username import Username

from shared.application.ports import Command, Handler


@dataclass(frozen=True)
class CreateUserCommand(Command):
    account_id: UUID
    user_id: UUID = field(default_factory=uuid4)


class CreateUserHandler(Handler[CreateUserCommand, None]):
    def __init__(self, uow: UsersUnitOfWork, service: UserCreationService):
        self._uow = uow
        self._service = service

    async def handle(self, command: CreateUserCommand) -> None:
        random_id = "".join(secrets.choice(string.digits) for _ in range(9))
        username = f"User_{random_id}"
        username_vo = Username(username)
        async with self._uow:
            user = await self._service.create_user(
                self._uow.users, command.user_id, command.account_id, username_vo
            )
            await self._uow.users.add(user)
            await self._uow.commit()
