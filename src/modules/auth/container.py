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
from auth.application.events.handlers.send_password_reset_mail import (
    SendPasswordResetMailHandler,
)
from auth.application.events.handlers.send_verification_mail import (
    SendVerificationMailHandler,
)
from auth.application.events.publishers.account_registered import (
    AccountRegisteredIntegrationHandler,
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
from shared.application.ports import IntegrationEventPublisher
from shared.infrastructure.cqrs_buses import CommandBus, QueryBus
from shared.infrastructure.event_messaging import (
    DomainEventRegistryImpl,
    InMemoryDomainEventBus,
)
from shared.infrastructure.exception_handler import ExceptionMetadata
from shared.infrastructure.outbox import OutboxProcessor


class AuthContainer(containers.DeclarativeContainer):
    integration_event_publisher: providers.Dependency[IntegrationEventPublisher] = (
        providers.Dependency()
    )
    settings = providers.Configuration()
    session_factory: providers.Provider[Callable[..., Any]] = providers.Dependency()

    # --- Event Bus & Event Registry ---
    domain_event_bus = providers.Singleton(InMemoryDomainEventBus)

    domain_event_registry = providers.Singleton(
        DomainEventRegistryImpl,
        events=[
            VerificationRequestedDomainEvent,
            AccountRegisteredDomainEvent,
            PasswordResetRequestedDomainEvent,
        ],
    )

    # --- Unit of Work ---
    uow = providers.Factory(
        SqlAlchemyUnitOfWork,
        session_factory=session_factory,
        event_bus=domain_event_bus,
        event_registry=domain_event_registry,
    )

    # --- Infra Services ---
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

    # --- Domain Services ---
    account_registration_service = providers.Factory(
        AccountRegistrationService, hasher=hasher
    )

    account_authentication_service = providers.Factory(
        AccountAuthenticationService, hasher=hasher, token_manager=token_manager
    )

    # --- Commands & Handlers ---
    register_handler = providers.Factory(
        RegisterHandler,
        uow=uow,
        service=account_registration_service,
        token_manager=token_manager,
    )

    login_handler = providers.Factory(
        LoginHandler, uow=uow, service=account_authentication_service
    )

    request_verification_token_handler = providers.Factory(
        RequestVerificationTokenHandler, uow=uow, token_manager=token_manager
    )

    verify_email_handler = providers.Factory(
        VerifyEmailHandler, uow=uow, token_manager=token_manager
    )

    request_password_reset_handler = providers.Factory(
        RequestPasswordResetHandler, uow=uow, token_manager=token_manager
    )

    reset_password_handler = providers.Factory(
        ResetPasswordHandler, uow=uow, token_manager=token_manager, hasher=hasher
    )

    change_password_handler = providers.Factory(
        ChangePasswordHandler, uow=uow, hasher=hasher
    )

    refresh_token_handler = providers.Factory(
        RefreshTokenHandler, uow=uow, token_manager=token_manager
    )

    send_mail_handler = providers.Factory(SendMailHandler, mail_sender=mail_sender)

    command_handlers = providers.Dict(
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

    # -- Command Bus ---
    command_bus = providers.Factory(CommandBus, handlers=command_handlers)

    # --- Queries & Handlers ---
    get_account_by_token_handler = providers.Factory(
        GetAccountByTokenHandler, uow=uow, token_manager=token_manager
    )

    get_account_by_id_handler = providers.Factory(
        GetAccountByIdHandler,
        uow=uow,
    )

    query_handlers = providers.Dict(
        {
            GetAccountByTokenQuery: get_account_by_token_handler,
            GetAccountByIdQuery: get_account_by_id_handler,
        }
    )
    # --- Query Bus ---
    query_bus = providers.Factory(QueryBus, handlers=query_handlers)

    # --- Event Handlers ---
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
        AccountRegisteredIntegrationHandler, publisher=integration_event_publisher
    )

    # --- Event Bus Subscribers Registration ---
    domain_event_bus.add_kwargs(
        subscribers=providers.Dict(
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
    )

    # --- Outbox processor ---
    outbox_processor = providers.Singleton(
        OutboxProcessor,
        session_factory=session_factory,
        event_bus=domain_event_bus,
        registry=domain_event_registry,
        outbox_model=providers.Object(AuthOutboxEvent),
        batch_size=20,
    )

    # --- Exception Mappings ---
    exception_mappings = providers.Dict(
        {
            InvalidPasswordException: ExceptionMetadata(
                status.HTTP_401_UNAUTHORIZED, "invalid_password"
            ),
            PasswordsDoNotMatchException: ExceptionMetadata(
                status.HTTP_400_BAD_REQUEST, "password_do_not_match"
            ),
        }
    )

    # --- Module Contract ---
    auth_module_adapter = providers.Factory(AuthModuleAdapter, query_bus=query_bus)
