"""
Project Stratum model.
"""
import uuid
from sqlalchemy import String, ForeignKey, Numeric
from sqlalchemy.orm import Mapped, mapped_column, relationship
from backend.models.geometry_compat import GeometryColumn
from backend.models.base import Base, BaseModelMixin
from typing import TYPE_CHECKING, List, Optional

if TYPE_CHECKING:
    from backend.models.project import MRVProject
    from backend.models.sample_plot import SamplePlot


class ProjectStratum(BaseModelMixin, Base):
    """
    Represents a stratum within an MRV project.
    """
    __tablename__ = "project_strata"

    project_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("mrv_projects.id"), nullable=False)
    stratum_name: Mapped[str] = mapped_column(String(100), nullable=False)
    forest_type: Mapped[str] = mapped_column(String(100), nullable=False)
    age_class: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    
    # Spatial column
    geom = mapped_column(GeometryColumn("MULTIPOLYGON", srid=4326), nullable=True)
    
    area_ha: Mapped[Optional[float]] = mapped_column(Numeric(10, 2), nullable=True)

    project: Mapped["MRVProject"] = relationship("MRVProject", back_populates="strata")
    sample_plots: Mapped[List["SamplePlot"]] = relationship("SamplePlot", back_populates="stratum")
