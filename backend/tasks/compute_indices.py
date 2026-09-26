import os
import logging
import tempfile
from typing import Dict, Any, List
from backend.tasks.celery_app import celery_app

# Mock imports
try:
    from backend.services.minio_client import MinIOStorageClient
    from backend.analysis.spectral_indices import SpectralIndexCalculator
except ImportError:
    MinIOStorageClient = Any
    SpectralIndexCalculator = Any

logger = logging.getLogger(__name__)

@celery_app.task(bind=True, name='mrv.compute_indices', max_retries=3)
def compute_spectral_indices(self, scene_id: str, project_id: str, indices: List[str] = None) -> Dict[str, Any]:
    """
    Compute requested spectral indices for a given scene.
    """
    if indices is None:
        indices = ['NDVI', 'EVI', 'NDRE', 'NBR', 'NDWI']
        
    logger.info(f"Computing indices {indices} for scene {scene_id}")
    
    try:
        minio_client = MinIOStorageClient()
        calculator = SpectralIndexCalculator()
        index_paths = {}
        
        self.update_state(state='PROGRESS', meta={'status': 'Downloading scene', 'scene_id': scene_id})
        
        with tempfile.TemporaryDirectory() as temp_dir:
            # Step 1: Download scene COG from MinIO
            scene_path = os.path.join(temp_dir, f"{scene_id}.tif")
            minio_client.download_file(f"scenes/{scene_id}.tif", scene_path)
            
            # Note: Step 2 & 3: Loading raster bands and computing handled by SpectralIndexCalculator
            total_indices = len(indices)
            
            for i, index_name in enumerate(indices):
                self.update_state(state='PROGRESS', meta={'current': i+1, 'total': total_indices, 'status': f'Computing {index_name}'})
                
                # Step 4: Save each index as a separate COG
                output_path = os.path.join(temp_dir, f"{scene_id}_{index_name}.tif")
                calculator.compute(scene_path, index_name, output_path)
                
                # Step 5: Upload index COGs to MinIO
                s3_uri = minio_client.upload_file(output_path, f"indices/{scene_id}/{index_name}.tif")
                index_paths[index_name] = s3_uri
                
        # Step 6: Return dict with index_paths
        return {
            "index_paths": index_paths
        }
        
    except Exception as exc:
        logger.error(f"Compute indices task failed: {str(exc)}")
        raise self.retry(exc=exc, countdown=60)
