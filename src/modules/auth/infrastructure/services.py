from datetime import UTC, datetime, timedelta
from typing import Final

from jose import ExpiredSignatureError, JWTError, jwt
from passlib.context import CryptContext

from auth.domain.interfaces import PasswordHasher, TokenScope, TokenService
from auth.infrastructure.exceptions import InvalidTokenException, TokenExpiredException

BCRYPT_MAX_LENGTH: Final[int] = 72

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class BcryptPasswordHasher(PasswordHasher):
    def hash(self, password: str) -> str:
        truncated_password = password.encode("utf-8")[:BCRYPT_MAX_LENGTH]
        return str(pwd_context.hash(truncated_password))

    def verify(self, plain_password: str, hashed_password: str) -> bool:
        truncated_password = plain_password.encode("utf-8")[:BCRYPT_MAX_LENGTH]
        return bool(pwd_context.verify(truncated_password, hashed_password))


class JWTTokenService(TokenService):
    def __init__(
        self,
        secret_key: str,
        algorithm: str,
        access_expire_minutes: int,
        refresh_expire_days: int,
    ):
        self.secret_key = secret_key
        self.algorithm = algorithm
        self.access_expire_minutes = access_expire_minutes
        self.refresh_expire_days = refresh_expire_days

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

    def _create_token(
        self, subject: str, expires_delta: timedelta, token_type: TokenScope
    ) -> str:
        expire = datetime.now(UTC) + expires_delta
        to_encode = {"exp": expire, "sub": str(subject), "type": token_type}
        encoded_jwt = jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)
        return str(encoded_jwt)

    def decode_token(self, token: str, expected_type: TokenScope) -> str:
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])

            if payload.get("type") != expected_type:
                raise InvalidTokenException("Invalid token type")

            return str(payload.get("sub"))
        except ExpiredSignatureError as e:
            raise TokenExpiredException from e
        except JWTError as e:
            raise InvalidTokenException from e

    @property
    def refresh_token_expires_in_seconds(self) -> int:
        return self.refresh_expire_days * 24 * 60 * 60
