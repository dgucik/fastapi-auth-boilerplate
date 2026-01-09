from collections.abc import AsyncGenerator

from dependency_injector import containers, providers
from starlette import status
from users.containers.users import UsersContainer

from auth import AuthContainer
from config.database import scoped_session_factory
from shared.application.exceptions import (
    CommandHandlingException,
    EventReconstructionException,
    QueryExecutionException,
    UnitOfWorkException,
)
from shared.application.ports import IntegrationEventProducer
from shared.domain.exceptions import (
    BusinessRuleViolationException,
    EntityAlreadyExistsException,
    EntityNotFoundException,
    ValidationException,
)
from shared.infrastructure.exceptions.exception_handler import GlobalExceptionHandler
from shared.infrastructure.exceptions.exception_registry import (
    ExceptionMetadata,
    ExceptionRegistry,
)
from shared.infrastructure.exceptions.exceptions import (
    DatabaseConnectionException,
    ExternalServiceException,
)
from shared.infrastructure.messaging.event_producer import (
    KafkaIntegrationEventProducer,
)

SHARED_EXCEPTION_MAPPINGS = {
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


async def init_event_producer(
    bootstrap_servers: str,
) -> AsyncGenerator[IntegrationEventProducer, None]:
    producer = KafkaIntegrationEventProducer(bootstrap_servers=bootstrap_servers)
    await producer.start()
    yield producer
    await producer.stop()


class AppContainer(containers.DeclarativeContainer):
    settings = providers.Configuration()

    session_factory = providers.Singleton(lambda: scoped_session_factory)

    # --- Integration Events Publisher ----
    event_producer = providers.Resource(
        init_event_producer, bootstrap_servers=settings.kafka.BOOTSTRAP_SERVERS
    )

    # --- Module Containers ---
    auth = providers.Container(
        AuthContainer,
        settings=settings,
        session_factory=session_factory,
        event_producer=event_producer,
    )

    users = providers.Container(
        UsersContainer,
        settings=settings,
        session_factory=session_factory,
        event_producer=event_producer,
        auth_contract=auth.auth_module_adapter,
    )

    # --- Exceptions ---
    exc_registry = providers.Singleton(
        ExceptionRegistry,
        mappings_list=providers.List(
            SHARED_EXCEPTION_MAPPINGS,
            auth.exception_mappings,
            # users.exception_mappings,
        ),
    )

    exc_handler = providers.Singleton(GlobalExceptionHandler, registry=exc_registry)
