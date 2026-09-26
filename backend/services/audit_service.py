import json
import hashlib
import logging
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)

class AuditService:
    """
    Cryptographic Audit Service for maintaining an immutable ledger of actions.
    """

    @staticmethod
    def compute_payload_hash(payload: Dict[str, Any]) -> str:
        """
        Compute SHA-256 hash of canonical JSON payload.
        """
        canonical_json = json.dumps(payload, sort_keys=True, separators=(',', ':'))
        return hashlib.sha256(canonical_json.encode('utf-8')).hexdigest()

    @staticmethod
    def compute_ledger_hash(payload_hash: str, previous_hash: str) -> str:
        """
        Compute SHA-256 hash of concatenated payload_hash and previous_hash.
        """
        concatenated = previous_hash + payload_hash
        return hashlib.sha256(concatenated.encode('utf-8')).hexdigest()

    @staticmethod
    async def record_action(db_session, project_id: int, entity_type: str, entity_id: int, action_type: str, payload: Dict[str, Any], actor_id: Optional[int] = None, details: Optional[str] = None) -> Any:
        """
        Record a new action in the cryptographic audit ledger.
        
        Args:
            db_session: Async SQLAlchemy session.
            project_id: ID of the project.
            entity_type: Type of entity modified.
            entity_id: ID of the entity.
            action_type: Type of action (e.g., 'CREATE', 'UPDATE').
            payload: The action payload.
            actor_id: ID of the user performing the action.
            details: Optional details about the action.
            
        Returns:
            The created AuditLedger record.
        """
        try:
            # Note: This implies the existence of an AuditLedger model
            from backend.models.audit import AuditLedger
            from sqlalchemy import select
            
            # Get the last ledger entry's current_ledger_hash
            stmt = select(AuditLedger).where(AuditLedger.project_id == project_id).order_by(AuditLedger.id.desc()).limit(1)
            result = await db_session.execute(stmt)
            last_entry = result.scalar_one_or_none()
            
            previous_hash = last_entry.current_ledger_hash if last_entry else '0' * 64
            
            payload_hash = AuditService.compute_payload_hash(payload)
            current_ledger_hash = AuditService.compute_ledger_hash(payload_hash, previous_hash)
            
            new_entry = AuditLedger(
                project_id=project_id,
                entity_type=entity_type,
                entity_id=entity_id,
                action_type=action_type,
                payload=payload,
                actor_id=actor_id,
                details=details,
                previous_hash=previous_hash,
                payload_hash=payload_hash,
                current_ledger_hash=current_ledger_hash
            )
            
            db_session.add(new_entry)
            await db_session.flush()
            
            return new_entry
        except Exception as e:
            logger.error(f"Failed to record audit action: {str(e)}")
            raise

    @staticmethod
    async def verify_chain_integrity(db_session, project_id: int) -> Dict[str, Any]:
        """
        Walk the entire chain and verify each hash links correctly.
        """
        try:
            from backend.models.audit import AuditLedger
            from sqlalchemy import select
            
            stmt = select(AuditLedger).where(AuditLedger.project_id == project_id).order_by(AuditLedger.id.asc())
            result = await db_session.execute(stmt)
            entries = result.scalars().all()
            
            if not entries:
                return {"valid": True, "total_entries": 0, "broken_at": None}
                
            expected_prev_hash = '0' * 64
            
            for entry in entries:
                if entry.previous_hash != expected_prev_hash:
                    return {"valid": False, "total_entries": len(entries), "broken_at": entry.id}
                    
                computed_payload_hash = AuditService.compute_payload_hash(entry.payload)
                if computed_payload_hash != entry.payload_hash:
                    return {"valid": False, "total_entries": len(entries), "broken_at": entry.id}
                    
                computed_ledger_hash = AuditService.compute_ledger_hash(computed_payload_hash, entry.previous_hash)
                if computed_ledger_hash != entry.current_ledger_hash:
                    return {"valid": False, "total_entries": len(entries), "broken_at": entry.id}
                    
                expected_prev_hash = entry.current_ledger_hash
                
            return {"valid": True, "total_entries": len(entries), "broken_at": None}
            
        except Exception as e:
            logger.error(f"Failed to verify chain integrity: {str(e)}")
            raise
