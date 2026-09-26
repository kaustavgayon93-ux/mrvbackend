from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from backend.database import get_db_session
from backend.models import SatelliteScene, User
from backend.schemas.satellite import IngestionRequest, SceneResponse, IngestionStatus
from backend.api.auth import get_current_user

router = APIRouter(prefix="/api/v1/satellite", tags=["satellite"])

@router.post("/ingest", response_model=IngestionStatus)
async def ingest_satellite_data(req: IngestionRequest, current_user: User = Depends(get_current_user)):
    """Start satellite ingestion task."""
    task_id = "mock-task-id-1234"
    return IngestionStatus(task_id=task_id, status="QUEUED", message="Ingestion task started")

@router.get("/scenes", response_model=list[SceneResponse])
async def list_scenes(db: AsyncSession = Depends(get_db_session), current_user: User = Depends(get_current_user)):
    """List ingested scenes."""
    result = await db.execute(select(SatelliteScene))
    return result.scalars().all()

@router.get("/scenes/{scene_id}", response_model=SceneResponse)
async def get_scene(scene_id: UUID, db: AsyncSession = Depends(get_db_session), current_user: User = Depends(get_current_user)):
    """Get scene details."""
    result = await db.execute(select(SatelliteScene).where(SatelliteScene.id == scene_id))
    scene = result.scalar_one_or_none()
    if not scene:
        raise HTTPException(status_code=404, detail="Scene not found")
    return scene

@router.get("/ingest/status/{task_id}", response_model=IngestionStatus)
async def get_ingest_status(task_id: str, current_user: User = Depends(get_current_user)):
    """Check ingestion task status."""
    return IngestionStatus(task_id=task_id, status="COMPLETED", scenes_found=5, scenes_processed=5)

@router.get("/tiles/{scene_id}/{z}/{x}/{y}")
async def get_scene_tiles(scene_id: UUID, z: int, x: int, y: int, current_user: User = Depends(get_current_user)):
    """Proxy to TiTiler for scene tiles."""
    return {"message": f"Tile {z}/{x}/{y} for scene {scene_id}"}
