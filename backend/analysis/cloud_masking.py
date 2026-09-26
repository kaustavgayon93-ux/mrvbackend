import numpy as np
import xarray as xr
import logging

logger = logging.getLogger(__name__)

class CloudMasker:
    """
    Cloud and shadow masking utility for Sentinel-2 and Landsat imagery.
    """

    @staticmethod
    def apply_scl_mask(dataset: xr.Dataset, scl_band: str = 'SCL') -> xr.Dataset:
        """
        Masks a Sentinel-2 dataset using the Scene Classification Layer (SCL).
        Valid classes: 4 (Vegetation), 5 (Bare Soil/Not Vegetated), 6 (Water).
        Masked classes are set to NaN.
        """
        if scl_band not in dataset:
            logger.warning(f"SCL band {scl_band} not found. Skipping masking.")
            return dataset
        
        scl = dataset[scl_band]
        valid_mask = scl.isin([4, 5, 6])
        return dataset.where(valid_mask)

    @staticmethod
    def apply_qa_pixel_mask(dataset: xr.Dataset, qa_band: str = 'QA_PIXEL') -> xr.Dataset:
        """
        Masks a Landsat dataset using QA_PIXEL bitmask.
        Bit 3: Cloud Shadow, Bit 4: Snow, Bit 5: Cloud, Bit 6: Cloud (dilated).
        """
        if qa_band not in dataset:
            logger.warning(f"QA_PIXEL band {qa_band} not found. Skipping masking.")
            return dataset
        
        qa = dataset[qa_band].astype(np.uint16)
        
        cloud_shadow = (qa & (1 << 3)) > 0
        snow = (qa & (1 << 4)) > 0
        cloud = (qa & (1 << 5)) > 0
        cloud_dilated = (qa & (1 << 6)) > 0
        
        invalid_mask = cloud_shadow | snow | cloud | cloud_dilated
        return dataset.where(~invalid_mask)

    @staticmethod
    def compute_cloud_percentage(mask: xr.DataArray) -> float:
        """
        Calculate the percentage of cloudy pixels from a binary mask.
        """
        total_pixels = mask.size
        if total_pixels == 0:
            return 0.0
            
        cloudy_pixels = int(mask.sum().item())
        return (cloudy_pixels / total_pixels) * 100.0

    @staticmethod
    def create_composite(datasets: list[xr.Dataset], method: str = 'median') -> xr.Dataset:
        """
        Create a temporal composite from multiple scenes to reduce cloud contamination.
        Methods supported: 'median', 'mean', 'max'.
        """
        if not datasets:
            raise ValueError("Empty list of datasets provided.")
            
        concat_ds = xr.concat(datasets, dim='time')
        
        if method == 'median':
            return concat_ds.median(dim='time', keep_attrs=True)
        elif method == 'mean':
            return concat_ds.mean(dim='time', keep_attrs=True)
        elif method == 'max':
            return concat_ds.max(dim='time', keep_attrs=True)
        else:
            raise ValueError(f"Unsupported compositing method: {method}")
