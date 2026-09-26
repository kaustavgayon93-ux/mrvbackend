from datetime import datetime, date
from uuid import UUID
from typing import Optional, List
from pydantic import BaseModel

class CarbonAssessmentCreate(BaseModel):
    project_id: UUID
    epoch_name: str
    start_date: date
    end_date: date

class CarbonAssessmentResponse(BaseModel):
    id: UUID
    project_id: UUID
    epoch_name: str
    start_date: date
    end_date: date
    status: str
    total_area_ha: Optional[float]
    total_carbon_stock_tco2e: Optional[float]
    buffer_pool_contribution_tco2e: Optional[float]
    net_tradable_credits: Optional[float]
    created_at: datetime
    updated_at: datetime
    
    model_config = {"from_attributes": True}

class CarbonSummary(BaseModel):
    total_area_ha: float
    total_plots: int
    total_trees: int
    mean_agbd_mg_ha: float
    total_carbon_stock_tco2e: float
    net_removals_tco2e: float
    net_credits: float
    uncertainty_percent: float

class TreeCarbonDetail(BaseModel):
    id: UUID
    tag_number: str
    species_scientific: Optional[str]
    dbh_cm: float
    height_m: Optional[float]
    wood_density_g_cm3: float
    agb_kg: float
    bgb_kg: float
    carbon_kg: float
    tco2e: float
    
    model_config = {"from_attributes": True}
