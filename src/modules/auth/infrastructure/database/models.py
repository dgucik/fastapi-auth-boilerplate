import uuid

from sqlalchemy import Boolean, String
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column

from config.database import Base
from shared.infrastructure.outbox.mixin import OutboxMixin


class AccountModel(Base):
    """SQLAlchemy model for the accounts table."""

    __tablename__ = "accounts"
    __table_args__ = {"extend_existing": True}

    id: Mapped[uuid.UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True)
    email: Mapped[str] = mapped_column(String, unique=True, index=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(String, nullable=False)
    is_verified: Mapped[bool] = mapped_column(Boolean, default=False)
    is_superuser: Mapped[bool] = mapped_column(Boolean, default=False)


class AuthOutboxEvent(Base, OutboxMixin):
    """SQLAlchemy model for the auth outbox events table."""

    __tablename__ = "auth_outbox_events"
