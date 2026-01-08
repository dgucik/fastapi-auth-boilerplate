import logging
from typing import Final

from passlib.context import CryptContext

from auth.domain.ports import (
    PasswordHasher,
)

logger = logging.getLogger(__name__)

BCRYPT_MAX_LENGTH: Final[int] = 72

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class BcryptPasswordHasher(PasswordHasher):
    def hash(self, password: str) -> str:
        truncated_password = password.encode("utf-8")[:BCRYPT_MAX_LENGTH]
        hashed = pwd_context.hash(truncated_password)
        logger.debug("Password hashed successfully")
        return str(hashed)

    def verify(self, plain_password: str, hashed_password: str) -> bool:
        truncated_password = plain_password.encode("utf-8")[:BCRYPT_MAX_LENGTH]
        result = bool(pwd_context.verify(truncated_password, hashed_password))
        if not result:
            logger.debug("Password verification failed")
        return result
