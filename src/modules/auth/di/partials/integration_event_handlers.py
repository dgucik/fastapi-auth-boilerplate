from dependency_injector import containers, providers

from auth.application.events.external.account_registered import AccountRegisteredHandler
from auth.contracts.events.account_registered import AccountRegisteredIntegrationEvent
from shared.infrastructure.messaging.event_consumer import KafkaIntegrationEventConsumer


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

    # --- Event Factories ---
    account_registered_handler = providers.Factory(AccountRegisteredHandler)

    # --- Handlers Map ---
    event_map = providers.Dict(
        {
            "AccountRegisteredIntegrationEvent": (
                AccountRegisteredIntegrationEvent,
                account_registered_handler,
            )
        }
    )

    # --- Event Consumer ---
    consumer = providers.Singleton(
        KafkaIntegrationEventConsumer,
        bootstrap_servers=settings.kafka.BOOTSTRAP_SERVERS,
        group_id="auth_consumer_group",
        topics=providers.List("account.registered"),
        event_map=event_map,
    )
