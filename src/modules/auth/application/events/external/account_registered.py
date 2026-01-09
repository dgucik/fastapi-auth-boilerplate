from auth.contracts.events.account_registered import AccountRegisteredIntegrationEvent
from shared.application.ports import IntegrationEventHandler


class AccountRegisteredHandler(
    IntegrationEventHandler[AccountRegisteredIntegrationEvent]
):
    async def handle(self, event: AccountRegisteredIntegrationEvent) -> None:
        print(f"\n\nTEST: {event.account_id}\n\n", flush=True)
