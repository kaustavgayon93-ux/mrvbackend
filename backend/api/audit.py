from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from backend.database import get_db_session
from backend.models import AuditLedger, User
from backend.api.auth import get_current_user
from backend.services.audit_service import AuditService

router = APIRouter(prefix="/api/v1/audit", tags=["audit"])

@router.get("/ledger/{project_id}")
async def get_audit_ledger(project_id: UUID, db: AsyncSession = Depends(get_db_session), current_user: User = Depends(get_current_user)):
    """Get audit trail for a project."""
    result = await db.execute(select(AuditLedger).where(AuditLedger.project_id == project_id).order_by(AuditLedger.recorded_at.desc()))
    return result.scalars().all()

@router.get("/ledger/{project_id}/verify")
async def verify_ledger(project_id: UUID, db: AsyncSession = Depends(get_db_session), current_user: User = Depends(get_current_user)):
    """Verify chain integrity."""
    result = await AuditService.verify_chain_integrity(db, project_id)
    return {"project_id": project_id, "is_valid": result.get("valid", True), "details": result}

@router.get("/ledger/{project_id}/export")
async def export_ledger(project_id: UUID, db: AsyncSession = Depends(get_db_session), current_user: User = Depends(get_current_user)):
    """Export ledger as JSON."""
    result = await db.execute(select(AuditLedger).where(AuditLedger.project_id == project_id).order_by(AuditLedger.recorded_at.asc()))
    records = result.scalars().all()
    return [{"id": r.id, "action": r.action_type, "hash": r.current_ledger_hash, "previous_hash": r.previous_ledger_hash, "payload_hash": r.payload_sha256, "recorded_at": r.recorded_at.isoformat() if r.recorded_at else None} for r in records]
