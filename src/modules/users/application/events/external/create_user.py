from users.application.commands.create_user import CreateUserCommand

from auth.contracts.events.account_registered import AccountRegisteredIntegrationEvent
from shared.application.ports import IntegrationEventHandler
from shared.infrastructure.cqrs.buses import CommandBus


class CreateUserHandler(IntegrationEventHandler[AccountRegisteredIntegrationEvent]):
    def __init__(self, command_bus: CommandBus):
        self._command_bus = command_bus

    async def handle(self, event: AccountRegisteredIntegrationEvent) -> None:
        print("\n\nDEBUG: Invoked\n\n", flush=True)
        command = CreateUserCommand(account_id=event.account_id)
        await self._command_bus.dispatch(command)
