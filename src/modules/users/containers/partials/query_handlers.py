from dependency_injector import containers, providers
from users.application.queries.get_user_by_account_id import (
    GetUserByAccountIdHandler,
    GetUserByAccountIdQuery,
)
from users.application.uow import UsersUnitOfWork

from shared.infrastructure.cqrs.buses import QueryBus


class QueryHandlersContainer(containers.DeclarativeContainer):
    """
    Query handlers container.

    To add a new query:
    1. Import the query and handler in the imports section
    2. Add the handler factory here
    3. Add to handlers dict
    """

    # --- Dependencies ---
    uow: providers.Dependency[UsersUnitOfWork] = providers.Dependency()

    # --- Handler Factories ---
    get_user_by_account_id_handler = providers.Factory(
        GetUserByAccountIdHandler, uow=uow
    )

    # --- Handlers Map ---
    handlers = providers.Dict({GetUserByAccountIdQuery: get_user_by_account_id_handler})

    # --- Bus ---
    bus = providers.Factory(QueryBus, handlers=handlers)
