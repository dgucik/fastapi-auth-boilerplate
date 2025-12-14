from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Generic, TypeVar


@dataclass(frozen=True)
class Command:
    pass


@dataclass(frozen=True)
class Query:
    pass


@dataclass(frozen=True)
class Dto:
    pass


TMessage = TypeVar("TMessage", bound=Command | Query)
TResult = TypeVar("TResult", bound=Dto | None)


class Handler(Generic[TMessage, TResult], ABC):
    @abstractmethod
    async def handle(self, message: TMessage) -> TResult:
        pass


class MessageBus(Generic[TMessage, TResult], ABC):
    @abstractmethod
    async def dispatch(self, message: TMessage) -> TResult:
        pass
