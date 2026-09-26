from datetime import datetime, date
from uuid import UUID
from typing import Optional, Dict, Any
from pydantic import BaseModel
from .common import GeoJSONMultiPolygon

class ProjectCreate(BaseModel):
    org_id: UUID
    name: str
    description: str
    methodology: str = "VERRA_VM0047"
    start_date: date
    crediting_period_years: int = 30
    boundary: Dict[str, Any]

class ProjectUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    status: Optional[str] = None

class ProjectResponse(BaseModel):
    id: UUID
    org_id: UUID
    name: str
    description: str
    methodology: str
    status: str
    start_date: date
    crediting_period_years: int
    total_area_ha: Optional[float]
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}

class ProjectListResponse(BaseModel):
    id: UUID
    name: str
    status: str
    methodology: str
    total_area_ha: Optional[float]
    created_at: datetime

    model_config = {"from_attributes": True}
