"""
Audit Ledger model.
"""
import uuid
from datetime import datetime
from sqlalchemy import BigInteger, String, ForeignKey, Text, Index, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func
from backend.models.base import Base
from typing import TYPE_CHECKING, Optional

if TYPE_CHECKING:
    from backend.models.project import MRVProject


class AuditLedger(Base):
    """
    Immutable cryptographic audit ledger.
    """
    __tablename__ = "audit_ledger"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    project_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("mrv_projects.id"), nullable=False)
    entity_type: Mapped[str] = mapped_column(String(100), nullable=False)
    entity_id: Mapped[uuid.UUID] = mapped_column(nullable=False)
    action_type: Mapped[str] = mapped_column(String(50), nullable=False)
    
    payload_sha256: Mapped[str] = mapped_column(String(64), nullable=False)
    previous_ledger_hash: Mapped[str] = mapped_column(String(64), nullable=False)
    current_ledger_hash: Mapped[str] = mapped_column(String(64), nullable=False)
    
    actor_id: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    details: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    recorded_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    project: Mapped["MRVProject"] = relationship("MRVProject")

    __table_args__ = (
        Index("idx_audit_ledger_project_id", "project_id"),
        Index("idx_audit_ledger_recorded_at", "recorded_at"),
    )
