import logging
from dataclasses import dataclass

from auth.application.uow import AuthUnitOfWork
from auth.domain.ports import TokenManager, TokenScope
from shared.application.ports import Command, Dto, Handler

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class RefreshTokenCommand(Command):
    """Command to refresh access token."""

    refresh_token: str


@dataclass(frozen=True)
class RefreshTokenDto(Dto):
    """Data Transfer Object for token refresh response."""

    access_token: str
    refresh_token: str
    refresh_token_expires_in_seconds: int


class RefreshTokenHandler(Handler[RefreshTokenCommand, RefreshTokenDto]):
    """Handler for RefreshTokenCommand."""

    def __init__(self, uow: AuthUnitOfWork, token_manager: TokenManager) -> None:
        self._uow = uow
        self._token_manager = token_manager

    async def handle(self, command: RefreshTokenCommand) -> RefreshTokenDto:
        """Processes the refresh token command.

        Args:
            command: The command data.

        Returns:
            RefreshTokenDto containing new tokens.
        """
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
