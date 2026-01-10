from dataclasses import dataclass
from uuid import UUID

from auth.application.queries.common_dtos import AccountDto
from auth.application.uow import AuthUnitOfWork
from auth.contracts.exceptions import ContractAccountNotFoundException
from shared.application.ports import Handler, Query


@dataclass(frozen=True)
class GetAccountByIdQuery(Query):
    """Query to retrieve an account by ID."""

    account_id: UUID


class GetAccountByIdHandler(Handler[GetAccountByIdQuery, AccountDto]):
    """Handler for GetAccountByIdQuery."""

    def __init__(self, uow: AuthUnitOfWork):
        self._uow = uow

    async def handle(self, query: GetAccountByIdQuery) -> AccountDto:
        async with self._uow:
            account = await self._uow.accounts.get_by_id(query.account_id)

        if not account:
            raise ContractAccountNotFoundException

        return AccountDto(
            id=account.id, email=account.email.value, is_superuser=account.is_superuser
        )
