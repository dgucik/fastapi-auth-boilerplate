import os
from datetime import UTC, datetime, timedelta
from email.message import EmailMessage
from typing import Any, Final

import aiosmtplib
from jinja2 import Environment, FileSystemLoader, select_autoescape
from jose import ExpiredSignatureError, JWTError, jwt
from passlib.context import CryptContext

from auth.domain.interfaces import MailSender, PasswordHasher, TokenManager, TokenScope
from auth.infrastructure.exceptions import InvalidTokenException, TokenExpiredException
from config import MailSettings

BCRYPT_MAX_LENGTH: Final[int] = 72

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class BcryptPasswordHasher(PasswordHasher):
    def hash(self, password: str) -> str:
        truncated_password = password.encode("utf-8")[:BCRYPT_MAX_LENGTH]
        return str(pwd_context.hash(truncated_password))

    def verify(self, plain_password: str, hashed_password: str) -> bool:
        truncated_password = plain_password.encode("utf-8")[:BCRYPT_MAX_LENGTH]
        return bool(pwd_context.verify(truncated_password, hashed_password))


class JWTTokenManager(TokenManager):
    def __init__(
        self,
        secret_key: str,
        algorithm: str,
        access_expire_minutes: int,
        refresh_expire_days: int,
        verification_expire_minutes: int,
    ):
        self.secret_key = secret_key
        self.algorithm = algorithm
        self.access_expire_minutes = access_expire_minutes
        self.refresh_expire_days = refresh_expire_days
        self.verification_expire_minutes = verification_expire_minutes

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

    @property
    def verification_token_expires_in_minutes(self) -> int:
        return self.verification_expire_minutes


class AioSmtpMailSender(MailSender):
    def __init__(self, config: MailSettings | dict[str, Any]) -> None:
        if isinstance(config, dict):
            self._config = MailSettings(**config)
        else:
            self._config = config

        current_dir = os.path.dirname(os.path.abspath(__file__))
        template_path = os.path.join(current_dir, "templates")

        self._jinja_env = Environment(
            loader=FileSystemLoader(template_path),
            autoescape=select_autoescape(["html", "xml"]),
        )

    async def send_mail(
        self,
        recipients: list[str],
        subject: str,
        verification_link: str,
        verification_token_expires_in_minutes: int,
    ) -> None:
        template = self._jinja_env.get_template("verification_mail.html")

        html_content = template.render(
            verification_link=verification_link,
            verification_token_expires_in_minutes=verification_token_expires_in_minutes,
        )

        message = EmailMessage()
        message["From"] = self._config.FROM
        message["To"] = ", ".join(recipients)
        message["Subject"] = subject
        message.add_alternative(html_content, subtype="html")

        await aiosmtplib.send(
            message,
            hostname=self._config.SERVER,
            port=self._config.PORT,
            username=self._config.USERNAME,
            password=self._config.PASSWORD,
            use_tls=False,
            start_tls=True,
        )
