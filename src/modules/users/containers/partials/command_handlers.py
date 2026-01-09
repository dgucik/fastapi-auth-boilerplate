from dependency_injector import containers, providers
from users.application.uow import UsersUnitOfWork

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
    uow: providers.Dependency[UsersUnitOfWork] = providers.Dependency()
    domain_services = providers.DependenciesContainer()

    # --- Handler Factories ---

    # --- Handlers Map
    handlers = providers.Dict({})

    # --- Bus ---
    bus = providers.Factory(CommandBus, handlers=handlers)
