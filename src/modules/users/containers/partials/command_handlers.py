from dependency_injector import containers, providers
from users.application.commands.delete_user_by_id import (
    DeleteUserByIdCommand,
    DeleteUserByIdHandler,
)
from users.application.commands.update_user import UpdateUserCommand, UpdateUserHandler
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
    update_user_handler = providers.Factory(UpdateUserHandler, uow=uow)
    delete_user_by_id_handler = providers.Factory(DeleteUserByIdHandler, uow=uow)

    # --- Handlers Map
    handlers = providers.Dict(
        {
            UpdateUserCommand: update_user_handler,
            DeleteUserByIdCommand: delete_user_by_id_handler,
        }
    )

    # --- Bus ---
    bus = providers.Factory(CommandBus, handlers=handlers)
