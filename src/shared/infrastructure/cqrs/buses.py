import logging
from typing import Any

from shared.application.ports import (
    Command,
    CqrsBus,
    Handler,
    Query,
)
from shared.infrastructure.exceptions.exceptions import BusException

logger = logging.getLogger(__name__)


class GenericCqrsBus[TMessage, TResult](CqrsBus[TMessage, TResult]):
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


class QueryBus(GenericCqrsBus[Query, Any]):
    pass
