import uuid

from sqlalchemy import String
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column

from config.database import Base
from shared.infrastructure.outbox.mixin import OutboxMixin


class UserModel(Base):
    __tablename__ = "users"
    __table_args__ = {"extend_existing": True}

    id: Mapped[uuid.UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True)
    account_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True), unique=True, nullable=True
    )
    username: Mapped[str] = mapped_column(
        String, unique=True, index=True, nullable=False
    )


class UsersOutboxEvent(Base, OutboxMixin):
    __tablename__ = "users_outbox_events"
