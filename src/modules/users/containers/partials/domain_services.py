from dependency_injector import containers, providers
from users.domain.services.user_creation import UserCreationService


class DomainServicesContainer(containers.DeclarativeContainer):
    """Container for domain services."""

    user_creation_service = providers.Factory(UserCreationService)
