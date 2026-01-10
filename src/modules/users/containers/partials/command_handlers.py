from dependency_injector import containers, providers
from users.application.commands.delete_user_by_id import (
    DeleteUserProfileByIdCommand,
    DeleteUserProfileByIdHandler,
)
from users.application.commands.update_my_user_profile import (
    UpdateMyUserProfileCommand,
    UpdateMyUserProfileHandler,
)
from users.application.commands.update_user_profile_by_id import (
    UpdateUserProfileByIdCommand,
    UpdateUserProfileByIdHandler,
)
from users.application.uow import UsersUnitOfWork

from shared.infrastructure.cqrs.buses import CommandBus


class CommandHandlersContainer(containers.DeclarativeContainer):
    """Container for command handlers.

    Provides factories for all command handlers in the users module.
    """

    # --- Dependencies ---
    uow: providers.Dependency[UsersUnitOfWork] = providers.Dependency()
    domain_services = providers.DependenciesContainer()

    # --- Handler Factories ---
    update_my_user_profile_handler = providers.Factory(
        UpdateMyUserProfileHandler, uow=uow
    )

    update_user_profile_by_id_handler = providers.Factory(
        UpdateUserProfileByIdHandler, uow=uow
    )

    delete_user_by_id_handler = providers.Factory(DeleteUserProfileByIdHandler, uow=uow)

    # --- Handlers Map
    handlers = providers.Dict(
        {
            UpdateMyUserProfileCommand: update_my_user_profile_handler,
            UpdateUserProfileByIdCommand: update_user_profile_by_id_handler,
            DeleteUserProfileByIdCommand: delete_user_by_id_handler,
        }
    )

    # --- Bus ---
    bus = providers.Factory(CommandBus, handlers=handlers)
