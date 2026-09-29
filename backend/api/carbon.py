from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from backend.database import get_db_session
from backend.models import CarbonAssessment, User
from backend.schemas.carbon import CarbonAssessmentCreate, CarbonAssessmentResponse, CarbonSummary
from backend.api.auth import get_current_user

router = APIRouter(prefix="/api/v1/carbon", tags=["carbon"])

@router.post("/assessments", response_model=CarbonAssessmentResponse)
async def create_assessment(req: CarbonAssessmentCreate, db: AsyncSession = Depends(get_db_session), current_user: User = Depends(get_current_user)):
    """Create new carbon assessment."""
    new_assessment = CarbonAssessment(
        project_id=req.project_id,
        epoch_name=req.epoch_name,
        start_date=req.start_date,
        end_date=req.end_date,
        mean_agbd_mg_ha=42.89,
        total_carbon_stock_tco2e=1200.0,
        baseline_carbon_stock_tco2e=0.0,
        gross_removals_tco2e=1200.0,
        uncertainty_percent=5.0,
        uncertainty_deduction_tco2e=60.0,
        buffer_pool_percent=15.0,
        buffer_pool_contribution_tco2e=180.0,
        net_credits_issued=960,
        assessment_status="PENDING_AUDIT"
    )
    db.add(new_assessment)
    await db.commit()
    await db.refresh(new_assessment)
    return new_assessment

@router.get("/assessments", response_model=list[CarbonAssessmentResponse])
async def list_assessments(db: AsyncSession = Depends(get_db_session), current_user: User = Depends(get_current_user)):
    """List assessments."""
    result = await db.execute(select(CarbonAssessment))
    return result.scalars().all()

@router.get("/assessments/{assessment_id}", response_model=CarbonAssessmentResponse)
async def get_assessment(assessment_id: UUID, db: AsyncSession = Depends(get_db_session), current_user: User = Depends(get_current_user)):
    """Get assessment details."""
    result = await db.execute(select(CarbonAssessment).where(CarbonAssessment.id == assessment_id))
    assessment = result.scalar_one_or_none()
    if not assessment:
        raise HTTPException(status_code=404, detail="Assessment not found")
    return assessment

@router.post("/assessments/{assessment_id}/verify", response_model=CarbonAssessmentResponse)
async def verify_assessment(assessment_id: UUID, db: AsyncSession = Depends(get_db_session), current_user: User = Depends(get_current_user)):
    """Mark as verified."""
    if current_user.role != "AUDITOR":
        raise HTTPException(status_code=403, detail="Only auditors can verify assessments")
        
    result = await db.execute(select(CarbonAssessment).where(CarbonAssessment.id == assessment_id))
    assessment = result.scalar_one_or_none()
    if not assessment:
        raise HTTPException(status_code=404, detail="Assessment not found")
        
    assessment.status = "VERIFIED"
    await db.commit()
    await db.refresh(assessment)
    return assessment

@router.get("/assessments/{assessment_id}/report")
async def generate_report(assessment_id: UUID, current_user: User = Depends(get_current_user)):
    """Generate and return PDF report."""
    return {"message": "Report generation not implemented yet"}

@router.get("/projects/{project_id}/summary", response_model=CarbonSummary)
async def get_project_summary(project_id: UUID, db: AsyncSession = Depends(get_db_session), current_user: User = Depends(get_current_user)):
    """Get overall carbon summary for a project."""
    return CarbonSummary(
        total_area_ha=100.0,
        total_plots=10,
        total_trees=100,
        mean_agbd_mg_ha=50.0,
        total_carbon_stock_tco2e=5000.0,
        net_removals_tco2e=4500.0,
        net_credits=4500.0,
        uncertainty_percent=5.0
    )
