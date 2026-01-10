import logging

from shared.application.exceptions import EventReconstructionException
from shared.application.ports import (
    DomainEventRegistry,
)
from shared.domain.events import DomainEvent

logger = logging.getLogger(__name__)


class DomainEventRegistryImpl(DomainEventRegistry):
    """Implementation of Domain Event Registry.

    Args:
        events: Optional list of events to pre-register.
    """

    def __init__(self, events: list[type[DomainEvent]] | None = None):
        """Initializes registry and registers events."""
        self._name_to_cls: dict[str, type[DomainEvent]] = {}
        self._cls_to_name: dict[type[DomainEvent], str] = {}

        if events:
            for event in events:
                self._register(event)

    def _register(self, event_class: type[DomainEvent]) -> None:
        """Registers a domain event class."""
        event_name = event_class.__name__

        self._name_to_cls[event_name] = event_class
        self._cls_to_name[event_class] = event_name

    def get_class(self, event_name: str) -> type[DomainEvent]:
        """Retrieves event class by name.

        Args:
            event_name: Name of the event.

        Returns:
            type[DomainEvent]: The event class.

        Raises:
            EventReconstructionException: If event is not registered.
        """
        if event_name not in self._name_to_cls:
            raise EventReconstructionException(f"Event {event_name} not registered.")
        return self._name_to_cls[event_name]

    def get_name(self, event_cls: type[DomainEvent]) -> str:
        """Retrieves name for an event class."""
        return self._cls_to_name.get(event_cls, event_cls.__name__)
