import numpy as np
import xarray as xr
import pandas as pd
import geopandas as gpd
from scipy.stats import linregress
import rasterio.features
from shapely.geometry import shape
import logging

logger = logging.getLogger(__name__)

class ForestChangeDetector:
    """
    Time-Series Forest Change Detection using methodologies like CCDC/COLD.
    """

    @staticmethod
    def detect_loss_gain(ndvi_timeseries: xr.DataArray, baseline_period: slice, monitoring_period: slice) -> dict:
        """
        Compare mean NDVI between baseline and monitoring periods.
        Classifies pixels as GAIN, LOSS, or STABLE.
        """
        baseline_mean = ndvi_timeseries.sel(time=baseline_period).mean(dim='time')
        monitor_mean = ndvi_timeseries.sel(time=monitoring_period).mean(dim='time')
        
        diff = monitor_mean - baseline_mean
        
        gain_mask = diff > 0.1
        loss_mask = diff < -0.1
        stable_mask = (diff >= -0.1) & (diff <= 0.1)
        
        try:
            dx = abs(float(ndvi_timeseries.x[1] - ndvi_timeseries.x[0]))
            dy = abs(float(ndvi_timeseries.y[1] - ndvi_timeseries.y[0]))
            pixel_area_ha = (dx * dy) / 10000.0
        except Exception as e:
            logger.warning(f"Failed to calculate pixel area, defaulting to 0.01 ha (10m res). {e}")
            pixel_area_ha = 0.01
            
        gain_area = float(gain_mask.sum().item()) * pixel_area_ha
        loss_area = float(loss_mask.sum().item()) * pixel_area_ha
        stable_area = float(stable_mask.sum().item()) * pixel_area_ha
        
        change_map = xr.zeros_like(diff, dtype=np.int8)
        change_map = change_map.where(~gain_mask, 1)
        change_map = change_map.where(~loss_mask, -1)
        
        return {
            'loss_area_ha': loss_area,
            'gain_area_ha': gain_area,
            'stable_area_ha': stable_area,
            'change_map': change_map
        }

    @staticmethod
    def detect_disturbance_zscore(timeseries: xr.DataArray, window_size: int = 12, threshold: float = 3.0) -> xr.DataArray:
        """
        Z-score based anomaly detection for detecting abrupt forest disturbances.
        """
        rolling_mean = timeseries.rolling(time=window_size, center=False).mean()
        rolling_std = timeseries.rolling(time=window_size, center=False).std()
        
        z_score = (timeseries - rolling_mean) / (rolling_std + 1e-6)
        disturbance = z_score < -threshold
        
        return disturbance

    @staticmethod
    def compute_trend(timeseries: xr.DataArray) -> dict:
        """
        Linear regression trend for each pixel over time.
        """
        def calc_linregress(y):
            if np.isnan(y).all():
                return np.array([np.nan, np.nan, np.nan, np.nan])
            valid = ~np.isnan(y)
            x = np.arange(len(y))[valid]
            y_valid = y[valid]
            if len(x) < 2:
                return np.array([np.nan, np.nan, np.nan, np.nan])
            res = linregress(x, y_valid)
            return np.array([res.slope, res.intercept, res.rvalue**2, res.pvalue])
        
        res = xr.apply_ufunc(
            calc_linregress,
            timeseries,
            input_core_dims=[['time']],
            output_core_dims=[['stats']],
            vectorize=True,
            dask="parallelized",
            output_dtypes=[float],
            dask_gufunc_kwargs={'output_sizes': {'stats': 4}}
        )
        
        return {
            'slope': res.isel(stats=0),
            'intercept': res.isel(stats=1),
            'r_squared': res.isel(stats=2),
            'p_value': res.isel(stats=3)
        }

    @staticmethod
    def generate_alert_map(change_map: xr.DataArray, min_patch_size_ha: float = 0.5) -> gpd.GeoDataFrame:
        """
        Convert raster disturbance map to vector polygons and filter out small patches.
        """
        mask = (change_map == -1).values
        
        transform = None
        if hasattr(change_map, 'rio'):
            transform = change_map.rio.transform()
            
        shapes = rasterio.features.shapes(
            change_map.values.astype(np.int16), 
            mask=mask, 
            transform=transform
        )
        
        polygons = [shape(geom) for geom, val in shapes]
        
        crs = "EPSG:4326"
        if hasattr(change_map, 'rio') and change_map.rio.crs:
            crs = change_map.rio.crs
            
        gdf = gpd.GeoDataFrame({'geometry': polygons, 'severity': -1}, crs=crs)
        
        if gdf.empty:
            return gdf
            
        if gdf.crs and gdf.crs.is_geographic:
            try:
                gdf_proj = gdf.to_crs(gdf.estimate_utm_crs())
                gdf['area_ha'] = gdf_proj.geometry.area / 10000.0
            except:
                gdf['area_ha'] = gdf.geometry.area / 10000.0  # Approx or warning needed
        else:
            gdf['area_ha'] = gdf.geometry.area / 10000.0
            
        filtered_gdf = gdf[gdf['area_ha'] >= min_patch_size_ha].copy()
        filtered_gdf['detection_date'] = pd.Timestamp.utcnow()
        
        return filtered_gdf
