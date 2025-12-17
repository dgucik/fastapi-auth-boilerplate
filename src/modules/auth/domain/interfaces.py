from __future__ import annotations

from abc import ABC, abstractmethod
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


class TokenService(ABC):
    @abstractmethod
    def create_access_token(self, subject: str) -> str:
        pass

    @abstractmethod
    def create_refresh_token(self, subject: str) -> str:
        pass

    @abstractmethod
    def decode_token(self, token: str, token_type: TokenScope) -> str:
        pass

    @property
    @abstractmethod
    def refresh_token_expires_in(self) -> int:
        pass
