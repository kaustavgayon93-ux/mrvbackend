from datetime import datetime, date
from uuid import UUID
from typing import Optional, List
from pydantic import BaseModel

class IngestionRequest(BaseModel):
    bbox: List[float]
    start_date: date
    end_date: date
    sensor: str = "SENTINEL_2"
    max_cloud_cover: float = 15.0

class SceneResponse(BaseModel):
    id: UUID
    scene_id: str
    sensor: str
    acquisition_date: datetime
    cloud_cover_percent: Optional[float]
    processing_level: Optional[str]
    cog_storage_path: Optional[str]
    
    model_config = {"from_attributes": True}

class IngestionStatus(BaseModel):
    task_id: str
    status: str
    scenes_found: Optional[int] = 0
    scenes_processed: Optional[int] = 0
    message: Optional[str] = None
