"""
Sample Plot model.
"""
import uuid
from sqlalchemy import String, ForeignKey, Numeric
from sqlalchemy.orm import Mapped, mapped_column, relationship
from backend.models.geometry_compat import GeometryColumn
from backend.models.base import Base, BaseModelMixin
from typing import TYPE_CHECKING, List, Optional

if TYPE_CHECKING:
    from backend.models.project import MRVProject
    from backend.models.stratum import ProjectStratum
    from backend.models.field_tree import FieldTree


class SamplePlot(BaseModelMixin, Base):
    """
    Represents a permanent ground sample plot.
    """
    __tablename__ = "sample_plots"

    project_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("mrv_projects.id"), nullable=False)
    stratum_id: Mapped[Optional[uuid.UUID]] = mapped_column(ForeignKey("project_strata.id"), nullable=True)
    plot_code: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    radius_meters: Mapped[float] = mapped_column(Numeric(5, 2), default=12.62, nullable=False)
    
    # Spatial column
    location = mapped_column(GeometryColumn("POINT", srid=4326), nullable=True)
    
    elevation_m: Mapped[Optional[float]] = mapped_column(Numeric(6, 2), nullable=True)
    slope_deg: Mapped[Optional[float]] = mapped_column(Numeric(5, 2), nullable=True)
    aspect_deg: Mapped[Optional[float]] = mapped_column(Numeric(5, 2), nullable=True)

    project: Mapped["MRVProject"] = relationship("MRVProject", back_populates="sample_plots")
    stratum: Mapped[Optional["ProjectStratum"]] = relationship("ProjectStratum", back_populates="sample_plots")
    field_trees: Mapped[List["FieldTree"]] = relationship("FieldTree", back_populates="plot", cascade="all, delete-orphan")
