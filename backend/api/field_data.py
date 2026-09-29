from datetime import datetime, timezone
from uuid import UUID
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from backend.database import get_db_session
from backend.models import SamplePlot, FieldTree, User
from backend.schemas.field_data import PlotCreate, PlotResponse, TreeCreate, TreeResponse, FieldSubmission, FieldSubmissionResponse, PlotCarbonSummary
from backend.api.auth import get_current_user
from backend.services.carbon_calculator import CarbonCalculator

router = APIRouter(prefix="/api/v1/field", tags=["field_data"])

@router.post("/plots", response_model=PlotResponse)
async def create_plot(plot: PlotCreate, db: AsyncSession = Depends(get_db_session), current_user: User = Depends(get_current_user)):
    """Create sample plot."""
    location = f"SRID=4326;POINT({plot.longitude} {plot.latitude})"
    new_plot = SamplePlot(
        project_id=plot.project_id,
        stratum_id=plot.stratum_id,
        plot_code=plot.plot_code,
        radius_meters=plot.radius_meters,
        location=location,
        elevation_m=plot.elevation_m,
        slope_deg=plot.slope_deg,
        aspect_deg=plot.aspect_deg
    )
    db.add(new_plot)
    await db.commit()
    await db.refresh(new_plot)
    return new_plot

@router.get("/plots", response_model=List[PlotResponse])
async def list_plots(project_id: Optional[UUID] = None, db: AsyncSession = Depends(get_db_session), current_user: User = Depends(get_current_user)):
    """List plots."""
    query = select(SamplePlot)
    if project_id:
        query = query.where(SamplePlot.project_id == project_id)
    result = await db.execute(query)
    return result.scalars().all()

@router.get("/plots/{plot_id}", response_model=PlotResponse)
async def get_plot(plot_id: UUID, db: AsyncSession = Depends(get_db_session), current_user: User = Depends(get_current_user)):
    """Get plot."""
    result = await db.execute(select(SamplePlot).where(SamplePlot.id == plot_id))
    plot = result.scalar_one_or_none()
    if not plot:
        raise HTTPException(status_code=404, detail="Plot not found")
    return plot

@router.post("/plots/{plot_id}/trees", response_model=TreeResponse)
async def add_tree(plot_id: UUID, tree: TreeCreate, db: AsyncSession = Depends(get_db_session), current_user: User = Depends(get_current_user)):
    """Add tree measurement."""
    carbon_data = CarbonCalculator.compute_tree_biomass(
        dbh_cm=tree.dbh_cm,
        height_m=tree.height_m or 10.0,
        wood_density=tree.wood_density_g_cm3,
        is_conifer=tree.is_conifer
    )
    
    measured_at = tree.measured_at or datetime.now(timezone.utc)
    new_tree = FieldTree(
        plot_id=plot_id,
        tag_number=tree.tag_number,
        species_common=tree.species_common,
        species_scientific=tree.species_scientific or "Unknown",
        dbh_cm=tree.dbh_cm,
        height_m=tree.height_m,
        wood_density_g_cm3=tree.wood_density_g_cm3,
        is_conifer=tree.is_conifer,
        photo_url=tree.photo_url,
        photo_azimuth_deg=tree.photo_azimuth_deg,
        measured_at=measured_at,
        surveyor_id=str(tree.surveyor_id),
        health_status=tree.health_status,
        calculated_agb_kg=carbon_data["agb_kg"],
        calculated_bgb_kg=carbon_data["bgb_kg"],
        calculated_carbon_kg=carbon_data["carbon_kg"],
        calculated_tco2e=carbon_data["tco2e"]
    )
    db.add(new_tree)
    await db.commit()
    await db.refresh(new_tree)
    return new_tree

@router.post("/submissions", response_model=FieldSubmissionResponse)
async def submit_field_data(submission: FieldSubmission, db: AsyncSession = Depends(get_db_session), current_user: User = Depends(get_current_user)):
    """Bulk submit plot + trees."""
    plot = await create_plot(submission.plot, db, current_user)
    trees = []
    total_agb, total_bgb, total_c, total_tco2e = 0, 0, 0, 0
    for tree_req in submission.trees:
        tree_req.plot_id = plot.id
        tree = await add_tree(plot.id, tree_req, db, current_user)
        trees.append(tree)
        total_agb += (tree.agb_kg or 0)
        total_bgb += (tree.bgb_kg or 0)
        total_c += (tree.carbon_kg or 0)
        total_tco2e += (tree.tco2e or 0)
        
    summary = PlotCarbonSummary(
        plot_id=plot.id,
        total_trees=len(trees),
        mean_dbh_cm=sum(t.dbh_cm for t in trees) / len(trees) if trees else 0,
        total_agb_kg=total_agb,
        total_bgb_kg=total_bgb,
        total_carbon_kg=total_c,
        total_tco2e=total_tco2e
    )
    return FieldSubmissionResponse(plot=plot, trees=trees, summary=summary)

@router.get("/plots/{plot_id}/carbon-summary", response_model=PlotCarbonSummary)
async def get_plot_carbon_summary(plot_id: UUID, db: AsyncSession = Depends(get_db_session), current_user: User = Depends(get_current_user)):
    """Get plot-level carbon summary."""
    result = await db.execute(select(FieldTree).where(FieldTree.plot_id == plot_id))
    trees = result.scalars().all()
    
    total_agb = sum((t.agb_kg or 0) for t in trees)
    total_bgb = sum((t.bgb_kg or 0) for t in trees)
    total_c = sum((t.carbon_kg or 0) for t in trees)
    total_tco2e = sum((t.tco2e or 0) for t in trees)
    
    return PlotCarbonSummary(
        plot_id=plot_id,
        total_trees=len(trees),
        mean_dbh_cm=sum(t.dbh_cm for t in trees) / len(trees) if trees else 0,
        total_agb_kg=total_agb,
        total_bgb_kg=total_bgb,
        total_carbon_kg=total_c,
        total_tco2e=total_tco2e
    )
