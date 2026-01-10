import inspect
import json
import logging
from collections.abc import Callable
from typing import Any

from aiokafka import AIOKafkaConsumer, ConsumerRecord

from shared.application.ports import (
    IntegrationEventConsumer,
    IntegrationEventHandler,
)
from shared.infrastructure.exceptions.exceptions import ConsumerNotStartedException

logger = logging.getLogger(__name__)


class KafkaIntegrationEventConsumer(IntegrationEventConsumer):
    """Kafka implementation of integration event consumer.

    Args:
        bootstrap_servers: Kafka servers.
        group_id: Consumer group.
        topics: Topics to subscribe to.
        event_map: Mapping of event names to handlers.
    """

    def __init__(
        self,
        bootstrap_servers: str,
        group_id: str,
        topics: list[str],
        event_map: dict[
            str, tuple[type[Any], Callable[[], IntegrationEventHandler[Any]]]
        ],
    ) -> None:
        """Initializes the consumer."""
        self._bootstrap_servers = bootstrap_servers
        self._group_id = group_id
        self._topics = topics
        self._event_map = event_map
        self._consumer: AIOKafkaConsumer | None = None
        self._is_running = False

    async def start(self) -> None:
        """Starts the Kafka consumer."""
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
        """Stops the Kafka consumer."""
        self._is_running = False
        if self._consumer:
            await self._consumer.stop()
            logger.info("Kafka Consumer stopped.")

    async def run_forever(self) -> None:
        """Runs the consumer loop indefinitely.

        Raises:
            ConsumerNotStartedException: If consumer isn't started.
        """
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

            event_class, handler_provider = self._event_map[event_type]
            payload = json.loads(msg.value.decode("utf-8"))
            event_instance = event_class.from_dict(payload)

            if callable(handler_provider):
                handler = handler_provider()
                if inspect.isawaitable(handler):
                    handler = await handler
            else:
                handler = handler_provider

            await handler.handle(event_instance)

        except Exception as e:
            logger.error(f"Error handling event {event_type}: {e}", exc_info=True)
