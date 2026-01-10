from dependency_injector import containers, providers
from users.application.queries.get_my_user_profile import (
    GetMyUserProfileHandler,
    GetMyUserProfileQuery,
)
from users.application.queries.get_user_profile_by_id import (
    GetUserProfileByIdHandler,
    GetUserProfileByIdQuery,
)
from users.application.uow import UsersUnitOfWork

from shared.infrastructure.cqrs.buses import QueryBus


class QueryHandlersContainer(containers.DeclarativeContainer):
    """Container for query handlers.

    Provides factories for all query handlers in the users module.
    """

    # --- Dependencies ---
    uow: providers.Dependency[UsersUnitOfWork] = providers.Dependency()

    # --- Handler Factories ---
    get_my_user_profile_handler = providers.Factory(GetMyUserProfileHandler, uow=uow)

    get_user_profile_by_id_handler = providers.Factory(
        GetUserProfileByIdHandler, uow=uow
    )

    # --- Handlers Map ---
    handlers = providers.Dict(
        {
            GetMyUserProfileQuery: get_my_user_profile_handler,
            GetUserProfileByIdQuery: get_user_profile_by_id_handler,
        }
    )

    # --- Bus ---
    bus = providers.Factory(QueryBus, handlers=handlers)
