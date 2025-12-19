import uuid
from abc import ABC
from dataclasses import dataclass, field

from shared.domain.events import Event


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
    _events: list[Event] = field(default_factory=list, init=False, repr=False)

    def add_event(self, event: Event) -> None:
        self._events.append(event)

    def pull_events(self) -> list[Event]:
        events = self._events[:]
        self._events.clear()
        return events

    def clear_events(self) -> None:
        self._events.clear()
