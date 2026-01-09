from collections.abc import Callable
from typing import Any

from dependency_injector import containers, providers

from auth.di.partials.command_handlers import CommandHandlersContainer
from auth.di.partials.domain_event_handlers import DomainEventHandlersContainer
from auth.di.partials.domain_services import DomainServicesContainer
from auth.di.partials.exception_mappings import AUTH_EXCEPTION_MAPPINGS
from auth.di.partials.infra_services import InfraServicesContainer
from auth.di.partials.integration_event_handlers import (
    IntegrationEventHandlersContainer,
)
from auth.di.partials.query_handlers import QueryHandlersContainer
from auth.infrastructure.database.models import AuthOutboxEvent
from auth.infrastructure.database.uow import SqlAlchemyUnitOfWork
from auth.infrastructure.module_adapter import AuthModuleAdapter
from shared.application.ports import (
    DomainEventBus,
    DomainEventRegistry,
    IntegrationEventProducer,
)
from shared.infrastructure.outbox.processor import OutboxProcessor


class AuthContainer(containers.DeclarativeContainer):
    # --- Dependencies ---
    event_producer: providers.Dependency[IntegrationEventProducer] = (
        providers.Dependency()
    )
    settings = providers.Configuration()
    session_factory: providers.Provider[Callable[..., Any]] = providers.Dependency()

    # --- Placeholders ----
    event_bus: providers.Dependency[DomainEventBus] = providers.Dependency()
    event_registry: providers.Dependency[DomainEventRegistry] = providers.Dependency()

    # --- Unit of Work ---
    uow = providers.Factory(
        SqlAlchemyUnitOfWork,
        session_factory=session_factory,
        event_bus=event_bus,
        event_registry=event_registry,
    )

    outbox_processor = providers.Singleton(
        OutboxProcessor,
        session_factory=session_factory,
        event_bus=event_bus,
        event_registry=event_registry,
        outbox_model=providers.Object(AuthOutboxEvent),
        batch_size=20,
    )

    # --- Sub-Containers ---
    infra_services = providers.Container(InfraServicesContainer, settings=settings)
    domain_services = providers.Container(
        DomainServicesContainer, infra_services=infra_services
    )
    command_handlers = providers.Container(
        CommandHandlersContainer,
        uow=uow,
        settings=settings,
        infra_services=infra_services,
        domain_services=domain_services,
    )
    query_handlers = providers.Container(
        QueryHandlersContainer, uow=uow, infra_services=infra_services
    )
    domain_event_handlers = providers.Container(
        DomainEventHandlersContainer,
        settings=settings,
        command_bus=command_handlers.bus,
        producer=event_producer,
    )
    integration_event_handlers = providers.Container(
        IntegrationEventHandlersContainer, settings=settings
    )

    # --- Module Contract ---
    auth_module_adapter = providers.Factory(
        AuthModuleAdapter, query_bus=query_handlers.bus
    )

    # --- Overrides ---
    event_bus.override(domain_event_handlers.bus)
    event_registry.override(domain_event_handlers.registry)

    # --- Convenience aliases ---
    command_bus = command_handlers.bus
    query_bus = query_handlers.bus
    token_manager = infra_services.token_manager
    event_consumer = integration_event_handlers.consumer
    exception_mappings = providers.Object(AUTH_EXCEPTION_MAPPINGS)
