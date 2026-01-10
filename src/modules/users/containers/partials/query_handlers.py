from dependency_injector import containers, providers
from users.application.queries.get_user import GetUserHandler, GetUserQuery
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
    get_user_handler = providers.Factory(GetUserHandler, uow=uow)
    # --- Handlers Map ---
    handlers = providers.Dict({GetUserQuery: get_user_handler})

    # --- Bus ---
    bus = providers.Factory(QueryBus, handlers=handlers)
