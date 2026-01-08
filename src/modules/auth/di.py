from collections.abc import Callable
from typing import Any

from dependency_injector import containers, providers
from starlette import status

from auth.application.commands.change_password import (
    ChangePasswordCommand,
    ChangePasswordHandler,
)
from auth.application.commands.login import LoginCommand, LoginHandler
from auth.application.commands.refresh_token import (
    RefreshTokenCommand,
    RefreshTokenHandler,
)
from auth.application.commands.register import RegisterCommand, RegisterHandler
from auth.application.commands.request_password_reset import (
    RequestPasswordResetCommand,
    RequestPasswordResetHandler,
)
from auth.application.commands.request_verification_token import (
    RequestVerificationTokenCommand,
    RequestVerificationTokenHandler,
)
from auth.application.commands.reset_password import (
    ResetPasswordCommand,
    ResetPasswordHandler,
)
from auth.application.commands.send_mail import SendMailCommand, SendMailHandler
from auth.application.commands.verify import VerifyEmailCommand, VerifyEmailHandler

# --- To dodałem ---
from auth.application.events.external.account_registered import AccountRegisteredHandler
from auth.application.events.integration.account_registered import (
    AccountRegisteredIntegrationHandler,
)
from auth.application.events.internal.send_password_reset_mail import (
    SendPasswordResetMailHandler,
)
from auth.application.events.internal.send_verification_mail import (
    SendVerificationMailHandler,
)
from auth.application.exceptions import PasswordsDoNotMatchException
from auth.application.queries.get_account_by_id import (
    GetAccountByIdHandler,
    GetAccountByIdQuery,
)
from auth.application.queries.get_account_by_token import (
    GetAccountByTokenHandler,
    GetAccountByTokenQuery,
)
from auth.application.uow import AuthUnitOfWork
from auth.contracts.events.account_registered import AccountRegisteredIntegrationEvent
from auth.domain.events.account_registered import AccountRegisteredDomainEvent
from auth.domain.events.password_reset_requested import (
    PasswordResetRequestedDomainEvent,
)
from auth.domain.events.verification_requested import VerificationRequestedDomainEvent
from auth.domain.exceptions import InvalidPasswordException
from auth.domain.services.account_authentication import AccountAuthenticationService
from auth.domain.services.account_registration import AccountRegistrationService
from auth.infrastructure.database.models import AuthOutboxEvent
from auth.infrastructure.database.uow import SqlAlchemyUnitOfWork
from auth.infrastructure.module_adapter import AuthModuleAdapter
from auth.infrastructure.services.mail_sender import AioSmtpMailSender
from auth.infrastructure.services.password_hasher import BcryptPasswordHasher
from auth.infrastructure.services.token_manager import JWTTokenManager
from shared.application.ports import (
    DomainEventBus,
    DomainEventRegistry,
    IntegrationEventProducer,
)
from shared.infrastructure.cqrs.buses import CommandBus, QueryBus
from shared.infrastructure.exceptions.exception_registry import ExceptionMetadata
from shared.infrastructure.messaging.event_bus import InMemoryDomainEventBus
from shared.infrastructure.messaging.event_consumer import KafkaIntegrationEventConsumer
from shared.infrastructure.messaging.event_registry import DomainEventRegistryImpl
from shared.infrastructure.outbox.processor import OutboxProcessor

AUTH_EXCPETION_MAPPINGS = {
    InvalidPasswordException: ExceptionMetadata(
        status.HTTP_401_UNAUTHORIZED, "invalid_password"
    ),
    PasswordsDoNotMatchException: ExceptionMetadata(
        status.HTTP_400_BAD_REQUEST, "password_do_not_match"
    ),
}


class InfraServicesContainer(containers.DeclarativeContainer):
    settings = providers.Configuration()

    hasher = providers.Singleton(BcryptPasswordHasher)

    token_manager = providers.Singleton(
        JWTTokenManager,
        secret_key=settings.token.SECRET_KEY,
        algorithm=settings.token.ALGORITHM,
        access_expire_minutes=settings.token.ACCESS_TOKEN_EXPIRE_MINUTES,
        refresh_expire_days=settings.token.REFRESH_TOKEN_EXPIRE_DAYS,
        verification_expire_minutes=settings.token.VERIFICATION_TOKEN_EXPIRE_MINUTES,
        password_reset_expire_minutes=settings.token.PASSWORD_RESET_EXPIRE_MINUTES,
    )

    mail_sender = providers.Singleton(AioSmtpMailSender, config=settings.mail)


class DomainServicesContainer(containers.DeclarativeContainer):
    infra_services = providers.DependenciesContainer()

    account_registration_service = providers.Factory(
        AccountRegistrationService, hasher=infra_services.hasher
    )

    account_authentication_service = providers.Factory(
        AccountAuthenticationService,
        hasher=infra_services.hasher,
        token_manager=infra_services.token_manager,
    )


class CommandHandlersContainer(containers.DeclarativeContainer):
    """
    Command handlers container.

    To add a new command:
    1. Import the command and handler in the imports section
    2. Add the handler factory here
    3. Add to handlers dict
    """

    # --- Dependencies ---
    uow: providers.Dependency[AuthUnitOfWork] = providers.Dependency()
    settings = providers.Configuration()

    infra_services = providers.DependenciesContainer()
    domain_services = providers.DependenciesContainer()

    # --- Handler Factories ---
    register_handler = providers.Factory(
        RegisterHandler,
        uow=uow,
        service=domain_services.account_registration_service,
        token_manager=infra_services.token_manager,
    )

    login_handler = providers.Factory(
        LoginHandler, uow=uow, service=domain_services.account_authentication_service
    )

    request_verification_token_handler = providers.Factory(
        RequestVerificationTokenHandler,
        uow=uow,
        token_manager=infra_services.token_manager,
    )

    verify_email_handler = providers.Factory(
        VerifyEmailHandler, uow=uow, token_manager=infra_services.token_manager
    )

    request_password_reset_handler = providers.Factory(
        RequestPasswordResetHandler, uow=uow, token_manager=infra_services.token_manager
    )

    reset_password_handler = providers.Factory(
        ResetPasswordHandler,
        uow=uow,
        token_manager=infra_services.token_manager,
        hasher=infra_services.hasher,
    )

    change_password_handler = providers.Factory(
        ChangePasswordHandler, uow=uow, hasher=infra_services.hasher
    )

    refresh_token_handler = providers.Factory(
        RefreshTokenHandler, uow=uow, token_manager=infra_services.token_manager
    )

    send_mail_handler = providers.Factory(
        SendMailHandler, mail_sender=infra_services.mail_sender
    )

    # --- Handlers Map ---
    handlers = providers.Dict(
        {
            RegisterCommand: register_handler,
            LoginCommand: login_handler,
            RequestVerificationTokenCommand: request_verification_token_handler,
            VerifyEmailCommand: verify_email_handler,
            RequestPasswordResetCommand: request_password_reset_handler,
            ResetPasswordCommand: reset_password_handler,
            ChangePasswordCommand: change_password_handler,
            RefreshTokenCommand: refresh_token_handler,
            SendMailCommand: send_mail_handler,
        }
    )

    # -- Bus ---
    bus = providers.Factory(CommandBus, handlers=handlers)


class QueryHandlersContainer(containers.DeclarativeContainer):
    """
    Query handlers container.

    To add a new query:
    1. Import the query and handler in the imports section
    2. Add the handler factory here
    3. Add to handlers dict
    """

    # --- Dependencies ---
    uow: providers.Dependency[AuthUnitOfWork] = providers.Dependency()

    infra_services = providers.DependenciesContainer()

    # --- Handlers Factories ---
    get_account_by_token_handler = providers.Factory(
        GetAccountByTokenHandler, uow=uow, token_manager=infra_services.token_manager
    )

    get_account_by_id_handler = providers.Factory(
        GetAccountByIdHandler,
        uow=uow,
    )

    # --- Handlers Map ---
    handlers = providers.Dict(
        {
            GetAccountByTokenQuery: get_account_by_token_handler,
            GetAccountByIdQuery: get_account_by_id_handler,
        }
    )

    # --- Bus ---
    bus = providers.Factory(QueryBus, handlers=handlers)


class DomainEventHandlersContainer(containers.DeclarativeContainer):
    """
    Domain Event handlers container

    To add a new event:
    1. Import the event and handler in the imports section
    2. Add the handler factory here
    3. Add to handlers dict
    4. Add to registry
    """

    # --- Dependencies ---
    settings = providers.Configuration()
    command_bus: providers.Dependency[CommandBus] = providers.Dependency()
    producer: providers.Dependency[IntegrationEventProducer] = providers.Dependency()

    # --- Event Factories ---
    send_verification_mail_handler = providers.Factory(
        SendVerificationMailHandler,
        command_bus=command_bus,
        base_url=settings.APP_BASE_URL,
    )

    send_password_reset_handler = providers.Factory(
        SendPasswordResetMailHandler,
        command_bus=command_bus,
        base_url=settings.APP_BASE_URL,
    )

    account_registered_integration_handler = providers.Factory(
        AccountRegisteredIntegrationHandler, producer=producer
    )

    # --- Handlers Map ---
    handlers = providers.Dict(
        {
            VerificationRequestedDomainEvent: providers.List(
                send_verification_mail_handler.provider
            ),
            PasswordResetRequestedDomainEvent: providers.List(
                send_password_reset_handler.provider
            ),
            AccountRegisteredDomainEvent: providers.List(
                account_registered_integration_handler.provider
            ),
        }
    )

    # --- Bus ---
    bus = providers.Singleton(InMemoryDomainEventBus, subscribers=handlers)

    # --- Registry ---
    registry = providers.Singleton(
        DomainEventRegistryImpl,
        events=[
            VerificationRequestedDomainEvent,
            AccountRegisteredDomainEvent,
            PasswordResetRequestedDomainEvent,
        ],
    )


class IntegrationEventHandlersContainer(containers.DeclarativeContainer):
    """
    Integration Event handlers container

    To add a new event:
    1. Import the event and handler in the imports section
    2. Add the handler factory here
    3. Add to handlers dict
    """

    # --- Dependencies ---
    settings = providers.Configuration()

    # --- Event Factories ---
    account_registered_handler = providers.Factory(AccountRegisteredHandler)

    # --- Handlers Map ---
    event_map = providers.Dict(
        {
            "AccountRegisteredIntegrationEvent": (
                AccountRegisteredIntegrationEvent,
                account_registered_handler,
            )
        }
    )

    # --- Event Consumer ---
    consumer = providers.Singleton(
        KafkaIntegrationEventConsumer,
        bootstrap_servers=settings.kafka.BOOTSTRAP_SERVERS,
        group_id="auth_consumer_group",
        topics=providers.List("account.registered"),
        event_map=event_map,
    )


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
