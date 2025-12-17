from abc import ABC, abstractmethod
from typing import Generic, TypeVar

from shared.domain.events import DomainEvent

TEvent = TypeVar("TEvent", bound=DomainEvent)


class EventHandler(ABC, Generic[TEvent]):
    @abstractmethod
    async def handle(self, event: TEvent) -> None:
        pass


class DomainEventHandler(EventHandler[TEvent], ABC):
    pass


class EventBus(ABC, Generic[TEvent]):
    @abstractmethod
    async def publish(self, event: TEvent) -> None:
        pass
