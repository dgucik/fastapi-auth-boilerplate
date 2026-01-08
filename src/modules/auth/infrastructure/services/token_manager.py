import logging
from datetime import UTC, datetime, timedelta

from jose import ExpiredSignatureError, JWTError, jwt

from auth.domain.ports import (
    AuthenticationResult,
    TokenManager,
    TokenScope,
)
from auth.infrastructure.exceptions import InvalidTokenException, TokenExpiredException

logger = logging.getLogger(__name__)


class JWTTokenManager(TokenManager):
    def __init__(
        self,
        secret_key: str,
        algorithm: str,
        access_expire_minutes: int,
        refresh_expire_days: int,
        verification_expire_minutes: int,
        password_reset_expire_minutes: int,
    ):
        self.secret_key = secret_key
        self.algorithm = algorithm
        self.access_expire_minutes = access_expire_minutes
        self.refresh_expire_days = refresh_expire_days
        self.verification_expire_minutes = verification_expire_minutes
        self.password_reset_expire_minutes = password_reset_expire_minutes

    def issue_auth_tokens(self, subject: str) -> AuthenticationResult:
        access_token = self.create_access_token(subject)
        refresh_token = self.create_refresh_token(subject)
        refresh_token_expires_in_seconds = self.refresh_token_expires_in_seconds

        logger.debug(f"Auth tokens issued for subject: {subject}")
        return AuthenticationResult(
            access_token, refresh_token, refresh_token_expires_in_seconds
        )

    def create_access_token(self, subject: str) -> str:
        return self._create_token(
            subject=subject,
            expires_delta=timedelta(minutes=self.access_expire_minutes),
            token_type=TokenScope.ACCESS,
        )

    def create_refresh_token(self, subject: str) -> str:
        return self._create_token(
            subject=subject,
            expires_delta=timedelta(days=self.refresh_expire_days),
            token_type=TokenScope.REFRESH,
        )

    def create_verification_token(self, subject: str) -> str:
        return self._create_token(
            subject=subject,
            expires_delta=timedelta(minutes=self.verification_expire_minutes),
            token_type=TokenScope.VERIFICATION,
        )

    def create_password_reset_token(self, subject: str) -> str:
        return self._create_token(
            subject=subject,
            expires_delta=timedelta(minutes=self.password_reset_expire_minutes),
            token_type=TokenScope.PASSWORD_RESET,
        )

    def _create_token(
        self, subject: str, expires_delta: timedelta, token_type: TokenScope
    ) -> str:
        expire = datetime.now(UTC) + expires_delta
        to_encode = {"exp": expire, "sub": str(subject), "type": token_type}
        encoded_jwt = jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)
        logger.debug(f"Token created: {token_type} for subject: {subject}")
        return str(encoded_jwt)

    def decode_token(self, token: str, expected_type: TokenScope) -> str:
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])

            if payload.get("type") != expected_type:
                raise InvalidTokenException("Invalid token type")

            subject = str(payload.get("sub"))
            logger.debug(f"Token decoded successfully for subject: {subject}")
            return subject
        except ExpiredSignatureError as e:
            raise TokenExpiredException from e
        except JWTError as e:
            raise InvalidTokenException from e

    @property
    def refresh_token_expires_in_seconds(self) -> int:
        return self.refresh_expire_days * 24 * 60 * 60

    @property
    def verification_token_expires_in_minutes(self) -> int:
        return self.verification_expire_minutes
