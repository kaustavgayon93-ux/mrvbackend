import numpy as np
import xarray as xr
import pandas as pd
from scipy.optimize import curve_fit
from scipy.signal import savgol_filter
import logging
from typing import List, Tuple, Dict, Any

logger = logging.getLogger(__name__)

class TimeSeriesAnalyzer:
    """
    Temporal compositing and harmonic analysis of vegetation time series.
    """

    @staticmethod
    def create_monthly_composite(scenes: List[xr.Dataset], method: str = 'median') -> xr.Dataset:
        """
        Group scenes by month and create composites.
        """
        if not scenes:
            raise ValueError("No scenes provided for compositing.")
            
        concat_ds = xr.concat(scenes, dim='time')
        
        if method == 'median':
            return concat_ds.groupby('time.month').median(dim='time', keep_attrs=True)
        elif method == 'mean':
            return concat_ds.groupby('time.month').mean(dim='time', keep_attrs=True)
        else:
            raise ValueError(f"Method {method} not supported.")

    @staticmethod
    def create_annual_composite(scenes: List[xr.Dataset], method: str = 'medoid') -> xr.Dataset:
        """
        Create an annual composite from multiple scenes.
        """
        if not scenes:
            raise ValueError("No scenes provided for compositing.")
            
        concat_ds = xr.concat(scenes, dim='time')
        
        if method == 'medoid':
            # Simplified medoid approximation: using median for robust central tendency
            return concat_ds.median(dim='time', keep_attrs=True)
        elif method == 'median':
            return concat_ds.median(dim='time', keep_attrs=True)
        elif method == 'mean':
            return concat_ds.mean(dim='time', keep_attrs=True)
        else:
            raise ValueError(f"Method {method} not supported.")

    @staticmethod
    def extract_pixel_timeseries(datasets: List[xr.Dataset], point: Tuple[float, float], band: str) -> pd.DataFrame:
        """
        Extract time series for a single spatial point across all scenes.
        """
        if not datasets:
            return pd.DataFrame()
            
        concat_ds = xr.concat(datasets, dim='time')
        x, y = point
        
        try:
            ts = concat_ds.sel(x=x, y=y, method='nearest')[band].values
            times = concat_ds['time'].values
            
            df = pd.DataFrame({
                'date': times,
                'value': ts
            }).sort_values('date').reset_index(drop=True)
            return df
        except KeyError:
            logger.error(f"Band {band} not found or spatial coordinates out of bounds.")
            return pd.DataFrame()

    @staticmethod
    def harmonic_fitting(timeseries: pd.DataFrame, n_harmonics: int = 2) -> Dict[str, Any]:
        """
        Fit a harmonic regression model to a time series to model seasonality.
        Formula: y = a0 + a1*cos(2π*t) + b1*sin(2π*t) + a2*cos(4π*t) + b2*sin(4π*t)
        """
        df = timeseries.dropna(subset=['value']).copy()
        
        if df.empty or len(df) < n_harmonics * 2 + 1:
            return {}
            
        days_in_year = 365.25
        t = (df['date'] - df['date'].min()).dt.days / days_in_year
        y = df['value'].values
        
        def harmonic_model(t, a0, a1, b1, a2, b2):
            return a0 + a1 * np.cos(2 * np.pi * t) + b1 * np.sin(2 * np.pi * t) + \
                   a2 * np.cos(4 * np.pi * t) + b2 * np.sin(4 * np.pi * t)
                   
        try:
            popt, _ = curve_fit(harmonic_model, t, y)
            fitted = harmonic_model(t, *popt)
            residuals = y - fitted
            rmse = np.sqrt(np.mean(residuals**2))
            
            return {
                'coefficients': popt.tolist(),
                'fitted_values': fitted.tolist(),
                'residuals': residuals.tolist(),
                'rmse': float(rmse)
            }
        except RuntimeError:
            logger.warning("Harmonic curve fit failed to converge.")
            return {}

    @staticmethod
    def smooth_timeseries(timeseries: pd.DataFrame, method: str = 'savgol', window: int = 7) -> pd.DataFrame:
        """
        Smooth a time series using Savitzky-Golay or similar filter.
        """
        df = timeseries.copy().sort_values('date')
        
        if method == 'savgol':
            if len(df) > window:
                polyorder = min(3, window - 1)
                df['smoothed'] = savgol_filter(df['value'], window_length=window, polyorder=polyorder)
            else:
                df['smoothed'] = df['value']
        else:
            logger.warning(f"Smoothing method {method} not implemented. Returning original values.")
            df['smoothed'] = df['value']
            
        return df

    @staticmethod
    def detect_phenology(smoothed_ts: pd.DataFrame) -> Dict[str, Any]:
        """
        Detect Start of Season (SOS), End of Season (EOS), and peak dates.
        """
        df = smoothed_ts.copy()
        if 'smoothed' not in df.columns or df.empty:
            return {}
            
        peak_idx = df['smoothed'].idxmax()
        peak_date = df.loc[peak_idx, 'date']
        amplitude = df['smoothed'].max() - df['smoothed'].min()
        
        # Simple threshold for onset/senescence (20% of amplitude)
        thresh = df['smoothed'].min() + 0.2 * amplitude
        
        pre_peak = df.loc[:peak_idx]
        post_peak = df.loc[peak_idx:]
        
        sos_candidates = pre_peak[pre_peak['smoothed'] >= thresh]
        sos_idx = sos_candidates.index.min() if not sos_candidates.empty else df.index[0]
        
        eos_candidates = post_peak[post_peak['smoothed'] <= thresh]
        eos_idx = eos_candidates.index.min() if not eos_candidates.empty else df.index[-1]
        
        return {
            'sos': df.loc[sos_idx, 'date'].isoformat() if hasattr(df.loc[sos_idx, 'date'], 'isoformat') else str(df.loc[sos_idx, 'date']),
            'eos': df.loc[eos_idx, 'date'].isoformat() if hasattr(df.loc[eos_idx, 'date'], 'isoformat') else str(df.loc[eos_idx, 'date']),
            'peak_date': peak_date.isoformat() if hasattr(peak_date, 'isoformat') else str(peak_date),
            'amplitude': float(amplitude)
        }
