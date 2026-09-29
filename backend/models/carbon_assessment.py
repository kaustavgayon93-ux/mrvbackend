"""
Carbon Assessment model.
"""
import uuid
from datetime import date
from sqlalchemy import String, ForeignKey, Numeric, Integer, Date, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from backend.models.base import Base, BaseModelMixin
from typing import TYPE_CHECKING, Optional

if TYPE_CHECKING:
    from backend.models.project import MRVProject


class CarbonAssessment(BaseModelMixin, Base):
    """
    Represents a carbon stock assessment for a project.
    """
    __tablename__ = "carbon_assessments"

    project_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("mrv_projects.id"), nullable=False)
    epoch_name: Mapped[str] = mapped_column(String(100), nullable=False)
    start_date: Mapped[date] = mapped_column(Date, nullable=False)
    end_date: Mapped[date] = mapped_column(Date, nullable=False)
    
    mean_agbd_mg_ha: Mapped[float] = mapped_column(Numeric(8, 2), nullable=False)
    total_carbon_stock_tco2e: Mapped[float] = mapped_column(Numeric(12, 2), nullable=False)
    baseline_carbon_stock_tco2e: Mapped[float] = mapped_column(Numeric(12, 2), nullable=False)
    gross_removals_tco2e: Mapped[float] = mapped_column(Numeric(12, 2), nullable=False)
    
    uncertainty_percent: Mapped[float] = mapped_column(Numeric(5, 2), default=0, nullable=False)
    uncertainty_deduction_tco2e: Mapped[float] = mapped_column(Numeric(12, 2), default=0, nullable=False)
    buffer_pool_percent: Mapped[float] = mapped_column(Numeric(5, 2), default=15, nullable=False)
    buffer_pool_contribution_tco2e: Mapped[float] = mapped_column(Numeric(12, 2), nullable=False)
    
    net_credits_issued: Mapped[int] = mapped_column(Integer, nullable=False)
    
    assessment_status: Mapped[str] = mapped_column(String(50), default="PENDING_AUDIT", nullable=False)
    verified_by: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    verification_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    report_pdf_url: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    project: Mapped["MRVProject"] = relationship("MRVProject", back_populates="carbon_assessments")

    @property
    def status(self) -> str:
        return self.assessment_status

    @status.setter
    def status(self, val: str):
        self.assessment_status = val

    @property
    def net_tradable_credits(self) -> float:
        return float(self.net_credits_issued)
