from auth.domain.events import AccountRegistered
from shared.application.event_handling import DomainEventHandler


class SendWelcomeEmail(DomainEventHandler[AccountRegistered]):
    async def handle(self, event: AccountRegistered) -> None:
        print(f"Sending welcome email to: {event.email}", flush=True)
