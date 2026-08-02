"""Client model — the accounting firm's end-client."""

from __future__ import annotations

import uuid

from sqlalchemy import Enum, ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..db.base import Base, TimestampMixin, UUIDPrimaryKeyMixin
from .enums import ClientStatus


class Client(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "clients"

    organization_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("organizations.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    tax_id: Mapped[str | None] = mapped_column(String(50), nullable=True)
    email: Mapped[str | None] = mapped_column(String(255), nullable=True)
    phone: Mapped[str | None] = mapped_column(String(50), nullable=True)
    contact_person: Mapped[str | None] = mapped_column(String(255), nullable=True)
    status: Mapped[ClientStatus] = mapped_column(
        Enum(ClientStatus, name="client_status", native_enum=True),
        nullable=False,
        default=ClientStatus.on_track,
    )

    # Relationships
    organization: Mapped["Organization"] = relationship(  # noqa: F821
        back_populates="clients",
    )
    documents: Mapped[list["Document"]] = relationship(  # noqa: F821
        back_populates="client", lazy="selectin",
    )
    workflows: Mapped[list["Workflow"]] = relationship(  # noqa: F821
        back_populates="client", lazy="selectin",
    )
