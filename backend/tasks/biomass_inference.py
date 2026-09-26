import os
import logging
import tempfile
from typing import Dict, Any, List, Optional
from backend.tasks.celery_app import celery_app

# Mock imports
try:
    from backend.analysis.biomass_estimator import BiomassEstimator
    from backend.analysis.zonal_stats import ZonalStatsCalculator
    from backend.services.minio_client import MinIOStorageClient
except ImportError:
    BiomassEstimator = Any
    ZonalStatsCalculator = Any
    MinIOStorageClient = Any

logger = logging.getLogger(__name__)

@celery_app.task(bind=True, name='mrv.biomass_inference', max_retries=2)
def run_biomass_inference(self, project_id: str, scene_ids: List[str], model_path: Optional[str] = None) -> Dict[str, Any]:
    """
    Run LightGBM biomass model inference.
    """
    logger.info(f"Running biomass inference for project {project_id}")
    
    try:
        minio_client = MinIOStorageClient()
        
        # Step 1: Load pre-trained LightGBM model
        estimator = BiomassEstimator(model_path=model_path)
        stats_calc = ZonalStatsCalculator()
        
        self.update_state(state='PROGRESS', meta={'status': 'Loading model and preparing features'})
        
        epoch = "latest"  
        
        with tempfile.TemporaryDirectory() as temp_dir:
            # Step 2 & 3: Download features and prepare feature stack
            feature_stack_path = os.path.join(temp_dir, "features.tif")
            estimator.prepare_features(scene_ids, feature_stack_path)
            
            self.update_state(state='PROGRESS', meta={'status': 'Running predictions'})
            
            # Step 4 & 5: Run quantile prediction and generate biomass map COG
            biomass_cog_path = os.path.join(temp_dir, "biomass.tif")
            estimator.predict(feature_stack_path, biomass_cog_path, quantiles=True)
            
            # Step 6: Upload to MinIO
            s3_uri = minio_client.upload_file(biomass_cog_path, f"biomass/{project_id}/{epoch}/biomass.tif")
            
            self.update_state(state='PROGRESS', meta={'status': 'Computing zonal statistics'})
            
            # Step 7: Compute zonal statistics for project boundary
            stats = stats_calc.compute_stats(biomass_cog_path, project_id)
            
            # Step 8: Return results
            return {
                "biomass_cog_path": s3_uri,
                "mean_agbd_mg_ha": stats.get('mean', 0.0),
                "total_tco2e": stats.get('total_tco2e', 0.0),
                "uncertainty_percent": stats.get('uncertainty', 0.0)
            }
            
    except Exception as exc:
        logger.error(f"Biomass inference failed: {str(exc)}")
        raise self.retry(exc=exc, countdown=120)
