import json
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, text
from backend.database import get_db_session
from backend.models import MRVProject, ProjectStratum, Organization
from backend.schemas.project import ProjectCreate, ProjectUpdate, ProjectResponse, ProjectListResponse
from backend.schemas.organization import OrganizationCreate, OrganizationResponse
from backend.schemas.common import PaginatedResponse
from backend.api.auth import get_current_user
from backend.models import User
from backend.services.audit_service import AuditService
from backend.config import get_settings

router = APIRouter(prefix="/api/v1/projects", tags=["projects"])

@router.post("/organizations", response_model=OrganizationResponse)
async def create_organization(org: OrganizationCreate, db: AsyncSession = Depends(get_db_session), current_user: User = Depends(get_current_user)):
    """Create a new organization."""
    new_org = Organization(
        name=org.name,
        country_code=org.country_code,
        contact_email=str(org.contact_email) if org.contact_email else None
    )
    db.add(new_org)
    await db.commit()
    await db.refresh(new_org)
    return new_org

@router.get("/organizations", response_model=list[OrganizationResponse])
async def list_organizations(db: AsyncSession = Depends(get_db_session), current_user: User = Depends(get_current_user)):
    """List all organizations."""
    result = await db.execute(select(Organization))
    return result.scalars().all()

@router.post("/", response_model=ProjectResponse)
async def create_project(project: ProjectCreate, db: AsyncSession = Depends(get_db_session), current_user: User = Depends(get_current_user)):
    """Create a new project."""
    settings = get_settings()
    boundary_json = json.dumps(project.boundary)
    
    total_area_ha = 100.0  # Default estimate
    boundary_val = boundary_json
    
    if not settings.is_sqlite:
        try:
            area_query = text("SELECT ST_Area(ST_GeomFromGeoJSON(:geom)::geography) / 10000.0")
            area_result = await db.execute(area_query, {"geom": boundary_json})
            total_area_ha = float(area_result.scalar_one())
            boundary_val = func.ST_GeomFromGeoJSON(boundary_json)
        except Exception:
            pass

    new_project = MRVProject(
        org_id=project.org_id,
        name=project.name,
        description=project.description,
        methodology=project.methodology,
        start_date=project.start_date,
        crediting_period_years=project.crediting_period_years,
        boundary=boundary_val,
        total_area_ha=total_area_ha
    )
    db.add(new_project)
    await db.commit()
    await db.refresh(new_project)
    
    try:
        await AuditService.record(db, new_project.id, current_user.id, "PROJECT_CREATED", {"name": project.name, "area": total_area_ha})
    except Exception:
        pass
        
    return new_project

@router.get("/", response_model=PaginatedResponse[ProjectListResponse])
async def list_projects(page: int = 1, page_size: int = 20, db: AsyncSession = Depends(get_db_session), current_user: User = Depends(get_current_user)):
    """List all projects."""
    offset = (page - 1) * page_size
    
    count_query = select(func.count()).select_from(MRVProject)
    total = (await db.execute(count_query)).scalar_one()
    
    query = select(MRVProject).offset(offset).limit(page_size)
    result = await db.execute(query)
    items = result.scalars().all()
    
    return PaginatedResponse(items=items, total=total, page=page, page_size=page_size)

@router.get("/{project_id}", response_model=ProjectResponse)
async def get_project(project_id: UUID, db: AsyncSession = Depends(get_db_session), current_user: User = Depends(get_current_user)):
    """Get project details."""
    result = await db.execute(select(MRVProject).where(MRVProject.id == project_id))
    project = result.scalar_one_or_none()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return project

@router.patch("/{project_id}", response_model=ProjectResponse)
async def update_project(project_id: UUID, project_update: ProjectUpdate, db: AsyncSession = Depends(get_db_session), current_user: User = Depends(get_current_user)):
    """Update project."""
    result = await db.execute(select(MRVProject).where(MRVProject.id == project_id))
    project = result.scalar_one_or_none()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
        
    for key, value in project_update.model_dump(exclude_unset=True).items():
        setattr(project, key, value)
        
    await db.commit()
    await db.refresh(project)
    await AuditService.record(db, project.id, current_user.id, "PROJECT_UPDATED", project_update.model_dump(exclude_unset=True))
    return project

@router.delete("/{project_id}")
async def delete_project(project_id: UUID, db: AsyncSession = Depends(get_db_session), current_user: User = Depends(get_current_user)):
    """Soft delete / archive project."""
    result = await db.execute(select(MRVProject).where(MRVProject.id == project_id))
    project = result.scalar_one_or_none()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
        
    project.status = "ARCHIVED"
    await db.commit()
    await AuditService.record(db, project.id, current_user.id, "PROJECT_ARCHIVED", {})
    return {"message": "Project archived successfully"}

@router.get("/{project_id}/strata")
async def list_strata(project_id: UUID, db: AsyncSession = Depends(get_db_session), current_user: User = Depends(get_current_user)):
    """List strata for project."""
    query = select(ProjectStratum).where(ProjectStratum.project_id == project_id)
    result = await db.execute(query)
    return result.scalars().all()

@router.post("/{project_id}/strata")
async def add_stratum(project_id: UUID, db: AsyncSession = Depends(get_db_session), current_user: User = Depends(get_current_user)):
    """Add stratum to project."""
    pass
