from typing import Any

from shared.domain.primitives import AggregateRoot
from shared.domain.registry import AggregateRegistry


class BaseSqlAlchemyRepository[TAggregate: AggregateRoot]:
    """Base repository for SQLAlchemy with aggregate registration.

    Args:
        session: SQLAlchemy session.
    """

    def __init__(self, session: Any):
        """Initializes the repository."""
        self._session = session

    def _register(self, aggregate: TAggregate) -> TAggregate:
        """Registers aggregate with the global registry.

        Args:
            aggregate: Aggregate root to register.

        Returns:
            TAggregate: The registered aggregate.
        """
        if aggregate:
            AggregateRegistry.register(aggregate)
        return aggregate
