"""
Field Tree model.
"""
import uuid
from datetime import datetime
from sqlalchemy import String, ForeignKey, Numeric, Boolean, Text, CheckConstraint, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from backend.models.base import Base, BaseModelMixin
from typing import TYPE_CHECKING, Optional

if TYPE_CHECKING:
    from backend.models.sample_plot import SamplePlot


class FieldTree(BaseModelMixin, Base):
    """
    Represents a tree measured in a sample plot.
    """
    __tablename__ = "field_trees"
    __table_args__ = (
        CheckConstraint("dbh_cm > 0", name="chk_dbh_positive"),
        CheckConstraint("height_m > 0", name="chk_height_positive"),
    )

    plot_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("sample_plots.id"), nullable=False)
    tag_number: Mapped[str] = mapped_column(String(50), nullable=False)
    species_common: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    species_scientific: Mapped[str] = mapped_column(String(255), nullable=False)
    dbh_cm: Mapped[float] = mapped_column(Numeric(6, 2), nullable=False)
    height_m: Mapped[Optional[float]] = mapped_column(Numeric(5, 2), nullable=True)
    wood_density_g_cm3: Mapped[float] = mapped_column(Numeric(4, 3), default=0.58, nullable=False)
    is_conifer: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    
    calculated_agb_kg: Mapped[Optional[float]] = mapped_column(Numeric(10, 2), nullable=True)
    calculated_bgb_kg: Mapped[Optional[float]] = mapped_column(Numeric(10, 2), nullable=True)
    calculated_carbon_kg: Mapped[Optional[float]] = mapped_column(Numeric(10, 2), nullable=True)
    calculated_tco2e: Mapped[Optional[float]] = mapped_column(Numeric(10, 4), nullable=True)
    
    photo_url: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    photo_azimuth_deg: Mapped[Optional[float]] = mapped_column(Numeric(5, 2), nullable=True)
    measured_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    surveyor_id: Mapped[str] = mapped_column(String(100), nullable=False)
    health_status: Mapped[str] = mapped_column(String(50), default="HEALTHY", nullable=False)

    plot: Mapped["SamplePlot"] = relationship("SamplePlot", back_populates="field_trees")

    @property
    def agb_kg(self) -> Optional[float]:
        return float(self.calculated_agb_kg) if self.calculated_agb_kg is not None else None

    @property
    def bgb_kg(self) -> Optional[float]:
        return float(self.calculated_bgb_kg) if self.calculated_bgb_kg is not None else None

    @property
    def carbon_kg(self) -> Optional[float]:
        return float(self.calculated_carbon_kg) if self.calculated_carbon_kg is not None else None

    @property
    def tco2e(self) -> Optional[float]:
        return float(self.calculated_tco2e) if self.calculated_tco2e is not None else None
