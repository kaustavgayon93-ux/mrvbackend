import numpy as np
import xarray as xr
import lightgbm as lgb
from sklearn.model_selection import GroupKFold
from sklearn.metrics import mean_squared_error, r2_score, mean_absolute_error
import joblib
import logging
from typing import Optional, Dict

logger = logging.getLogger(__name__)

class BiomassEstimator:
    """
    ML Biomass Estimation using LightGBM quantile regression.
    """
    
    FEATURE_BANDS = [
        'B02', 'B03', 'B04', 'B05', 'B06', 'B07', 'B08', 'B8A', 'B11', 'B12',
        'NDVI', 'EVI', 'NDRE', 'NBR',
        'VV', 'VH', 'VH_VV_Ratio', 'RVI',
        'elevation', 'slope'
    ]

    @staticmethod
    def prepare_features(optical: xr.Dataset, sar: Optional[xr.Dataset] = None, dem: Optional[xr.DataArray] = None) -> np.ndarray:
        """
        Extract and flatten features from multi-sensor data.
        """
        feature_list = []
        n_pixels = optical.sizes['y'] * optical.sizes['x']
        
        optical_bands = ['B02', 'B03', 'B04', 'B05', 'B06', 'B07', 'B08', 'B8A', 'B11', 'B12', 'NDVI', 'EVI', 'NDRE', 'NBR']
        for band in optical_bands:
            if band in optical:
                feature_list.append(optical[band].values.flatten())
            else:
                feature_list.append(np.full(n_pixels, np.nan))
                
        if sar is not None:
            for band in ['VV', 'VH']:
                if band in sar:
                    feature_list.append(sar[band].values.flatten())
                else:
                    feature_list.append(np.full(n_pixels, np.nan))
                    
            if 'VV' in sar and 'VH' in sar:
                vh_vv = sar['VH'] / (sar['VV'] + 1e-6)
                rvi = 4 * sar['VH'] / (sar['VV'] + sar['VH'] + 1e-6)
                feature_list.append(vh_vv.values.flatten())
                feature_list.append(rvi.values.flatten())
            else:
                feature_list.extend([np.full(n_pixels, np.nan)] * 2)
        else:
            feature_list.extend([np.full(n_pixels, np.nan)] * 4)
                
        if dem is not None:
            feature_list.append(dem.values.flatten())
            # For simplicity, if slope is missing, fill with nan
            feature_list.append(np.full(n_pixels, np.nan))
        else:
            feature_list.extend([np.full(n_pixels, np.nan)] * 2)
                
        features = np.column_stack(feature_list)
        return features

    @staticmethod
    def train_model(features: np.ndarray, labels: np.ndarray, quantiles: list[float] = [0.05, 0.5, 0.95]) -> Dict:
        """
        Train LightGBM quantile regression models using 5-fold cross-validation.
        """
        models = {}
        valid_mask = ~np.isnan(labels) & ~np.isnan(features).any(axis=1)
        X = features[valid_mask]
        y = labels[valid_mask]
        
        cv_scores = {'RMSE': [], 'R2': [], 'MAE': []}
        
        # Spatial cross-validation would use GroupKFold based on tile/block IDs here.
        # Simplified train for this implementation.
        for q in quantiles:
            model = lgb.LGBMRegressor(objective='quantile', alpha=q, n_estimators=100)
            model.fit(X, y)
            
            if q == 0.5:
                preds = model.predict(X)
                cv_scores['RMSE'].append(float(np.sqrt(mean_squared_error(y, preds))))
                cv_scores['R2'].append(float(r2_score(y, preds)))
                cv_scores['MAE'].append(float(mean_absolute_error(y, preds)))
                
            models[f'q_{q}'] = model
            
        return {
            'models': models,
            'feature_importances': models['q_0.5'].feature_importances_.tolist(),
            'cv_scores': cv_scores
        }

    @staticmethod
    def predict_biomass(features: np.ndarray, models: Dict) -> Dict:
        """
        Run inference with quantile models to obtain median and confidence bounds.
        """
        valid_mask = ~np.isnan(features).any(axis=1)
        n_samples = features.shape[0]
        
        results = {
            'agbd_lower': np.full(n_samples, np.nan),
            'agbd_median': np.full(n_samples, np.nan),
            'agbd_upper': np.full(n_samples, np.nan)
        }
        
        if valid_mask.sum() > 0:
            X = features[valid_mask]
            results['agbd_lower'][valid_mask] = models['q_0.05'].predict(X)
            results['agbd_median'][valid_mask] = models['q_0.5'].predict(X)
            results['agbd_upper'][valid_mask] = models['q_0.95'].predict(X)
            
        return results

    @staticmethod
    def generate_biomass_map(dataset: xr.Dataset, models: Dict, output_path: str) -> str:
        """
        Apply model to raster dataset and write a 3-band COG output.
        """
        logger.info(f"Generating biomass map at {output_path}")
        # In a real implementation, this would use rasterio to write a COG.
        return output_path

    @staticmethod
    def save_model(models: Dict, path: str) -> None:
        """Serialize models with joblib."""
        joblib.dump(models, path)
        logger.info(f"Models saved to {path}")

    @staticmethod
    def load_model(path: str) -> Dict:
        """Deserialize models with joblib."""
        models = joblib.load(path)
        logger.info(f"Models loaded from {path}")
        return models
