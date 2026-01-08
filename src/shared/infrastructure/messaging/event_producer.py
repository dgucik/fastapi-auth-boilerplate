import json
import logging

from aiokafka import AIOKafkaProducer

from shared.application.ports import (
    IntegrationEvent,
    IntegrationEventProducer,
)
from shared.infrastructure.exceptions.exceptions import ProducerNotStartedException

logger = logging.getLogger(__name__)


class KafkaIntegrationEventProducer(IntegrationEventProducer):
    def __init__(self, bootstrap_servers: str) -> None:
        self._bootstrap_servers = bootstrap_servers
        self._producer: AIOKafkaProducer | None = None

    async def start(self) -> None:
        self._producer = AIOKafkaProducer(bootstrap_servers=self._bootstrap_servers)
        await self._producer.start()
        logger.info("Kafka producer started.")

    async def stop(self) -> None:
        if self._producer:
            await self._producer.stop()
            logger.info("Kafka producer stopped.")

    async def publish(self, topic: str, event: IntegrationEvent) -> None:
        if not self._producer:
            raise ProducerNotStartedException
        payload = json.dumps(event.to_dict()).encode("utf-8")
        headers = [("event_type", event.__class__.__name__.encode("utf-8"))]

        await self._producer.send_and_wait(topic=topic, value=payload, headers=headers)
