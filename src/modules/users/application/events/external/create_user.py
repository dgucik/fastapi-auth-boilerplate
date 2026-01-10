import logging
import secrets
import string
from uuid import uuid4

from users.application.uow import UsersUnitOfWork
from users.domain.services.user_creation import UserCreationService
from users.domain.value_objects.username import Username

from auth.contracts.events.account_registered import AccountRegisteredIntegrationEvent
from shared.application.ports import IntegrationEventHandler

logger = logging.getLogger(__name__)


class CreateUserHandler(IntegrationEventHandler[AccountRegisteredIntegrationEvent]):
    def __init__(self, uow: UsersUnitOfWork, service: UserCreationService):
        self._uow = uow
        self._service = service

    async def handle(self, event: AccountRegisteredIntegrationEvent) -> None:
        user_id = uuid4()
        random_id = "".join(secrets.choice(string.digits) for _ in range(9))
        username = f"User_{random_id}"
        username_vo = Username(username)
        async with self._uow:
            user = await self._service.create_user(
                self._uow.users, user_id, event.account_id, username_vo
            )
            await self._uow.users.add(user)
            await self._uow.commit()
        logger.info(f"User profile for account id: {event.account_id} created.")
