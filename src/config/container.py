from collections.abc import Callable
from typing import Any

from aiokafka import AIOKafkaProducer
from dependency_injector import containers, providers
from starlette import status

from auth import AuthContainer
from shared.application.exceptions import (
    CommandHandlingException,
    EventReconstructionException,
    QueryExecutionException,
    UnitOfWorkException,
)
from shared.domain.exceptions import (
    BusinessRuleViolationException,
    EntityAlreadyExistsException,
    EntityNotFoundException,
    ValidationException,
)
from shared.infrastructure.exceptions.exception_handler import (
    ExceptionMetadata,
    ExceptionRegistry,
    GlobalExceptionHandler,
)
from shared.infrastructure.exceptions.exceptions import (
    DatabaseConnectionException,
    ExternalServiceException,
)
from shared.infrastructure.messaging.event_messaging import (
    KafkaIntegrationEventPublisher,
)


class AppContainer(containers.DeclarativeContainer):
    settings = providers.Configuration()

    session_factory: providers.Provider[Callable[..., Any]] = providers.Dependency()

    # --- Shared Exceptions Mappings ---
    shared_exception_mappings = providers.Dict(
        {
            ValidationException: ExceptionMetadata(
                status.HTTP_400_BAD_REQUEST, "validation_error"
            ),
            EntityNotFoundException: ExceptionMetadata(
                status.HTTP_404_NOT_FOUND, "entity_not_found"
            ),
            EntityAlreadyExistsException: ExceptionMetadata(
                status.HTTP_409_CONFLICT, "entity_already_exists"
            ),
            BusinessRuleViolationException: ExceptionMetadata(
                status.HTTP_409_CONFLICT, "business_rule_violation"
            ),
            CommandHandlingException: ExceptionMetadata(
                status.HTTP_500_INTERNAL_SERVER_ERROR, "command_handling_error"
            ),
            QueryExecutionException: ExceptionMetadata(
                status.HTTP_500_INTERNAL_SERVER_ERROR, "query_execution_error"
            ),
            EventReconstructionException: ExceptionMetadata(
                status.HTTP_500_INTERNAL_SERVER_ERROR, "event_reconstruction_error"
            ),
            UnitOfWorkException: ExceptionMetadata(
                status.HTTP_500_INTERNAL_SERVER_ERROR, "unit_of_work_error"
            ),
            DatabaseConnectionException: ExceptionMetadata(
                status.HTTP_503_SERVICE_UNAVAILABLE, "database_connection_error"
            ),
            ExternalServiceException: ExceptionMetadata(
                status.HTTP_503_SERVICE_UNAVAILABLE, "external_service_error"
            ),
        }
    )

    # --- Integration Events Publisher ----
    kafka_producer = providers.Singleton(
        AIOKafkaProducer, bootstrap_servers=settings.kafka.BOOTSTRAP_SERVERS
    )

    kafka_integration_event_publisher = providers.Factory(
        KafkaIntegrationEventPublisher, producer=kafka_producer
    )

    # --- Module Containers ---
    auth = providers.Container(
        AuthContainer,
        settings=settings,
        session_factory=session_factory,
        integration_event_publisher=kafka_integration_event_publisher,
    )

    # --- Exception Handling ---
    exception_registry = providers.Singleton(
        ExceptionRegistry,
        mappings_list=providers.List(
            shared_exception_mappings,
            auth.exception_mappings,
        ),
    )

    exception_handler = providers.Singleton(
        GlobalExceptionHandler, registry=exception_registry
    )
