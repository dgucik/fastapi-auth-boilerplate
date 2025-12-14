from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Generic

if TYPE_CHECKING:
    from shared.application.primitives import TMessage, TResult


class UnitOfWork(ABC):
    @abstractmethod
    async def commit(self) -> None:
        pass

    @abstractmethod
    async def rollback(self) -> None:
        pass


class Handler(Generic[TMessage, TResult], ABC):
    @abstractmethod
    async def handle(self, message: TMessage) -> TResult:
        pass


class MessageBus(Generic[TMessage, TResult], ABC):
    @abstractmethod
    async def dispatch(self, message: TMessage) -> TResult:
        pass
