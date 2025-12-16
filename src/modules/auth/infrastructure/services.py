from datetime import datetime, timedelta
from typing import Final

from jose import ExpiredSignatureError, JWTError, jwt
from passlib.context import CryptContext

from auth.domain.interfaces import PasswordHasher, TokenService
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
        expire = datetime.utcnow() + timedelta(minutes=self.access_expire_minutes)
        to_encode = {"exp": expire, "sub": subject}
        return str(jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm))

    def create_refresh_token(self, subject: str) -> str:
        expire = datetime.utcnow() + timedelta(days=self.refresh_expire_days)
        to_encode = {"exp": expire, "sub": subject}
        return str(jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm))

    def decode_token(self, token: str) -> str:
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            return str(payload.get("sub"))
        except ExpiredSignatureError as err:
            raise TokenExpiredException from err
        except JWTError as err:
            raise InvalidTokenException from err

    @property
    def refresh_token_expires_in(self) -> int:
        return self.refresh_expire_days * 24 * 60 * 60
