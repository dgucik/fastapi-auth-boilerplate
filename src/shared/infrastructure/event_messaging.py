import json
import logging
from collections.abc import Callable

from aiokafka import AIOKafkaProducer

from shared.application.exceptions import EventReconstructionException
from shared.application.ports import (
    DomainEventBus,
    DomainEventHandler,
    DomainEventRegistry,
    IntegrationEvent,
    IntegrationEventPublisher,
)
from shared.domain.events import DomainEvent

logger = logging.getLogger(__name__)


class DomainEventRegistryImpl(DomainEventRegistry):
    def __init__(self, events: list[type[DomainEvent]] | None = None):
        self._name_to_cls: dict[str, type[DomainEvent]] = {}
        self._cls_to_name: dict[type[DomainEvent], str] = {}

        if events:
            for event in events:
                self.register(event)

    def register(self, event_class: type[DomainEvent]) -> None:
        event_name = event_class.__name__

        self._name_to_cls[event_name] = event_class
        self._cls_to_name[event_class] = event_name

    def get_class(self, event_name: str) -> type[DomainEvent]:
        if event_name not in self._name_to_cls:
            raise EventReconstructionException(f"Event {event_name} not registered.")
        return self._name_to_cls[event_name]

    def get_name(self, event_cls: type[DomainEvent]) -> str:
        return self._cls_to_name.get(event_cls, event_cls.__name__)


class InMemoryDomainEventBus(DomainEventBus):
    def __init__(
        self,
        subscribers: dict[
            type[DomainEvent], list[Callable[[], DomainEventHandler[DomainEvent]]]
        ],
    ):
        self._subscribers: dict[
            type[DomainEvent], list[Callable[[], DomainEventHandler[DomainEvent]]]
        ] = subscribers or {}

    async def publish(self, event: DomainEvent) -> None:
        handler_factories = self._subscribers.get(type(event), [])
        if not handler_factories:
            logger.debug(f"No subscribers for event: {type(event).__name__}")
            return

        for handler_factory in handler_factories:
            handler = handler_factory()
            await handler.handle(event)
        logger.debug(f"Published event: {type(event).__name__}")


class KafkaIntegrationEventPublisher(IntegrationEventPublisher):
    def __init__(self, producer: AIOKafkaProducer):
        self._producer = producer

    async def publish(self, topic: str, event: IntegrationEvent) -> None:
        payload = json.dumps(event.to_dict()).encode("utf-8")
        await self._producer.send_and_wait(
            topic=topic,
            value=payload,
        )
