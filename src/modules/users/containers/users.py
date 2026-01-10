import asyncio
from collections.abc import AsyncGenerator, Callable
from typing import Any

from dependency_injector import containers, providers
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker
from users.containers.partials.command_handlers import CommandHandlersContainer
from users.containers.partials.domain_event_handlers import DomainEventHandlersContainer
from users.containers.partials.domain_services import DomainServicesContainer
from users.containers.partials.exception_mappings import USERS_EXCEPTION_MAPPINGS
from users.containers.partials.integration_event_handlers import (
    IntegrationEventHandlersContainer,
)
from users.containers.partials.query_handlers import QueryHandlersContainer
from users.infrastructure.database.models import UsersOutboxEvent
from users.infrastructure.database.uow import SqlAlchemyUsersUnitOfWork

from auth.contracts.module_port import AuthModulePort
from shared.application.ports import (
    DomainEventBus,
    DomainEventRegistry,
    IntegrationEventProducer,
)
from shared.infrastructure.outbox.mixin import OutboxMixin
from shared.infrastructure.outbox.processor import OutboxProcessor


async def init_outbox_processor(
    session_factory: async_sessionmaker[AsyncSession],
    event_bus: DomainEventBus,
    event_registry: DomainEventRegistry,
    outbox_model: type[OutboxMixin],
    batch_size: int,
) -> AsyncGenerator[None, None]:
    """Initializes and runs the outbox processor.

    Args:
        session_factory: SQLAlchemy session factory.
        event_bus: Domain event bus.
        event_registry: Domain event registry.
        outbox_model: Model class for outbox events.
        batch_size: Number of events to process per batch.

    Yields:
        None: Yields control back to the caller while running.
    """
    processor = OutboxProcessor(
        session_factory=session_factory,
        event_bus=event_bus,
        event_registry=event_registry,
        outbox_model=outbox_model,
        batch_size=batch_size,
    )
    task = asyncio.create_task(
        processor.run_forever(interval=0.5), name="users_outbox_task"
    )
    yield
    task.cancel()
    try:
        await task
    except asyncio.CancelledError:
        pass


class UsersContainer(containers.DeclarativeContainer):
    """Main container for the Users module.

    Wires together all sub-containers and dependencies.
    """

    # --- Dependencies ---
    event_producer: providers.Dependency[IntegrationEventProducer] = (
        providers.Dependency()
    )
    settings = providers.Configuration()
    session_factory: providers.Provider[Callable[..., Any]] = providers.Dependency()

    # --- External Contracts ---
    auth_contract: providers.Provider[AuthModulePort] = providers.Dependency()

    # --- Placeholders ----
    event_bus: providers.Dependency[DomainEventBus] = providers.Dependency()
    event_registry: providers.Dependency[DomainEventRegistry] = providers.Dependency()

    # --- Unit of Work ---
    uow = providers.Factory(
        SqlAlchemyUsersUnitOfWork,
        session_factory=session_factory,
        event_registry=event_registry,
    )

    outbox_processor = providers.Resource(
        init_outbox_processor,
        session_factory=session_factory,
        event_bus=event_bus,
        event_registry=event_registry,
        outbox_model=providers.Object(UsersOutboxEvent),
        batch_size=20,
    )

    # --- Sub-Containers ---
    domain_services = providers.Container(DomainServicesContainer)
    command_handlers = providers.Container(
        CommandHandlersContainer, uow=uow, domain_services=domain_services
    )
    query_handlers = providers.Container(QueryHandlersContainer, uow=uow)
    domain_event_handlers = providers.Container(
        DomainEventHandlersContainer,
        settings=settings,
        producer=event_producer,
    )
    integration_event_handlers = providers.Container(
        IntegrationEventHandlersContainer,
        settings=settings,
        domain_services=domain_services,
        uow=uow,
    )

    # --- Overrides ---
    event_bus.override(domain_event_handlers.bus)
    event_registry.override(domain_event_handlers.registry)
    command_handlers.uow.override(uow)
    query_handlers.uow.override(uow)
    integration_event_handlers.uow.override(uow)

    # --- Convenience aliases ---
    command_bus = command_handlers.bus
    query_bus = query_handlers.bus
    event_consumer = integration_event_handlers.consumer
    exception_mappings = providers.Object(USERS_EXCEPTION_MAPPINGS)
