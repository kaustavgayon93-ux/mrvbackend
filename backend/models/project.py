"""
MRV Project model.
"""
import uuid
from datetime import date
from sqlalchemy import String, Text, ForeignKey, Integer, Numeric, Date
from sqlalchemy.orm import Mapped, mapped_column, relationship
from backend.models.geometry_compat import GeometryColumn
from backend.models.base import Base, BaseModelMixin
from typing import TYPE_CHECKING, List, Optional

if TYPE_CHECKING:
    from backend.models.organization import Organization
    from backend.models.stratum import ProjectStratum
    from backend.models.sample_plot import SamplePlot
    from backend.models.carbon_assessment import CarbonAssessment


class MRVProject(BaseModelMixin, Base):
    """
    Represents an MRV project.
    """
    __tablename__ = "mrv_projects"

    org_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("organizations.id"), nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    methodology: Mapped[str] = mapped_column(String(50), default="VERRA_VM0047", nullable=False)
    status: Mapped[str] = mapped_column(String(50), default="DRAFT", nullable=False)
    start_date: Mapped[date] = mapped_column(Date, nullable=False)
    crediting_period_years: Mapped[int] = mapped_column(Integer, default=30, nullable=False)
    
    # Spatial column
    boundary = mapped_column(GeometryColumn("MULTIPOLYGON", srid=4326), nullable=True)
    
    total_area_ha: Mapped[Optional[float]] = mapped_column(Numeric(12, 2), nullable=True)

    organization: Mapped["Organization"] = relationship("Organization", back_populates="projects")
    strata: Mapped[List["ProjectStratum"]] = relationship("ProjectStratum", back_populates="project", cascade="all, delete-orphan")
    sample_plots: Mapped[List["SamplePlot"]] = relationship("SamplePlot", back_populates="project", cascade="all, delete-orphan")
    carbon_assessments: Mapped[List["CarbonAssessment"]] = relationship("CarbonAssessment", back_populates="project", cascade="all, delete-orphan")
