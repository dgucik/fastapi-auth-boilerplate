import json
import logging
from collections.abc import Callable
from typing import Any

from aiokafka import AIOKafkaConsumer, AIOKafkaProducer, ConsumerRecord

from shared.application.exceptions import EventReconstructionException
from shared.application.ports import (
    DomainEventBus,
    DomainEventHandler,
    DomainEventRegistry,
    IntegrationEvent,
    IntegrationEventConsumer,
    IntegrationEventHandler,
    IntegrationEventPublisher,
)
from shared.domain.events import DomainEvent
from shared.infrastructure.exceptions import ConsumerNotStartedException

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
        headers = [("event_type", event.__class__.__name__.encode("utf-8"))]

        await self._producer.send_and_wait(topic=topic, value=payload, headers=headers)


class KafkaIntegrationEventConsumer(IntegrationEventConsumer):
    def __init__(
        self,
        bootstrap_servers: str,
        group_id: str,
        topics: list[str],
        event_map: dict[
            str, tuple[type[Any], Callable[[], IntegrationEventHandler[Any]]]
        ],
    ) -> None:
        self._bootstrap_servers = bootstrap_servers
        self._group_id = group_id
        self._topics = topics
        self._event_map = event_map
        self._consumer: AIOKafkaConsumer | None = None
        self._is_running = False

    async def start(self) -> None:
        self._consumer = AIOKafkaConsumer(
            *self._topics,
            bootstrap_servers=self._bootstrap_servers,
            group_id=self._group_id,
            auto_offset_reset="earliest",
            enable_auto_commit=True,
        )
        await self._consumer.start()
        self._is_running = True
        logger.info(f"Kafka Consumer started on topics: {self._topics}.")

    async def stop(self) -> None:
        self._is_running = False
        if self._consumer:
            await self._consumer.stop()
            logger.info("Kafka Consumer stopped.")

    async def run_forever(self) -> None:
        if not self._consumer:
            raise ConsumerNotStartedException

        try:
            async for msg in self._consumer:
                if not self._is_running:
                    break
                await self._process_message(msg)
        except Exception as e:
            logger.error(f"Consumer loop error: {e}.")

    async def _process_message(self, msg: ConsumerRecord) -> None:
        try:
            headers = dict(msg.headers)
            event_type = headers.get("event_type", b"").decode("utf-8")

            if event_type not in self._event_map:
                return

            event_class, handler_factory = self._event_map[event_type]
            payload = json.loads(msg.value.decode("utf-8"))

            event_instance = event_class.from_dict(payload)
            handler = handler_factory()
            await handler.handle(event_instance)

        except Exception as e:
            logger.error(f"Error handling event {event_type}: {e}.")
