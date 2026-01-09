from dependency_injector import containers, providers

from shared.application.ports import IntegrationEventProducer
from shared.infrastructure.messaging.event_bus import InMemoryDomainEventBus
from shared.infrastructure.messaging.event_registry import DomainEventRegistryImpl


class DomainEventHandlersContainer(containers.DeclarativeContainer):
    """
    Domain Event handlers container

    To add a new event:
    1. Import the event and handler in the imports section
    2. Add the handler factory here
    3. Add to handlers dict
    4. Add to registry
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
