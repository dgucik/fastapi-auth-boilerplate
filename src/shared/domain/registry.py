from contextvars import ContextVar

from shared.domain.events import Event
from shared.domain.primitives import AggregateRoot


class AggregateRegistry:
    _aggregates: ContextVar[set[AggregateRoot]] = ContextVar(
        "aggregates", default=set()
    )

    @classmethod
    def register(cls, aggregate: AggregateRoot) -> None:
        if not isinstance(aggregate, AggregateRoot):
            return
        cls._aggregates.get().add(aggregate)

    @classmethod
    def pull_events(cls) -> list[Event]:
        all_events = []
        for aggregate in cls._aggregates.get():
            all_events.extend(aggregate.pull_events())
        return all_events

    @classmethod
    def clear(cls) -> None:
        cls._aggregates.set(set())
