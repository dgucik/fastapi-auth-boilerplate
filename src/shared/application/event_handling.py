from abc import ABC, abstractmethod
from typing import Generic, TypeVar

from shared.domain.events import DomainEvent

TDomainEvent = TypeVar("TDomainEvent", bound=DomainEvent)


class DomainEventHandler(ABC, Generic[TDomainEvent]):
    @abstractmethod
    async def handle(self, event: TDomainEvent) -> None:
        pass


class DomainEventBus(ABC):
    @abstractmethod
    async def publish(self, event: DomainEvent) -> None:
        pass
