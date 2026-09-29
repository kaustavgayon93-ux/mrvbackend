from datetime import datetime
from uuid import UUID
from typing import Optional, List, Union
from pydantic import BaseModel

class PlotCreate(BaseModel):
    project_id: UUID
    stratum_id: Optional[UUID] = None
    plot_code: str
    radius_meters: float = 12.62
    latitude: float
    longitude: float
    elevation_m: Optional[float] = None
    slope_deg: Optional[float] = None
    aspect_deg: Optional[float] = None

class PlotResponse(BaseModel):
    id: UUID
    project_id: UUID
    stratum_id: Optional[UUID] = None
    plot_code: str
    radius_meters: float
    elevation_m: Optional[float] = None
    slope_deg: Optional[float] = None
    aspect_deg: Optional[float] = None
    created_at: datetime

    model_config = {"from_attributes": True}

class TreeCreate(BaseModel):
    plot_id: Optional[UUID] = None
    tag_number: str
    species_common: Optional[str] = None
    species_scientific: Optional[str] = None
    dbh_cm: float
    height_m: Optional[float] = None
    wood_density_g_cm3: float = 0.58
    is_conifer: bool = False
    photo_url: Optional[str] = None
    photo_azimuth_deg: Optional[float] = None
    measured_at: Optional[datetime] = None
    surveyor_id: Union[UUID, str]
    health_status: str = "HEALTHY"

class TreeResponse(BaseModel):
    id: UUID
    plot_id: UUID
    tag_number: str
    species_common: Optional[str] = None
    species_scientific: Optional[str] = None
    dbh_cm: float
    height_m: Optional[float] = None
    wood_density_g_cm3: float
    is_conifer: bool = False
    photo_url: Optional[str] = None
    photo_azimuth_deg: Optional[float] = None
    measured_at: datetime
    surveyor_id: Union[UUID, str]
    health_status: str
    agb_kg: Optional[float] = None
    bgb_kg: Optional[float]
    carbon_kg: Optional[float]
    tco2e: Optional[float]
    created_at: datetime

    model_config = {"from_attributes": True}

class PlotCarbonSummary(BaseModel):
    plot_id: UUID
    total_trees: int
    mean_dbh_cm: float
    total_agb_kg: float
    total_bgb_kg: float
    total_carbon_kg: float
    total_tco2e: float

class FieldSubmission(BaseModel):
    plot: PlotCreate
    trees: List[TreeCreate]

class FieldSubmissionResponse(BaseModel):
    plot: PlotResponse
    trees: List[TreeResponse]
    summary: PlotCarbonSummary
