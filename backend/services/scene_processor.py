import logging
import rasterio
from rasterio.windows import Window
from rasterio.enums import Resampling
import numpy as np
import os
import boto3

logger = logging.getLogger(__name__)

class SceneProcessor:
    """
    Scene Processing Service for Satellite Imagery.
    """

    @staticmethod
    def process_sentinel2(scene_path: str, output_path: str) -> str:
        """
        Read L2A .SAFE or individual band TIFFs, apply cloud masking, 
        compute reflectance scaling, and convert to COG.
        
        Args:
            scene_path: Path to input band TIFF (e.g. B04).
            output_path: Path to output COG.
        """
        # This is a simplified version assuming scene_path points to a specific band
        # and we apply operations on it. A full implementation would need paths to SCL as well.
        try:
            with rasterio.open(scene_path) as src:
                profile = src.profile.copy()
                
                # Update profile for COG
                profile.update({
                    'driver': 'GTiff',
                    'compress': 'deflate',
                    'tiled': True,
                    'blockxsize': 256,
                    'blockysize': 256,
                    'nodata': 0,
                    'dtype': 'float32'
                })
                
                with rasterio.open(output_path, 'w', **profile) as dst:
                    for ji, window in src.block_windows(1):
                        data = src.read(1, window=window)
                        
                        # Assuming data is uint16 scaled by 10000
                        # Scaling
                        float_data = data.astype(np.float32) / 10000.0
                        
                        # In a real scenario, we would also read SCL here for the same window
                        # and mask out cloud pixels.
                        # For example: 
                        # scl_data = scl_src.read(1, window=window)
                        # mask = np.isin(scl_data, [3, 8, 9, 10, 11])
                        # float_data[mask] = 0 # or np.nan
                        
                        dst.write(float_data, 1, window=window)
                        
            logger.info(f"Successfully processed Sentinel-2 scene to {output_path}")
            return output_path
            
        except Exception as e:
            logger.error(f"Failed to process Sentinel-2 scene: {str(e)}")
            raise

    @staticmethod
    def process_landsat(scene_path: str, output_path: str) -> str:
        """
        Process Landsat bands similarly to Sentinel-2.
        """
        try:
            with rasterio.open(scene_path) as src:
                profile = src.profile.copy()
                
                profile.update({
                    'driver': 'GTiff',
                    'compress': 'deflate',
                    'tiled': True,
                    'blockxsize': 256,
                    'blockysize': 256,
                    'nodata': 0,
                    'dtype': 'float32'
                })
                
                with rasterio.open(output_path, 'w', **profile) as dst:
                    for ji, window in src.block_windows(1):
                        data = src.read(1, window=window)
                        
                        # Landsat C2 scaling: reflectance = (data * 0.0000275) - 0.2
                        # Ignoring QA_PIXEL masking in this simplified version
                        float_data = (data.astype(np.float32) * 0.0000275) - 0.2
                        
                        dst.write(float_data, 1, window=window)
                        
            logger.info(f"Successfully processed Landsat scene to {output_path}")
            return output_path
            
        except Exception as e:
            logger.error(f"Failed to process Landsat scene: {str(e)}")
            raise

    @staticmethod
    def upload_to_minio(local_path: str, bucket: str, object_key: str) -> str:
        """
        Upload COG to MinIO using boto3.
        """
        try:
            # Assuming AWS credentials or MinIO credentials are in env vars
            s3_client = boto3.client('s3', 
                endpoint_url=os.environ.get('MINIO_ENDPOINT'),
                aws_access_key_id=os.environ.get('MINIO_ACCESS_KEY'),
                aws_secret_access_key=os.environ.get('MINIO_SECRET_KEY')
            )
            
            s3_client.upload_file(local_path, bucket, object_key, ExtraArgs={'ContentType': 'image/tiff'})
            s3_uri = f"s3://{bucket}/{object_key}"
            logger.info(f"Successfully uploaded COG to {s3_uri}")
            return s3_uri
        except Exception as e:
            logger.error(f"Failed to upload COG to MinIO: {str(e)}")
            raise
