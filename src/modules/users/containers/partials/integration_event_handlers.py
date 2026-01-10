import asyncio
import logging
from collections.abc import AsyncGenerator, Callable
from typing import Any

from dependency_injector import containers, providers
from users.application.events.external.create_user import CreateUserHandler
from users.application.uow import UsersUnitOfWork

from auth.contracts.events.account_registered import AccountRegisteredIntegrationEvent
from shared.application.ports import IntegrationEventHandler
from shared.infrastructure.messaging.event_consumer import KafkaIntegrationEventConsumer

logger = logging.getLogger(__name__)


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
    logger.info("Users Event Consumer Started...")
    yield
    task.cancel()
    await consumer.stop()
    logger.info("Users Event Consumer Stopped.")


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
    uow: providers.Dependency[UsersUnitOfWork] = providers.Dependency()
    domain_services = providers.DependenciesContainer()

    # --- Event Factories ---
    create_user_handler = providers.Factory(
        CreateUserHandler, uow=uow, service=domain_services.user_creation_service
    )

    # --- Handlers Map ---
    event_map = providers.Callable(
        lambda handler: {
            "AccountRegisteredIntegrationEvent": (
                AccountRegisteredIntegrationEvent,
                handler,
            )
        },
        handler=create_user_handler,
    )

    # --- Event Consumer ---
    consumer = providers.Resource(
        init_event_consumer,
        bootstrap_servers=settings.kafka.BOOTSTRAP_SERVERS,
        group_id="auth_consumer_group",
        topics=providers.List("account.registered"),
        event_map=event_map,
    )
