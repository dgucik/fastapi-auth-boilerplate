import asyncio
from collections.abc import AsyncGenerator, Callable
from typing import Any

from dependency_injector import containers, providers
from users.application.events.external.create_user import CreateUserHandler

from auth.contracts.events.account_registered import AccountRegisteredIntegrationEvent
from shared.application.ports import IntegrationEventHandler
from shared.infrastructure.cqrs.buses import CommandBus
from shared.infrastructure.messaging.event_consumer import KafkaIntegrationEventConsumer


async def init_event_consumer(
    bootstrap_servers: str,
    group_id: str,
    topics: list[str],
    event_map: dict[str, tuple[type[Any], Callable[[], IntegrationEventHandler[Any]]]],
) -> AsyncGenerator[None, None]:
    consumer = KafkaIntegrationEventConsumer(
        bootstrap_servers=bootstrap_servers,
        group_id=group_id,
        topics=topics,
        event_map=event_map,
    )
    await consumer.start()
    task = asyncio.create_task(consumer.run_forever())
    yield
    task.cancel()
    await consumer.stop()


class IntegrationEventHandlersContainer(containers.DeclarativeContainer):
    """
    Integration Event handlers container

    To add a new event:
    1. Import the event and handler in the imports section
    2. Add the handler factory here
    3. Add to handlers dict
    """

    # --- Dependencies ---
    settings = providers.Configuration()
    command_bus: providers.Dependency[CommandBus] = providers.Dependency()

    # --- Event Factories ---
    create_user_handler = providers.Factory(CreateUserHandler, command_bus=command_bus)

    # --- Handlers Map ---
    event_map = providers.Dict(
        {
            "AccountRegisteredIntegrationEvent": (
                AccountRegisteredIntegrationEvent,
                create_user_handler,
            )
        }
    )

    # --- Event Consumer ---
    consumer = providers.Resource(
        init_event_consumer,
        bootstrap_servers=settings.kafka.BOOTSTRAP_SERVERS,
        group_id="auth_consumer_group",
        topics=providers.List("account.registered"),
        event_map=event_map,
    )
