"""
Time Series Forecaster using Prophet

Predicts future metrics values:
- CPU, memory, error rates 1-6 hours ahead
- Automatic seasonality detection (daily, weekly)
- Confidence intervals for predictions
- Trend analysis and change point detection
"""

import numpy as np
import pandas as pd
from datetime import datetime, timedelta
import joblib
import logging
from pathlib import Path
from typing import Dict, List, Optional, Tuple

logger = logging.getLogger(__name__)


class MetricForecaster:
    """Prophet-based time series forecasting for metrics"""
    
    def __init__(self):
        self.models = {}  # One model per metric
        self.is_trained = False
        self.training_stats = {}
        self.metrics_to_forecast = [
            'cpu_usage_percent',
            'memory_usage_mb',
            'error_rate',
            'response_time_p95'
        ]
    
    def train(self, df: pd.DataFrame, metrics: Optional[List[str]] = None) -> Dict:
        """
        Train Prophet models for each metric
        
        Args:
            df: DataFrame with 'timestamp' and metric columns
            metrics: List of metrics to forecast (default: all supported)
            
        Returns:
            Training statistics
        """
        try:
            from prophet import Prophet
        except ImportError:
            raise ImportError("Prophet not installed. Run: pip install prophet")
        
        if metrics is None:
            metrics = self.metrics_to_forecast
        
        # Validate data
        if len(df) < 100:
            raise ValueError(f"Need at least 100 samples, got {len(df)}")
        
        if 'timestamp' not in df.columns:
            raise ValueError("DataFrame must have 'timestamp' column")
        
        # Ensure timestamp is datetime
        df = df.copy()
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        
        logger.info(f"Training forecasters on {len(df)} samples for {len(metrics)} metrics...")
        
        training_results = {}
        
        for metric in metrics:
            if metric not in df.columns:
                logger.warning(f"Metric {metric} not in data, skipping")
                continue
            
            try:
                # Prepare data for Prophet (requires 'ds' and 'y' columns)
                prophet_df = pd.DataFrame({
                    'ds': df['timestamp'],
                    'y': df[metric]
                })
                
                # Remove NaN values
                prophet_df = prophet_df.dropna()
                
                if len(prophet_df) < 100:
                    logger.warning(f"Not enough valid data for {metric}, skipping")
                    continue
                
                # Configure Prophet
                model = Prophet(
                    yearly_seasonality=False,  # Not enough data for yearly
                    weekly_seasonality=True,   # Weekly patterns
                    daily_seasonality=True,    # Daily patterns
                    seasonality_mode='multiplicative',  # Better for metrics
                    changepoint_prior_scale=0.05,  # Conservative change detection
                    interval_width=0.95  # 95% confidence intervals
                )
                
                # Train model
                logger.debug(f"Training Prophet model for {metric}...")
                model.fit(prophet_df)
                
                # Store model
                self.models[metric] = model
                
                # Calculate training statistics
                train_predictions = model.predict(prophet_df)
                mse = np.mean((train_predictions['yhat'].values - prophet_df['y'].values) ** 2)
                rmse = np.sqrt(mse)
                mae = np.mean(np.abs(train_predictions['yhat'].values - prophet_df['y'].values))
                
                training_results[metric] = {
                    'samples': len(prophet_df),
                    'rmse': float(rmse),
                    'mae': float(mae),
                    'mean_value': float(prophet_df['y'].mean()),
                    'std_value': float(prophet_df['y'].std())
                }
                
                logger.info(f"✓ Trained {metric}: RMSE={rmse:.2f}, MAE={mae:.2f}")
                
            except Exception as e:
                logger.error(f"Failed to train {metric}: {e}")
                continue
        
        if not self.models:
            raise ValueError("Failed to train any models")
        
        self.is_trained = True
        self.training_stats = {
            'metrics_trained': list(self.models.keys()),
            'total_metrics': len(self.models),
            'training_results': training_results,
            'trained_at': datetime.now().isoformat()
        }
        
        logger.info(f"Training complete: {len(self.models)} models trained")
        
        return self.training_stats
    
    def forecast(self, hours_ahead: int = 6) -> pd.DataFrame:
        """
        Generate forecasts for all trained metrics
        
        Args:
            hours_ahead: How many hours to forecast (1-24)
            
        Returns:
            DataFrame with forecasts and confidence intervals
        """
        if not self.is_trained:
            raise ValueError("Models not trained. Call train() first.")
        
        if not (1 <= hours_ahead <= 24):
            raise ValueError("hours_ahead must be between 1 and 24")
        
        # Create future dates
        last_timestamp = datetime.now()
        future_dates = pd.date_range(
            start=last_timestamp,
            periods=hours_ahead * 60,  # One prediction per minute
            freq='1min'
        )
        
        future_df = pd.DataFrame({'ds': future_dates})
        
        # Generate predictions for each metric
        forecasts = {'timestamp': future_dates}
        
        for metric, model in self.models.items():
            try:
                predictions = model.predict(future_df)
                
                forecasts[f'{metric}_forecast'] = predictions['yhat'].values
                forecasts[f'{metric}_lower'] = predictions['yhat_lower'].values
                forecasts[f'{metric}_upper'] = predictions['yhat_upper'].values
                
            except Exception as e:
                logger.error(f"Failed to forecast {metric}: {e}")
        
        forecast_df = pd.DataFrame(forecasts)
        
        logger.info(f"Generated {len(forecast_df)} forecast points for {len(self.models)} metrics")
        
        return forecast_df
    
    def forecast_single_metric(self, metric: str, hours_ahead: int = 6) -> pd.DataFrame:
        """
        Forecast a single metric
        
        Args:
            metric: Metric name to forecast
            hours_ahead: How many hours ahead
            
        Returns:
            DataFrame with forecasts
        """
        if not self.is_trained:
            raise ValueError("Models not trained")
        
        if metric not in self.models:
            raise ValueError(f"No model trained for {metric}")
        
        model = self.models[metric]
        
        # Create future dates
        future_dates = pd.date_range(
            start=datetime.now(),
            periods=hours_ahead * 60,
            freq='1min'
        )
        
        future_df = pd.DataFrame({'ds': future_dates})
        predictions = model.predict(future_df)
        
        result = pd.DataFrame({
            'timestamp': future_dates,
            'forecast': predictions['yhat'].values,
            'lower_bound': predictions['yhat_lower'].values,
            'upper_bound': predictions['yhat_upper'].values
        })
        
        return result
    
    def predict_next_hour(self) -> Dict[str, Dict]:
        """
        Get average predicted values for next hour
        
        Returns:
            Dictionary with predictions per metric
        """
        if not self.is_trained:
            raise ValueError("Models not trained")
        
        forecast_df = self.forecast(hours_ahead=1)
        
        predictions = {}
        
        for metric in self.models.keys():
            forecast_col = f'{metric}_forecast'
            lower_col = f'{metric}_lower'
            upper_col = f'{metric}_upper'
            
            if forecast_col in forecast_df.columns:
                predictions[metric] = {
                    'mean_forecast': float(forecast_df[forecast_col].mean()),
                    'max_forecast': float(forecast_df[forecast_col].max()),
                    'lower_bound': float(forecast_df[lower_col].mean()),
                    'upper_bound': float(forecast_df[upper_col].mean()),
                    'trend': 'increasing' if forecast_df[forecast_col].iloc[-1] > forecast_df[forecast_col].iloc[0] else 'decreasing'
                }
        
        return predictions
    
    def detect_anomalous_forecast(self, thresholds: Dict[str, float]) -> List[Dict]:
        """
        Detect if forecasts predict threshold breaches
        
        Args:
            thresholds: Dictionary of metric -> threshold value
            
        Returns:
            List of predicted threshold breaches
        """
        predictions = self.predict_next_hour()
        
        alerts = []
        
        for metric, pred in predictions.items():
            threshold = thresholds.get(metric)
            if not threshold:
                continue
            
            # Check if forecast exceeds threshold
            if pred['mean_forecast'] > threshold:
                severity = 'CRITICAL' if pred['mean_forecast'] > threshold * 1.2 else 'WARNING'
                
                alerts.append({
                    'type': 'predicted_threshold_breach',
                    'metric': metric,
                    'severity': severity,
                    'predicted_value': pred['mean_forecast'],
                    'threshold': threshold,
                    'confidence_interval': [pred['lower_bound'], pred['upper_bound']],
                    'trend': pred['trend'],
                    'time_to_breach': 'within 1 hour'
                })
        
        return alerts
    
    def get_trend_analysis(self, metric: str) -> Dict:
        """
        Analyze trends for a metric
        
        Args:
            metric: Metric name
            
        Returns:
            Trend analysis
        """
        if metric not in self.models:
            raise ValueError(f"No model for {metric}")
        
        model = self.models[metric]
        
        # Get next 24 hours forecast
        forecast_df = self.forecast_single_metric(metric, hours_ahead=24)
        
        # Calculate trend
        start_value = forecast_df['forecast'].iloc[0]
        end_value = forecast_df['forecast'].iloc[-1]
        
        change = end_value - start_value
        pct_change = (change / start_value * 100) if start_value != 0 else 0
        
        # Determine trend direction
        if abs(pct_change) < 5:
            trend = 'stable'
        elif pct_change > 0:
            trend = 'increasing'
        else:
            trend = 'decreasing'
        
        return {
            'metric': metric,
            'current_forecast': float(start_value),
            '24h_forecast': float(end_value),
            'change': float(change),
            'percent_change': float(pct_change),
            'trend': trend,
            'volatility': float(forecast_df['forecast'].std())
        }
    
    def save(self, filepath: str) -> None:
        """Save trained models"""
        if not self.is_trained:
            raise ValueError("Cannot save untrained models")
        
        model_data = {
            'models': self.models,
            'training_stats': self.training_stats,
            'metrics_to_forecast': self.metrics_to_forecast
        }
        
        Path(filepath).parent.mkdir(parents=True, exist_ok=True)
        joblib.dump(model_data, filepath)
        
        logger.info(f"Forecaster models saved to {filepath}")
    
    @classmethod
    def load(cls, filepath: str) -> 'MetricForecaster':
        """Load trained models"""
        model_data = joblib.load(filepath)
        
        forecaster = cls()
        forecaster.models = model_data['models']
        forecaster.training_stats = model_data['training_stats']
        forecaster.metrics_to_forecast = model_data['metrics_to_forecast']
        forecaster.is_trained = True
        
        logger.info(f"Forecaster loaded from {filepath}")
        
        return forecaster
    
    def get_model_info(self) -> Dict:
        """Get information about trained models"""
        return {
            'is_trained': self.is_trained,
            'metrics_trained': list(self.models.keys()),
            'total_models': len(self.models),
            'training_stats': self.training_stats
        }


def create_default_forecaster() -> MetricForecaster:
    """Create forecaster with default settings"""
    return MetricForecaster()
