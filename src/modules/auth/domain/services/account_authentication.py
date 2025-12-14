from dataclasses import dataclass

from auth.domain.exceptions import InvalidPasswordException
from auth.domain.interfaces import PasswordHasher, TokenService
from auth.domain.repositories import AccountRepository
from auth.domain.value_objects import Email, PlainPassword


@dataclass(frozen=True)
class AuthenticationResponse:
    access_token: str
    refresh_token: str
    refresh_token_expires_in: int


class AccountAuthenticationService:
    def __init__(self, hasher: PasswordHasher, token_service: TokenService) -> None:
        self._hasher = hasher
        self._token_service = token_service

    async def authenticate(
        self, repo: AccountRepository, email: Email, plain_password: PlainPassword
    ) -> AuthenticationResponse:
        account = await repo.get_by_email(email)

        if not account:
            raise InvalidPasswordException

        account.login(plain_password, self._hasher)

        access_token = self._token_service.create_access_token(subject=str(account.id))
        refresh_token = self._token_service.create_refresh_token(
            subject=str(account.id)
        )
        refresh_token_expires_in = self._token_service.refresh_token_expires_in

        return AuthenticationResponse(
            access_token, refresh_token, refresh_token_expires_in
        )
