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


class DomainEventRegistry(ABC):
    @abstractmethod
    def register(self, event_class: type[DomainEvent]) -> None:
        pass

    @abstractmethod
    def get_class(self, event_name: str) -> type[DomainEvent]:
        pass

    @abstractmethod
    def get_name(self, event_cls: type[DomainEvent]) -> str:
        pass
