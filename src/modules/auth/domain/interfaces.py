from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import StrEnum


class PasswordHasher(ABC):
    @abstractmethod
    def hash(self, password: str) -> str:
        pass

    @abstractmethod
    def verify(self, plain: str, hashed: str) -> bool:
        pass


class TokenScope(StrEnum):
    ACCESS = "access"
    REFRESH = "refresh"
    VERIFICATION = "verification"


@dataclass(frozen=True)
class AuthenticationResult:
    access_token: str
    refresh_token: str
    refresh_token_expires_in_seconds: int


class TokenManager(ABC):
    @abstractmethod
    def issue_auth_tokens(self, subject: str) -> AuthenticationResult:
        pass

    @abstractmethod
    def create_access_token(self, subject: str) -> str:
        pass

    @abstractmethod
    def create_refresh_token(self, subject: str) -> str:
        pass

    @abstractmethod
    def create_verification_token(self, subject: str) -> str:
        pass

    @abstractmethod
    def decode_token(self, token: str, token_type: TokenScope) -> str:
        pass

    @property
    @abstractmethod
    def refresh_token_expires_in_seconds(self) -> int:
        pass

    @property
    @abstractmethod
    def verification_token_expires_in_minutes(self) -> int:
        pass


class MailSender(ABC):
    @abstractmethod
    async def send_mail(
        self,
        recipients: list[str],
        subject: str,
        verification_link: str,
    ) -> None:
        pass
