import numpy as np
import xarray as xr

class SpectralIndexCalculator:
    """
    Calculates various vegetation and environmental indices from optical satellite imagery.
    All methods are vectorized using xarray and numpy.
    """

    @staticmethod
    def compute_ndvi(nir: xr.DataArray, red: xr.DataArray) -> xr.DataArray:
        """
        Normalized Difference Vegetation Index (NDVI).
        Formula: (NIR - Red) / (NIR + Red + 1e-6)
        """
        ndvi = (nir - red) / (nir + red + 1e-6)
        return ndvi.clip(-1, 1)

    @staticmethod
    def compute_evi(nir: xr.DataArray, red: xr.DataArray, blue: xr.DataArray) -> xr.DataArray:
        """
        Enhanced Vegetation Index (EVI).
        Formula: 2.5 * (NIR - Red) / (NIR + 6*Red - 7.5*Blue + 1 + 1e-6)
        """
        evi = 2.5 * (nir - red) / (nir + 6 * red - 7.5 * blue + 1 + 1e-6)
        return evi.clip(-1, 2.5)

    @staticmethod
    def compute_savi(nir: xr.DataArray, red: xr.DataArray, L: float = 0.5) -> xr.DataArray:
        """
        Soil Adjusted Vegetation Index (SAVI).
        Formula: ((NIR - Red) / (NIR + Red + L)) * (1 + L)
        """
        savi = ((nir - red) / (nir + red + L)) * (1 + L)
        return savi

    @staticmethod
    def compute_ndre(nir: xr.DataArray, red_edge1: xr.DataArray) -> xr.DataArray:
        """
        Normalized Difference Red Edge Index (NDRE).
        Formula: (NIR - RE1) / (NIR + RE1 + 1e-6)
        """
        ndre = (nir - red_edge1) / (nir + red_edge1 + 1e-6)
        return ndre.clip(-1, 1)

    @staticmethod
    def compute_nbr(nir: xr.DataArray, swir2: xr.DataArray) -> xr.DataArray:
        """
        Normalized Burn Ratio (NBR).
        Formula: (NIR - SWIR2) / (NIR + SWIR2 + 1e-6)
        """
        nbr = (nir - swir2) / (nir + swir2 + 1e-6)
        return nbr.clip(-1, 1)

    @staticmethod
    def compute_ndwi(nir: xr.DataArray, swir1: xr.DataArray) -> xr.DataArray:
        """
        Normalized Difference Water Index (NDWI).
        Formula: (NIR - SWIR1) / (NIR + SWIR1 + 1e-6)
        """
        ndwi = (nir - swir1) / (nir + swir1 + 1e-6)
        return ndwi.clip(-1, 1)

    @staticmethod
    def compute_all_indices(dataset: xr.Dataset) -> xr.Dataset:
        """
        Computes NDVI, EVI, SAVI, NDRE, NBR, and NDWI.
        Expects bands: B02 (Blue), B04 (Red), B05 (RedEdge1), B08 (NIR), B11 (SWIR1), B12 (SWIR2).
        Applies cloud masking from SCL band if present.
        """
        ds_out = dataset.copy()
        
        # Cast to float32
        nir = dataset['B08'].astype(np.float32)
        red = dataset['B04'].astype(np.float32)
        blue = dataset['B02'].astype(np.float32)
        re1 = dataset['B05'].astype(np.float32)
        swir1 = dataset['B11'].astype(np.float32)
        swir2 = dataset['B12'].astype(np.float32)
        
        if 'SCL' in dataset.data_vars:
            scl = dataset['SCL']
            # Valid classes: 4, 5, 6
            mask = scl.isin([4, 5, 6])
            nir = nir.where(mask)
            red = red.where(mask)
            blue = blue.where(mask)
            re1 = re1.where(mask)
            swir1 = swir1.where(mask)
            swir2 = swir2.where(mask)
            
        ds_out['NDVI'] = SpectralIndexCalculator.compute_ndvi(nir, red)
        ds_out['EVI'] = SpectralIndexCalculator.compute_evi(nir, red, blue)
        ds_out['SAVI'] = SpectralIndexCalculator.compute_savi(nir, red)
        ds_out['NDRE'] = SpectralIndexCalculator.compute_ndre(nir, re1)
        ds_out['NBR'] = SpectralIndexCalculator.compute_nbr(nir, swir2)
        ds_out['NDWI'] = SpectralIndexCalculator.compute_ndwi(nir, swir1)
        
        return ds_out
