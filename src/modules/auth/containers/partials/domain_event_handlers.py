from dependency_injector import containers, providers

from auth.application.events.integration.account_registered import (
    AccountRegisteredIntegrationHandler,
)
from auth.application.events.internal.send_password_reset_mail import (
    SendPasswordResetMailHandler,
)
from auth.application.events.internal.send_verification_mail import (
    SendVerificationMailHandler,
)
from auth.domain.events.account_registered import AccountRegisteredDomainEvent
from auth.domain.events.password_reset_requested import (
    PasswordResetRequestedDomainEvent,
)
from auth.domain.events.verification_requested import VerificationRequestedDomainEvent
from shared.application.ports import (
    IntegrationEventProducer,
)
from shared.infrastructure.messaging.event_bus import InMemoryDomainEventBus
from shared.infrastructure.messaging.event_registry import DomainEventRegistryImpl


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
    infra_services = providers.DependenciesContainer()
    producer: providers.Dependency[IntegrationEventProducer] = providers.Dependency()

    # --- Event Factories ---
    send_verification_mail_handler = providers.Factory(
        SendVerificationMailHandler,
        mail_sender=infra_services.mail_sender,
        base_url=settings.APP_BASE_URL,
    )

    send_password_reset_handler = providers.Factory(
        SendPasswordResetMailHandler,
        mail_sender=infra_services.mail_sender,
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
