from abc import ABC, abstractmethod
from dataclasses import dataclass
from types import TracebackType
from typing import Any

from shared.domain.events import DomainEvent


# --- UOW ---
class UnitOfWork(ABC):
    @abstractmethod
    async def commit(self) -> None:
        pass

    @abstractmethod
    async def rollback(self) -> None:
        pass

    @abstractmethod
    async def __aenter__(self) -> "UnitOfWork":
        pass

    @abstractmethod
    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: TracebackType | None,
    ) -> None:
        pass

    @abstractmethod
    def _get_outbox_model(self) -> Any:
        pass


# --- Domain Events ---
class DomainEventHandler[TDomainEvent: DomainEvent](ABC):
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


# --- Integration Events ---
@dataclass(frozen=True)
class IntegrationEvent(ABC):
    TOPIC: str = "default"

    @abstractmethod
    def to_dict(self) -> dict[str, Any]:
        pass

    @classmethod
    @abstractmethod
    def from_dict(cls, data: dict[str, Any]) -> "IntegrationEvent":
        pass


class IntegrationEventHandler[TIntegrationEvent: IntegrationEvent](ABC):
    @abstractmethod
    async def handle(self, event: TIntegrationEvent) -> None:
        pass


class IntegrationEventProducer(ABC):
    @abstractmethod
    async def start(self) -> None:
        pass

    @abstractmethod
    async def stop(self) -> None:
        pass

    @abstractmethod
    async def publish(self, topic: str, event: IntegrationEvent) -> None:
        pass


class IntegrationEventConsumer(ABC):
    @abstractmethod
    async def start(self) -> None:
        pass

    @abstractmethod
    async def stop(self) -> None:
        pass

    @abstractmethod
    async def run_forever(self) -> None:
        pass


# --- CQRS ---
type TMessage = Command | Query
type TResult = Dto | None


@dataclass(frozen=True)
class Command:
    pass


@dataclass(frozen=True)
class Query:
    pass


@dataclass(frozen=True)
class Dto:
    pass


class Handler[TMessage, TResult](ABC):
    @abstractmethod
    async def handle(self, message: TMessage) -> TResult:
        pass


class CqrsBus[TMessage, TResult](ABC):
    @abstractmethod
    async def dispatch(self, message: TMessage) -> TResult:
        pass
