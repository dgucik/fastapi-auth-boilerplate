from uuid import UUID

from auth.application.queries.common_dtos import AccountDto
from auth.application.queries.get_account_by_id import GetAccountByIdQuery
from auth.application.queries.get_account_by_token import GetAccountByTokenQuery
from auth.contracts.dtos import AuthAccountDto
from auth.contracts.interfaces import AuthModuleContract
from shared.infrastructure.buses import QueryBus


class AuthModuleApi(AuthModuleContract):
    def __init__(self, query_bus: QueryBus):
        self._query_bus = query_bus

    async def get_account_by_token(self, token: str) -> AuthAccountDto:
        query = GetAccountByTokenQuery(token=token)
        dto: AccountDto = await self._query_bus.dispatch(query)
        return AuthAccountDto(id=dto.id, email=dto.email)

    async def get_account_by_id(self, id: UUID) -> AuthAccountDto:
        query = GetAccountByIdQuery(account_id=id)
        dto: AccountDto = await self._query_bus.dispatch(query)
        return AuthAccountDto(id=dto.id, email=dto.email)
