import inspect
import logging
from collections.abc import Callable

from shared.application.ports import (
    DomainEventBus,
    DomainEventHandler,
)
from shared.domain.events import DomainEvent

logger = logging.getLogger(__name__)


class InMemoryDomainEventBus(DomainEventBus):
    """In-memory implementation of DomainEventBus.

    Args:
        subscribers: Map of event types to handler factories.
    """

    def __init__(
        self,
        subscribers: dict[
            type[DomainEvent], list[Callable[[], DomainEventHandler[DomainEvent]]]
        ],
    ):
        """Initializes with subscribers."""
        self._subscribers: dict[
            type[DomainEvent], list[Callable[[], DomainEventHandler[DomainEvent]]]
        ] = subscribers or {}

    async def publish(self, event: DomainEvent) -> None:
        """Publishes a domain event to all local subscribers.

        Args:
            event: The domain event to publish.
        """
        handler_factories = self._subscribers.get(type(event), [])
        if not handler_factories:
            logger.debug(f"No subscribers for event: {type(event).__name__}")
            return

        for handler_factory in handler_factories:
            handler = handler_factory()
            if inspect.isawaitable(handler):
                handler = await handler
            try:
                await handler.handle(event)
            except Exception as e:
                logger.error(f"Error in handler: {e}.")
        logger.debug(f"Published event: {type(event).__name__}")
