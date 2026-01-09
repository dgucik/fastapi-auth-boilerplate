import logging
from dataclasses import dataclass

from auth.application.uow import AuthUnitOfWork
from auth.domain.ports import TokenManager, TokenScope
from shared.application.ports import Command, Dto, Handler

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class RefreshTokenCommand(Command):
    refresh_token: str


@dataclass(frozen=True)
class RefreshTokenDto(Dto):
    access_token: str
    refresh_token: str
    refresh_token_expires_in_seconds: int


class RefreshTokenHandler(Handler[RefreshTokenCommand, RefreshTokenDto]):
    def __init__(self, uow: AuthUnitOfWork, token_manager: TokenManager) -> None:
        self._uow = uow
        self._token_manager = token_manager

    async def handle(self, command: RefreshTokenCommand) -> RefreshTokenDto:
        account_id = self._token_manager.decode_token(
            command.refresh_token, TokenScope.REFRESH
        )

        response = self._token_manager.issue_auth_tokens(account_id)

        logger.info(f"Token refreshed for account: {account_id}")
        return RefreshTokenDto(
            response.access_token,
            response.refresh_token,
            response.refresh_token_expires_in_seconds,
        )
