from typing import Generic

from shared.application.interfaces import Handler, MessageBus
from shared.application.primitives import TMessage, TResult
from shared.infrastructure.exceptions import BusException


class SimpleMessageBus(MessageBus[TMessage, TResult], Generic[TMessage, TResult]):
    def __init__(self, handlers: dict[type[TMessage], Handler[TMessage, TResult]]):
        self._handlers = handlers

    async def dispatch(self, command: TMessage) -> TResult:
        handler = self._handlers.get(type(command))
        if not handler:
            raise BusException
        return await handler.handle(command)
