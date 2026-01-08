from auth.contracts.events.account_registered import AccountRegisteredIntegrationEvent
from shared.application.ports import IntegrationEventHandler


class AccountRegistered(IntegrationEventHandler[AccountRegisteredIntegrationEvent]):
    async def handle(self, event: AccountRegisteredIntegrationEvent) -> None:
        print(f"TEST: {event.account_id}", flush=True)
