from abc import ABC, abstractmethod
from dataclasses import dataclass
from types import TracebackType
from typing import Any

from shared.domain.events import DomainEvent


# --- UOW ---
class UnitOfWork(ABC):
    """Abstract interface for Unit of Work pattern."""

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
    """Abstract interface for domain event handlers."""

    @abstractmethod
    async def handle(self, event: TDomainEvent) -> None:
        pass


class DomainEventBus(ABC):
    """Abstract interface for domain event bus."""

    @abstractmethod
    async def publish(self, event: DomainEvent) -> None:
        pass


class DomainEventRegistry(ABC):
    """Abstract interface for domain event registry."""

    @abstractmethod
    def _register(self, event_class: type[DomainEvent]) -> None:
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
    """Abstract base class for integration events."""

    TOPIC: str = "default"

    @abstractmethod
    def to_dict(self) -> dict[str, Any]:
        pass

    @classmethod
    @abstractmethod
    def from_dict(cls, data: dict[str, Any]) -> "IntegrationEvent":
        pass


class IntegrationEventHandler[TIntegrationEvent: IntegrationEvent](ABC):
    """Abstract interface for integration event handlers."""

    @abstractmethod
    async def handle(self, event: TIntegrationEvent) -> None:
        pass


class IntegrationEventProducer(ABC):
    """Abstract interface for integration event producer."""

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
    """Abstract interface for integration event consumer."""

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
    """Base class for commands."""

    pass


@dataclass(frozen=True)
class Query:
    """Base class for queries."""

    pass


@dataclass(frozen=True)
class Dto:
    """Base class for Data Transfer Objects."""

    pass


class Handler[TMessage, TResult](ABC):
    """Abstract interface for message handlers."""

    @abstractmethod
    async def handle(self, message: TMessage) -> TResult:
        pass


class CqrsBus[TMessage, TResult](ABC):
    """Abstract interface for CQRS buses."""

    @abstractmethod
    async def dispatch(self, message: TMessage) -> TResult:
        pass
