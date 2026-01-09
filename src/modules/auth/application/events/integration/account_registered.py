import logging

from auth.contracts.events.account_registered import AccountRegisteredIntegrationEvent
from auth.domain.events.account_registered import AccountRegisteredDomainEvent
from shared.application.ports import (
    DomainEventHandler,
    IntegrationEventProducer,
)

logger = logging.getLogger(__name__)


class AccountRegisteredIntegrationHandler(
    DomainEventHandler[AccountRegisteredDomainEvent]
):
    def __init__(self, producer: IntegrationEventProducer):
        self._producer = producer

    async def handle(self, event: AccountRegisteredDomainEvent) -> None:
        integration_event = AccountRegisteredIntegrationEvent(
            account_id=event.account_id
        )
        await self._producer.publish(integration_event.TOPIC, integration_event)
        logger.info(
            f"Integration event: {type(integration_event).__name__} has been published."
        )
