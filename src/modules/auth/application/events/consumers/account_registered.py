import logging

from auth.contracts.integration_events import AccountRegisteredIntegrationEvent
from shared.application.ports import IntegrationEventHandler

logger = logging.getLogger(__name__)


class AccountRegistered(IntegrationEventHandler[AccountRegisteredIntegrationEvent]):
    async def handle(self, event: AccountRegisteredIntegrationEvent) -> None:
        print("TEST", flush=True)
