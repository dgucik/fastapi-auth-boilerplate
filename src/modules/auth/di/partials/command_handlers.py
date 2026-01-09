from dependency_injector import containers, providers

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
from auth.application.uow import AuthUnitOfWork
from shared.infrastructure.cqrs.buses import CommandBus


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
