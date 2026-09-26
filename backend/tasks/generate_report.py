import os
import logging
import hashlib
import tempfile
from typing import Dict, Any
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from backend.tasks.celery_app import celery_app

# Mock imports
try:
    from backend.services.report_generator import ReportGenerator
    from backend.services.minio_client import MinIOStorageClient
    from backend.models import Assessment, AuditLedger
except ImportError:
    ReportGenerator = Any
    MinIOStorageClient = Any
    Assessment = Any
    AuditLedger = Any

logger = logging.getLogger(__name__)

# Synchronous DB setup for Celery
DB_URL = os.environ.get("DATABASE_URL", "postgresql://user:password@localhost/mrv")
if DB_URL.startswith("postgresql+asyncpg://"):
    DB_URL = DB_URL.replace("postgresql+asyncpg://", "postgresql://")

engine = create_engine(DB_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@celery_app.task(bind=True, name='mrv.generate_report', max_retries=3)
def generate_assessment_report(self, assessment_id: str) -> Dict[str, Any]:
    """
    Generate PDF report for a carbon assessment.
    """
    logger.info(f"Generating report for assessment {assessment_id}")
    
    try:
        self.update_state(state='PROGRESS', meta={'status': 'Gathering data'})
        
        with SessionLocal() as db_session:
            # Step 1: Load assessment, project, strata, plots, trees from database
            assessment = db_session.query(Assessment).filter(Assessment.id == assessment_id).first()
            if not assessment:
                raise ValueError(f"Assessment {assessment_id} not found")
                
            project = assessment.project
            
            # Step 2, 3, 4: Compute stats, Generate HTML, Convert to PDF
            self.update_state(state='PROGRESS', meta={'status': 'Generating PDF'})
            
            report_gen = ReportGenerator()
            
            with tempfile.TemporaryDirectory() as temp_dir:
                pdf_path = os.path.join(temp_dir, f"report_{assessment_id}.pdf")
                report_gen.generate_pdf(assessment, project, output_path=pdf_path)
                
                # Calculate SHA-256 of the PDF
                with open(pdf_path, 'rb') as f:
                    file_hash = hashlib.sha256(f.read()).hexdigest()
                
                self.update_state(state='PROGRESS', meta={'status': 'Uploading report'})
                
                # Step 5: Upload PDF to MinIO
                minio_client = MinIOStorageClient()
                pdf_url = minio_client.upload_file(pdf_path, f"reports/{assessment_id}.pdf")
                
                # Step 6: Update assessment record
                assessment.report_pdf_url = pdf_url
                
                # Step 7: Record in audit ledger
                audit = AuditLedger(
                    action="REPORT_GENERATED",
                    entity_type="ASSESSMENT",
                    entity_id=assessment_id,
                    details={"pdf_url": pdf_url, "hash": file_hash}
                )
                db_session.add(audit)
                db_session.commit()
                
            # Return summary dict
            return {
                "pdf_url": pdf_url,
                "report_hash": file_hash
            }
            
    except Exception as exc:
        logger.error(f"Report generation failed: {str(exc)}")
        raise self.retry(exc=exc, countdown=60)
