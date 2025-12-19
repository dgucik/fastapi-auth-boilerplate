import asyncio
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


class GenericCqrsBus(CqrsBus[TMessage, TResult]):
    def __init__(self, handlers: dict[type[TMessage], Handler[TMessage, TResult]]):
        self._handlers = handlers

    async def dispatch(self, command: TMessage) -> TResult:
        handler = self._handlers.get(type(command))
        if not handler:
            raise BusException
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
        ]
        | None = None,
    ):
        self._subscribers: dict[
            type[DomainEvent], list[Callable[[], DomainEventHandler[DomainEvent]]]
        ] = subscribers or {}

    async def publish(self, event: DomainEvent, only_async: bool = False) -> None:
        handler_factories = self._subscribers.get(type(event), [])
        for handler_factory in handler_factories:
            handler = handler_factory()

            if not only_async and not handler.is_async:
                await handler.handle(event)
            elif only_async and handler.is_async:
                asyncio.create_task(handler.handle(event))
