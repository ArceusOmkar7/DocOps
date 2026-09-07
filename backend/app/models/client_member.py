"""ClientMember model — one person inside a client's family/group (Phase 1.3).

In ITR season a single client (e.g. a joint family) sends one PDF bundle
containing the husband's Form 16, the wife's LIC receipt, and the father's
pension statement. Each of those documents belongs to a different taxpayer,
so sub-documents are linked to the individual member via
`documents.client_member_id`.
"""

from __future__ import annotations

import uuid

from sqlalchemy import ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..db.base import Base, TimestampMixin, UUIDPrimaryKeyMixin


class ClientMember(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "client_members"

    client_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("clients.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    pan: Mapped[str | None] = mapped_column(String(10), nullable=True, index=True)
    relation: Mapped[str | None] = mapped_column(
        String(50), nullable=True, comment="e.g. self, spouse, son, father",
    )
    email: Mapped[str | None] = mapped_column(String(255), nullable=True)
    phone: Mapped[str | None] = mapped_column(String(50), nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Relationships
    client: Mapped["Client"] = relationship(  # noqa: F821
        back_populates="members",
    )
