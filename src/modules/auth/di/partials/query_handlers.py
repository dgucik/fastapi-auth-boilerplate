from dependency_injector import containers, providers

from auth.application.queries.get_account_by_id import (
    GetAccountByIdHandler,
    GetAccountByIdQuery,
)
from auth.application.queries.get_account_by_token import (
    GetAccountByTokenHandler,
    GetAccountByTokenQuery,
)
from auth.application.uow import AuthUnitOfWork
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
    uow: providers.Dependency[AuthUnitOfWork] = providers.Dependency()

    infra_services = providers.DependenciesContainer()

    # --- Handlers Factories ---
    get_account_by_token_handler = providers.Factory(
        GetAccountByTokenHandler, uow=uow, token_manager=infra_services.token_manager
    )

    get_account_by_id_handler = providers.Factory(
        GetAccountByIdHandler,
        uow=uow,
    )

    # --- Handlers Map ---
    handlers = providers.Dict(
        {
            GetAccountByTokenQuery: get_account_by_token_handler,
            GetAccountByIdQuery: get_account_by_id_handler,
        }
    )

    # --- Bus ---
    bus = providers.Factory(QueryBus, handlers=handlers)
