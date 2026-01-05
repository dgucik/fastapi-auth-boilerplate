from dataclasses import dataclass
from uuid import UUID

from auth.application.queries.common_dtos import AccountDto
from auth.application.uow import AuthUnitOfWork
from auth.contracts.exceptions import (
    ContractAccountNotFoundException,
    ContractInvalidTokenException,
    ContractTokenExpiredException,
)
from auth.domain.interfaces import TokenManager, TokenScope
from auth.infrastructure.exceptions import InvalidTokenException, TokenExpiredException
from shared.application.ports import Handler, Query


@dataclass(frozen=True)
class GetAccountByTokenQuery(Query):
    token: str


class GetAccountByTokenHandler(Handler[GetAccountByTokenQuery, AccountDto]):
    def __init__(self, uow: AuthUnitOfWork, token_manager: TokenManager):
        self._uow = uow
        self._token_manager = token_manager

    async def handle(self, query: GetAccountByTokenQuery) -> AccountDto:
        try:
            account_id = self._token_manager.decode_token(
                query.token, TokenScope.ACCESS
            )
        except TokenExpiredException as e:
            raise ContractTokenExpiredException from e
        except InvalidTokenException as e:
            raise ContractInvalidTokenException from e

        account = await self._uow.accounts.get_by_id(UUID(account_id))

        if not account:
            raise ContractAccountNotFoundException

        return AccountDto(id=account.id, email=account.email.value)
