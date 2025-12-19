from collections.abc import Callable
from typing import Any

from dependency_injector import containers, providers

from auth.application.commands.login import LoginCommand, LoginHandler
from auth.application.commands.register import RegisterCommand, RegisterHandler
from auth.application.commands.request_verification_token import (
    RequestVerificationTokenCommand,
    RequestVerificationTokenHandler,
)
from auth.application.events.send_verification_mail import SendVerificationMail
from auth.domain.events import VerificationRequested
from auth.domain.services.account_authentication import AccountAuthenticationService
from auth.domain.services.account_registration import AccountRegistrationService
from auth.infrastructure.database.uow import SqlAlchemyUnitOfWork
from auth.infrastructure.services import (
    AioSmtpMailSender,
    BcryptPasswordHasher,
    JWTTokenManager,
)
from shared.infrastructure.buses import CommandBus, InMemoryDomainEventBus


class AuthContainer(containers.DeclarativeContainer):
    settings = providers.Configuration()
    session_factory: providers.Provider[Callable[..., Any]] = providers.Dependency()

    # --- Event Bus ---
    domain_event_bus = providers.Singleton(InMemoryDomainEventBus)

    # --- Database ---
    uow = providers.Factory(
        SqlAlchemyUnitOfWork,
        session_factory=session_factory,
        event_bus=domain_event_bus,
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
    )

    mail_sender = providers.Singleton(AioSmtpMailSender, config=settings.mail)

    # --- Domain Services ---

    account_registration_service = providers.Factory(
        AccountRegistrationService, hasher=hasher
    )

    account_authentication_service = providers.Factory(
        AccountAuthenticationService, hasher=hasher, token_manager=token_manager
    )

    # Commands
    register_handler = providers.Factory(
        RegisterHandler, uow=uow, service=account_registration_service
    )

    login_handler = providers.Factory(
        LoginHandler, uow=uow, service=account_authentication_service
    )

    request_verification_token_handler = providers.Factory(
        RequestVerificationTokenHandler, uow=uow
    )

    command_handlers = providers.Dict(
        {
            RegisterCommand: register_handler,
            LoginCommand: login_handler,
            RequestVerificationTokenCommand: request_verification_token_handler,
        }
    )

    command_bus = providers.Factory(CommandBus, handlers=command_handlers)

    # --- Event Handlers ---
    send_verification_mail_handler = providers.Factory(
        SendVerificationMail,
        token_manager=token_manager,
        mail_sender=mail_sender,
        base_url=settings.APP_BASE_URL,
    )

    domain_event_bus.add_kwargs(
        subscribers=providers.Dict(
            {
                VerificationRequested: providers.List(
                    send_verification_mail_handler.provider
                ),
            }
        )
    )
