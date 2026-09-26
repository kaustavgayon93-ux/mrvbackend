"""
Satellite Scene model.
"""
from datetime import datetime
from sqlalchemy import String, Numeric, Text, JSON, Index, DateTime
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func
from backend.models.geometry_compat import GeometryColumn
from backend.models.base import Base, BaseModelMixin
from typing import Any, Dict, Optional


class SatelliteScene(BaseModelMixin, Base):
    """
    Represents a satellite scene catalog entry.
    """
    __tablename__ = "satellite_scenes"

    scene_id: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    sensor: Mapped[str] = mapped_column(String(50), nullable=False)
    acquisition_date: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    cloud_cover_percent: Mapped[Optional[float]] = mapped_column(Numeric(5, 2), nullable=True)
    processing_level: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    cog_storage_path: Mapped[str] = mapped_column(Text, nullable=False)
    file_size_mb: Mapped[Optional[float]] = mapped_column(Numeric(10, 2), nullable=True)
    
    # Spatial column
    footprint = mapped_column(GeometryColumn("POLYGON", srid=4326), nullable=True)
    
    metadata_json: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON, nullable=True)
    ingested_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    
    __table_args__ = (
        Index("idx_satellite_scenes_acquisition_date", "acquisition_date"),
    )
