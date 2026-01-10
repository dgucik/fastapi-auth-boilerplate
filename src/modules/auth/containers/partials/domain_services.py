from dependency_injector import containers, providers

from auth.domain.services.account_authentication import AccountAuthenticationService
from auth.domain.services.account_registration import AccountRegistrationService


class DomainServicesContainer(containers.DeclarativeContainer):
    """Container for domain services."""

    # --- Dependencies ---
    infra_services = providers.DependenciesContainer()

    # --- Services ---
    account_registration_service = providers.Factory(
        AccountRegistrationService, hasher=infra_services.hasher
    )

    account_authentication_service = providers.Factory(
        AccountAuthenticationService,
        hasher=infra_services.hasher,
        token_manager=infra_services.token_manager,
    )
