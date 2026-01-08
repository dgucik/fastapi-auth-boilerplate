import json
import logging

from aiokafka import AIOKafkaProducer

from shared.application.ports import (
    IntegrationEvent,
    IntegrationEventPublisher,
)

logger = logging.getLogger(__name__)


class KafkaIntegrationEventPublisher(IntegrationEventPublisher):
    def __init__(self, producer: AIOKafkaProducer):
        self._producer = producer

    async def publish(self, topic: str, event: IntegrationEvent) -> None:
        payload = json.dumps(event.to_dict()).encode("utf-8")
        headers = [("event_type", event.__class__.__name__.encode("utf-8"))]

        await self._producer.send_and_wait(topic=topic, value=payload, headers=headers)
