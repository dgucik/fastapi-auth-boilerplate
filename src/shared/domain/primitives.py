import uuid
from dataclasses import dataclass, field

from shared.domain.events import DomainEvent


@dataclass(frozen=True)
class ValueObject:
    """Base class for value objects."""

    pass


@dataclass(eq=False)
class Entity:
    """Base class for entities.

    Attributes:
        id: Unique identifier for the entity.
    """

    id: uuid.UUID = field(default_factory=uuid.uuid4, kw_only=True)

    def __eq__(self, other: object) -> bool:
        """Checks equality based on ID.

        Args:
            other: Object to compare.

        Returns:
            bool: True if IDs match, False otherwise.
        """
        if not isinstance(other, self.__class__):
            return False
        return self.id == other.id

    def __hash__(self) -> int:
        return hash(self.id)


@dataclass(eq=False)
class AggregateRoot(Entity):
    """Base class for aggregate roots.

    Maintains a list of domain events.
    """

    _events: list[DomainEvent] = field(default_factory=list, init=False, repr=False)

    def add_event(self, event: DomainEvent) -> None:
        """Adds a domain event to the aggregate.

        Args:
            event: Domain event to add.
        """
        self._events.append(event)

    def pull_events(self) -> list[DomainEvent]:
        """Retrieves and clears pending domain events.

        Returns:
            list[DomainEvent]: List of pending events.
        """
        events = self._events[:]
        self._events.clear()
        return events

    def clear_events(self) -> None:
        """Clears all pending domain events."""
        self._events.clear()
