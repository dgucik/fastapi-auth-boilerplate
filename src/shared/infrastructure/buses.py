import logging
from collections.abc import Callable

from shared.application.cqrs import (
    Command,
    CqrsBus,
    Dto,
    Handler,
    Query,
    TMessage,
    TResult,
)
from shared.application.event_handling import DomainEventBus, DomainEventHandler
from shared.domain.events import DomainEvent
from shared.infrastructure.exceptions import BusException

logger = logging.getLogger(__name__)


class GenericCqrsBus(CqrsBus[TMessage, TResult]):
    def __init__(self, handlers: dict[type[TMessage], Handler[TMessage, TResult]]):
        self._handlers = handlers

    async def dispatch(self, command: TMessage) -> TResult:
        handler = self._handlers.get(type(command))
        if not handler:
            logger.error(f"No handler found for command: {type(command).__name__}")
            raise BusException
        logger.debug(f"Dispatching command: {type(command).__name__}")
        return await handler.handle(command)


class CommandBus(GenericCqrsBus[Command, None]):
    pass


class QueryBus(GenericCqrsBus[Query, Dto]):
    pass


class InMemoryDomainEventBus(DomainEventBus):
    def __init__(
        self,
        subscribers: dict[
            type[DomainEvent], list[Callable[[], DomainEventHandler[DomainEvent]]]
        ],
    ):
        self._subscribers: dict[
            type[DomainEvent], list[Callable[[], DomainEventHandler[DomainEvent]]]
        ] = subscribers or {}

    async def publish(self, event: DomainEvent) -> None:
        handler_factories = self._subscribers.get(type(event), [])
        if not handler_factories:
            logger.debug(f"No subscribers for event: {type(event).__name__}")
            return

        for handler_factory in handler_factories:
            handler = handler_factory()
            await handler.handle(event)
        logger.debug(f"Published event: {type(event).__name__}")
