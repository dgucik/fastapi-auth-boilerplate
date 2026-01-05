from typing import Any

from shared.domain.primitives import AggregateRoot
from shared.domain.registry import AggregateRegistry


class BaseSqlAlchemyRepository[TAggregate: AggregateRoot]:
    def __init__(self, session: Any):
        self._session = session

    def _register(self, aggregate: TAggregate) -> TAggregate:
        if aggregate:
            AggregateRegistry.register(aggregate)
        return aggregate
