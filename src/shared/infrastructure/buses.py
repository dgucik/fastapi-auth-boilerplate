from shared.application.cqrs import (
    Command,
    Dto,
    Handler,
    MessageBus,
    Query,
    TMessage,
    TResult,
)
from shared.infrastructure.exceptions import BusException


class GenericMessageBus(MessageBus[TMessage, TResult]):
    def __init__(self, handlers: dict[type[TMessage], Handler[TMessage, TResult]]):
        self._handlers = handlers

    async def dispatch(self, command: TMessage) -> TResult:
        handler = self._handlers.get(type(command))
        if not handler:
            raise BusException
        return await handler.handle(command)


class CommandBus(GenericMessageBus[Command, None]):
    pass


class QueryBus(GenericMessageBus[Query, Dto]):
    pass
