"""
Failure Prediction using LightGBM - Phase 5

Predicts system failures hours in advance by analyzing:
- Historical metrics patterns
- Past incident characteristics
- Temporal trends and seasonality
- Service health indicators

Uses LightGBM for fast, accurate predictions on tabular data.
"""

import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import logging

try:
    import lightgbm as lgb
    LIGHTGBM_AVAILABLE = True
except ImportError:
    LIGHTGBM_AVAILABLE = False
    lgb = None

logger = logging.getLogger(__name__)


class FailurePredictor:
    """
    LightGBM-based failure predictor for proactive incident detection.
    
    Predicts probability of system failure in the next N hours based on
    current metrics, historical patterns, and incident history.
    """
    
    def __init__(self, db_connection):
        """
        Initialize the failure predictor.
        
        Args:
            db_connection: Database connection for accessing metrics and incidents
        """
        if not LIGHTGBM_AVAILABLE:
            raise ImportError("LightGBM is required. Install with: pip install lightgbm")
        
        self.db = db_connection
        self.model = None
        self.feature_names = []
        self.is_trained = False
        
        # Model hyperparameters (optimized for small datasets)
        self.params = {
            'objective': 'binary',
            'metric': 'auc',
            'boosting_type': 'gbdt',
            'num_leaves': 31,
            'learning_rate': 0.05,
            'feature_fraction': 0.9,
            'bagging_fraction': 0.8,
            'bagging_freq': 5,
            'verbose': -1,
            'max_depth': 6,
            'min_child_samples': 20
        }
        
        # Prediction thresholds
        self.high_risk_threshold = 0.7   # >= 70% probability
        self.medium_risk_threshold = 0.4  # >= 40% probability
        
        logger.info("FailurePredictor initialized")
    
    def _extract_features(self, metrics_df: pd.DataFrame, 
                         lookback_hours: int = 1) -> pd.DataFrame:
        """
        Extract features from metrics for failure prediction.
        
        Args:
            metrics_df: DataFrame with columns: timestamp, metric_name, value, service
            lookback_hours: Hours of historical data to use
            
        Returns:
            DataFrame with engineered features
        """
        if metrics_df.empty:
            return pd.DataFrame()
        
        # Pivot metrics to wide format
        pivot = metrics_df.pivot_table(
            index='timestamp',
            columns='metric_name',
            values='value',
            aggfunc='mean'
        ).fillna(method='ffill').fillna(0)
        
        features = pd.DataFrame(index=pivot.index)
        
        # 1. Current metric values
        for col in pivot.columns:
            features[f'{col}_current'] = pivot[col]
        
        # 2. Statistical features (mean, std, min, max over lookback window)
        for col in pivot.columns:
            rolling = pivot[col].rolling(window=min(12, len(pivot)), min_periods=1)
            features[f'{col}_mean'] = rolling.mean()
            features[f'{col}_std'] = rolling.std().fillna(0)
            features[f'{col}_min'] = rolling.min()
            features[f'{col}_max'] = rolling.max()
        
        # 3. Rate of change features
        for col in pivot.columns:
            features[f'{col}_change_rate'] = pivot[col].diff().fillna(0)
            features[f'{col}_change_pct'] = pivot[col].pct_change().fillna(0).replace([np.inf, -np.inf], 0)
        
        # 4. Cross-metric interactions (critical combinations)
        if 'cpu_usage' in pivot.columns and 'memory_usage' in pivot.columns:
            features['cpu_memory_product'] = pivot['cpu_usage'] * pivot['memory_usage']
            features['cpu_memory_ratio'] = (pivot['cpu_usage'] / (pivot['memory_usage'] + 1))
        
        if 'error_rate' in pivot.columns and 'response_time' in pivot.columns:
            features['error_latency_product'] = pivot['error_rate'] * pivot['response_time']
        
        # 5. Temporal features
        features['hour'] = pd.to_datetime(features.index).hour
        features['day_of_week'] = pd.to_datetime(features.index).dayofweek
        features['is_weekend'] = (features['day_of_week'] >= 5).astype(int)
        features['is_business_hours'] = ((features['hour'] >= 9) & (features['hour'] <= 17)).astype(int)
        
        # 6. Anomaly indicators (simple threshold-based)
        if 'cpu_usage' in pivot.columns:
            features['cpu_high'] = (pivot['cpu_usage'] > 80).astype(int)
        if 'memory_usage' in pivot.columns:
            features['memory_high'] = (pivot['memory_usage'] > 85).astype(int)
        if 'error_rate' in pivot.columns:
            features['error_high'] = (pivot['error_rate'] > 5).astype(int)
        
        # Fill any remaining NaNs
        features = features.fillna(0).replace([np.inf, -np.inf], 0)
        
        return features
    
    def _prepare_training_data(self, hours_back: int = 168) -> Tuple[pd.DataFrame, pd.Series]:
        """
        Prepare training data from historical metrics and incidents.
        
        Args:
            hours_back: How many hours of history to use (default: 7 days)
            
        Returns:
            Tuple of (features_df, labels_series)
        """
        from sqlalchemy import text
        
        # Get historical metrics
        query = text("""
            SELECT timestamp, metric_name, value, service
            FROM metrics_history
            WHERE timestamp > NOW() - INTERVAL :hours HOUR
            ORDER BY timestamp
        """)
        
        result = self.db.execute(query, {"hours": hours_back})
        metrics_data = result.fetchall()
        
        if not metrics_data:
            logger.warning("No metrics data available for training")
            return pd.DataFrame(), pd.Series()
        
        # Convert to DataFrame
        metrics_df = pd.DataFrame(metrics_data, columns=['timestamp', 'metric_name', 'value', 'service'])
        
        # Extract features
        features_df = self._extract_features(metrics_df, lookback_hours=1)
        
        if features_df.empty:
            return pd.DataFrame(), pd.Series()
        
        # Get incidents for labeling
        incident_query = text("""
            SELECT detected_at, incident_type
            FROM incidents
            WHERE detected_at > NOW() - INTERVAL :hours HOUR
        """)
        
        result = self.db.execute(incident_query, {"hours": hours_back})
        incidents_data = result.fetchall()
        
        # Create labels: 1 if incident occurred within next hour, 0 otherwise
        labels = pd.Series(0, index=features_df.index)
        
        for incident_time, incident_type in incidents_data:
            # Mark samples in the hour before incident as positive
            window_start = incident_time - timedelta(hours=1)
            window_end = incident_time
            
            mask = (features_df.index >= window_start) & (features_df.index <= window_end)
            labels[mask] = 1
        
        logger.info(f"Training data: {len(features_df)} samples, {labels.sum()} positive, {(labels == 0).sum()} negative")
        
        return features_df, labels
    
    def train(self, hours_back: int = 168, num_iterations: int = 100) -> Dict:
        """
        Train the failure prediction model.
        
        Args:
            hours_back: Hours of historical data to use (default: 7 days)
            num_iterations: Number of boosting iterations
            
        Returns:
            Training metrics dictionary
        """
        logger.info(f"Training failure predictor on {hours_back} hours of data...")
        
        # Prepare data
        X, y = self._prepare_training_data(hours_back)
        
        if X.empty or len(y) < 10:
            logger.warning("Insufficient data for training")
            return {
                "status": "insufficient_data",
                "samples": len(y),
                "message": "Need at least 10 samples to train"
            }
        
        # Check class balance
        positive_ratio = y.sum() / len(y)
        logger.info(f"Positive class ratio: {positive_ratio:.2%}")
        
        if positive_ratio < 0.01:
            logger.warning("Very few positive samples - model may not be reliable")
        
        # Store feature names
        self.feature_names = list(X.columns)
        
        # Create LightGBM dataset
        train_data = lgb.Dataset(X, label=y)
        
        # Update params with iterations
        train_params = self.params.copy()
        train_params['num_iterations'] = num_iterations
        
        # Train model
        self.model = lgb.train(
            train_params,
            train_data,
            valid_sets=[train_data],
            valid_names=['train']
        )
        
        self.is_trained = True
        
        # Calculate training metrics
        train_pred = self.model.predict(X)
        train_accuracy = np.mean((train_pred >= 0.5) == y)
        
        # Feature importance
        importance = self.model.feature_importance(importance_type='gain')
        top_features = sorted(
            zip(self.feature_names, importance),
            key=lambda x: x[1],
            reverse=True
        )[:10]
        
        metrics = {
            "status": "success",
            "samples": len(y),
            "positive_samples": int(y.sum()),
            "negative_samples": int((y == 0).sum()),
            "positive_ratio": float(positive_ratio),
            "train_accuracy": float(train_accuracy),
            "num_features": len(self.feature_names),
            "top_features": [{"feature": f, "importance": float(imp)} for f, imp in top_features[:5]],
            "trained_at": datetime.now().isoformat()
        }
        
        logger.info(f"Training complete. Accuracy: {train_accuracy:.2%}")
        
        return metrics
    
    def predict(self, lookback_hours: int = 1) -> Dict:
        """
        Predict failure probability for the next hour based on recent metrics.
        
        Args:
            lookback_hours: Hours of recent data to analyze
            
        Returns:
            Prediction dictionary with probability and risk level
        """
        if not self.is_trained:
            return {
                "status": "error",
                "message": "Model not trained. Call train() first."
            }
        
        from sqlalchemy import text
        
        # Get recent metrics
        query = text("""
            SELECT timestamp, metric_name, value, service
            FROM metrics_history
            WHERE timestamp > NOW() - INTERVAL :hours HOUR
            ORDER BY timestamp DESC
            LIMIT 1000
        """)
        
        result = self.db.execute(query, {"hours": lookback_hours})
        metrics_data = result.fetchall()
        
        if not metrics_data:
            return {
                "status": "error",
                "message": "No recent metrics available"
            }
        
        # Convert to DataFrame
        metrics_df = pd.DataFrame(metrics_data, columns=['timestamp', 'metric_name', 'value', 'service'])
        
        # Extract features
        features_df = self._extract_features(metrics_df, lookback_hours)
        
        if features_df.empty:
            return {
                "status": "error",
                "message": "Could not extract features from metrics"
            }
        
        # Use most recent sample
        latest_features = features_df.iloc[-1:][self.feature_names]
        
        # Predict
        probability = float(self.model.predict(latest_features)[0])
        
        # Determine risk level
        if probability >= self.high_risk_threshold:
            risk_level = "high"
            message = "High risk of failure in the next hour"
        elif probability >= self.medium_risk_threshold:
            risk_level = "medium"
            message = "Moderate risk of failure in the next hour"
        else:
            risk_level = "low"
            message = "Low risk of failure in the next hour"
        
        # Get feature contributions (SHAP-like importance)
        feature_values = latest_features.iloc[0].to_dict()
        
        return {
            "status": "success",
            "probability": probability,
            "risk_level": risk_level,
            "message": message,
            "predicted_at": datetime.now().isoformat(),
            "lookback_hours": lookback_hours,
            "top_contributing_features": self._get_top_contributors(latest_features)
        }
    
    def _get_top_contributors(self, features_df: pd.DataFrame, top_n: int = 5) -> List[Dict]:
        """Get top contributing features for prediction."""
        if not self.is_trained:
            return []
        
        # Get feature importance from model
        importance = self.model.feature_importance(importance_type='gain')
        feature_importance = dict(zip(self.feature_names, importance))
        
        # Get feature values
        feature_values = features_df.iloc[0].to_dict()
        
        # Combine importance with current values
        contributors = []
        for feature in self.feature_names:
            if feature in feature_importance and feature in feature_values:
                contributors.append({
                    "feature": feature,
                    "value": float(feature_values[feature]),
                    "importance": float(feature_importance[feature])
                })
        
        # Sort by importance and return top N
        contributors.sort(key=lambda x: x['importance'], reverse=True)
        return contributors[:top_n]
    
    def predict_batch(self, hours_ahead: int = 24) -> List[Dict]:
        """
        Predict failure probabilities for multiple future time windows.
        
        Args:
            hours_ahead: How many hours ahead to predict (in 1-hour increments)
            
        Returns:
            List of predictions for each hour
        """
        if not self.is_trained:
            return [{
                "status": "error",
                "message": "Model not trained"
            }]
        
        predictions = []
        
        # For simplicity, we'll use current metrics and predict for each hour
        # In production, this would use forecasted metrics from Phase 3
        current_prediction = self.predict(lookback_hours=1)
        
        for hour in range(1, hours_ahead + 1):
            pred = current_prediction.copy()
            pred['hour_ahead'] = hour
            pred['predicted_for'] = (datetime.now() + timedelta(hours=hour)).isoformat()
            predictions.append(pred)
        
        return predictions
    
    def get_model_info(self) -> Dict:
        """Get information about the trained model."""
        if not self.is_trained:
            return {
                "status": "not_trained",
                "message": "Model has not been trained yet"
            }
        
        return {
            "status": "trained",
            "num_features": len(self.feature_names),
            "feature_names": self.feature_names[:20],  # First 20 features
            "model_type": "LightGBM",
            "params": self.params,
            "thresholds": {
                "high_risk": self.high_risk_threshold,
                "medium_risk": self.medium_risk_threshold
            }
        }
    
    def save_model(self, filepath: str):
        """Save the trained model to disk."""
        if not self.is_trained:
            raise ValueError("Cannot save untrained model")
        
        self.model.save_model(filepath)
        logger.info(f"Model saved to {filepath}")
    
    def load_model(self, filepath: str):
        """Load a trained model from disk."""
        self.model = lgb.Booster(model_file=filepath)
        self.is_trained = True
        logger.info(f"Model loaded from {filepath}")
