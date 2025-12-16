from collections.abc import Callable
from typing import Any

from dependency_injector import containers, providers

from auth.application.commands.login import LoginCommand, LoginHandler
from auth.application.commands.register import RegisterCommand, RegisterHandler
from auth.domain.services.account_authentication import AccountAuthenticationService
from auth.domain.services.account_registration import AccountRegistrationService
from auth.infrastructure.database.uow import SqlAlchemyUnitOfWork
from auth.infrastructure.services import BcryptPasswordHasher, JWTTokenService
from shared.infrastructure.buses import CommandBus


class AuthContainer(containers.DeclarativeContainer):
    settings = providers.Configuration()
    session_factory: providers.Provider[Callable[..., Any]] = providers.Dependency()

    # --- Database ---
    uow = providers.Factory(SqlAlchemyUnitOfWork, session_factory=session_factory)

    # --- Services ---
    hasher = providers.Singleton(BcryptPasswordHasher)

    token_service = providers.Singleton(
        JWTTokenService,
        secret_key=settings.SECRET_KEY,
        algorithm=settings.ALGORITHM,
        access_expire_minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES,
        refresh_expire_days=settings.REFRESH_TOKEN_EXPIRE_DAYS,
    )

    account_registration_service = providers.Factory(
        AccountRegistrationService, hasher=hasher
    )

    account_authentication_service = providers.Factory(
        AccountAuthenticationService, hasher=hasher, token_service=token_service
    )

    # Commands
    register_handler = providers.Factory(
        RegisterHandler, uow=uow, service=account_registration_service
    )

    login_handler = providers.Factory(
        LoginHandler, uow=uow, service=account_authentication_service
    )

    command_handlers = providers.Dict(
        {RegisterCommand: register_handler, LoginCommand: login_handler}
    )

    command_bus = providers.Factory(CommandBus, handlers=command_handlers)
