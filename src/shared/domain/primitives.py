import uuid
from abc import ABC
from dataclasses import dataclass, field
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from shared.domain.events import DomainEvent


@dataclass(frozen=True)
class ValueObject:
    pass


@dataclass(eq=False)
class Entity(ABC):
    id: uuid.UUID = field(default_factory=uuid.uuid4, kw_only=True)

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, self.__class__):
            return False
        return self.id == other.id

    def __hash__(self) -> int:
        return hash(self.id)


@dataclass(eq=False)
class AggregateRoot(Entity):
    _events: list[DomainEvent] = field(default_factory=list, init=False, repr=False)

    def add_event(self, event: DomainEvent) -> None:
        self._events.append(event)

    def pull_events(self) -> list[DomainEvent]:
        events = self._events[:]
        self._events.clear()
        return events

    def clear_events(self) -> None:
        self._events.clear()
