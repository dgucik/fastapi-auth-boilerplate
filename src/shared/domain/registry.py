from contextvars import ContextVar

from shared.domain.events import DomainEvent
from shared.domain.primitives import AggregateRoot


class AggregateRegistry:
    _aggregates: ContextVar[set[AggregateRoot] | None] = ContextVar(
        "aggregates", default=None
    )

    @classmethod
    def _get_or_init_set(cls) -> set[AggregateRoot]:
        current_set = cls._aggregates.get()
        if current_set is None:
            current_set = set()
            cls._aggregates.set(current_set)
        return current_set

    @classmethod
    def register(cls, aggregate: AggregateRoot) -> None:
        if not isinstance(aggregate, AggregateRoot):
            return
        cls._get_or_init_set().add(aggregate)

    @classmethod
    def pull_events(cls) -> list[DomainEvent]:
        all_events = []
        current_set = cls._aggregates.get()
        if current_set:
            for aggregate in current_set:
                all_events.extend(aggregate.pull_events())
        return all_events

    @classmethod
    def clear(cls) -> None:
        cls._aggregates.set(None)
