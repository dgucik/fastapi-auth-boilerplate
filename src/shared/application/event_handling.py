from abc import ABC, abstractmethod
from typing import Generic, TypeVar

from shared.domain.events import Event

TEvent = TypeVar("TEvent", bound=Event)


class EventHandler(ABC, Generic[TEvent]):
    @abstractmethod
    async def handle(self, event: TEvent) -> None:
        pass


class EventBus(ABC):
    @abstractmethod
    async def publish(self, event: Event) -> None:
        pass


class EventRegistry(ABC):
    @abstractmethod
    def register(self, event_class: type[Event]) -> None:
        pass

    @abstractmethod
    def get_class(self, event_name: str) -> type[Event]:
        pass

    @abstractmethod
    def get_name(self, event_cls: type[Event]) -> str:
        pass
