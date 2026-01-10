from dependency_injector import containers, providers

from shared.application.ports import IntegrationEventProducer
from shared.infrastructure.messaging.event_bus import InMemoryDomainEventBus
from shared.infrastructure.messaging.event_registry import DomainEventRegistryImpl


class DomainEventHandlersContainer(containers.DeclarativeContainer):
    """Container for domain event handlers.

    Manages registration and bus configuration for domain events.
    """

    # --- Dependencies ---
    settings = providers.Configuration()
    producer: providers.Dependency[IntegrationEventProducer] = providers.Dependency()

    # --- Event Factories ---

    # --- Handlers Map ---
    handlers = providers.Dict({})

    # --- Bus ---
    bus = providers.Singleton(InMemoryDomainEventBus, subscribers=handlers)

    # --- Registry ---
    registry = providers.Singleton(
        DomainEventRegistryImpl,
        events=[],
    )
