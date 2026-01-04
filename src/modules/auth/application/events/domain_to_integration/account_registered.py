import logging

from auth.contracts.integration_events import AccountRegisteredIntegrationEvent
from auth.domain.events import AccountRegisteredDomainEvent
from shared.application.ports import (
    DomainEventHandler,
    IntegrationEventPublisher,
)

logger = logging.getLogger(__name__)


class AccountRegisteredIntegrationHandler(
    DomainEventHandler[AccountRegisteredDomainEvent]
):
    def __init__(self, publisher: IntegrationEventPublisher):
        self._publisher = publisher

    async def handle(self, event: AccountRegisteredDomainEvent) -> None:
        integration_event = AccountRegisteredIntegrationEvent(
            topic="account.registered", account_id=event.account_id
        )
        await self._publisher.publish(integration_event)
        logger.info(
            f"Integration event: {type(integration_event).__name__} has been published."
        )
