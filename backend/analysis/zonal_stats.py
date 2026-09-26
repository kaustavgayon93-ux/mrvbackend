import numpy as np
import geopandas as gpd
from rasterstats import zonal_stats
import rasterio
import rasterio.mask
import logging
from typing import Dict, List, Any

logger = logging.getLogger(__name__)

class ZonalStatsCalculator:
    """
    On-Demand Zonal Statistics calculation for raster data.
    """

    @staticmethod
    def compute_zonal_stats(raster_path: str, geometry: Dict[str, Any], stats: List[str] = ['mean', 'std', 'min', 'max', 'count', 'median']) -> Dict[str, Any]:
        """
        Use rasterstats to compute statistics for a GeoJSON geometry on a COG.
        """
        results = zonal_stats([geometry], raster_path, stats=stats)
        if results and results[0]:
            return results[0]
        return {}

    @staticmethod
    def compute_area_weighted_stats(raster_path: str, polygons: gpd.GeoDataFrame, weight_field: str = 'area_ha') -> Dict[str, float]:
        """
        Area-weighted statistics across multiple strata.
        """
        stats_list = zonal_stats(polygons, raster_path, stats=['mean'])
        
        total_weight = 0.0
        weighted_sum = 0.0
        
        for idx, stats in enumerate(stats_list):
            mean_val = stats.get('mean')
            if mean_val is not None:
                weight = polygons.iloc[idx][weight_field]
                weighted_sum += mean_val * weight
                total_weight += weight
                
        if total_weight > 0:
            return {'area_weighted_mean': weighted_sum / total_weight}
        return {'area_weighted_mean': np.nan}

    @staticmethod
    def compute_carbon_stock(biomass_raster_path: str, project_boundary: Dict[str, Any], carbon_fraction: float = 0.47) -> Dict[str, float]:
        """
        Calculate total carbon stock and tCO2e for a project area.
        """
        stats = zonal_stats([project_boundary], biomass_raster_path, stats=['mean', 'count'])
        if not stats or stats[0]['count'] == 0 or stats[0]['mean'] is None:
            return {}
            
        mean_agbd = stats[0]['mean']
        count = stats[0]['count']
        
        with rasterio.open(biomass_raster_path) as src:
            res_x, res_y = src.res
            # Assuming projected CRS in meters
            pixel_area_ha = (res_x * res_y) / 10000.0
            
        total_biomass_mg = mean_agbd * count * pixel_area_ha
        total_carbon_tc = total_biomass_mg * carbon_fraction
        total_tco2e = total_carbon_tc * (44.0 / 12.0)
        
        return {
            'total_biomass_mg': float(total_biomass_mg),
            'total_carbon_tc': float(total_carbon_tc),
            'total_tco2e': float(total_tco2e),
            'mean_agbd_mg_ha': float(mean_agbd)
        }

    @staticmethod
    def generate_histogram(raster_path: str, geometry: Dict[str, Any], n_bins: int = 50) -> Dict[str, Any]:
        """
        Extract pixel values within a geometry and compute the histogram.
        """
        try:
            with rasterio.open(raster_path) as src:
                out_image, _ = rasterio.mask.mask(src, [geometry], crop=True)
                data = out_image[0]
                valid_data = data[(data != src.nodata) & (~np.isnan(data))]
                
                if len(valid_data) == 0:
                    return {}
                    
                counts, bin_edges = np.histogram(valid_data, bins=n_bins)
                
                return {
                    'bin_edges': bin_edges.tolist(),
                    'counts': counts.tolist(),
                    'mean': float(np.mean(valid_data)),
                    'median': float(np.median(valid_data)),
                    'std': float(np.std(valid_data))
                }
        except Exception as e:
            logger.error(f"Error generating histogram: {e}")
            return {}
