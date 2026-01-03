from typing import Any, Generic, TypeVar

from shared.domain.primitives import AggregateRoot
from shared.domain.registry import AggregateRegistry

TAggregate = TypeVar("TAggregate", bound=AggregateRoot)


class BaseSqlAlchemyRepository(Generic[TAggregate]):
    def __init__(self, session: Any):
        self._session = session

    def _register(self, aggregate: TAggregate) -> TAggregate:
        if aggregate:
            AggregateRegistry.register(aggregate)
        return aggregate
