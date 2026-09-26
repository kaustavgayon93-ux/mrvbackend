"""
Organization model.
"""
from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from backend.models.base import Base, BaseModelMixin
from typing import TYPE_CHECKING, List

if TYPE_CHECKING:
    from backend.models.project import MRVProject
    from backend.models.user import User


class Organization(BaseModelMixin, Base):
    """
    Represents an organization managing MRV projects.
    """
    __tablename__ = "organizations"

    name: Mapped[str] = mapped_column(String(255), nullable=False)
    country_code: Mapped[str] = mapped_column(String(2), default="IN", nullable=False)
    contact_email: Mapped[str | None] = mapped_column(String(255), nullable=True)

    projects: Mapped[List["MRVProject"]] = relationship("MRVProject", back_populates="organization", cascade="all, delete-orphan")
    users: Mapped[List["User"]] = relationship("User", back_populates="organization")
