"""
Feature Extractor for ML Models

Transforms raw metrics into ML-ready features with:
- Rolling statistics (mean, std, min, max)
- Time-based features (hour, day of week, is_weekend)
- Lag features (previous 5, 10, 30 minutes)
- Rate of change calculations
- Anomaly indicators
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import logging

logger = logging.getLogger(__name__)


class FeatureExtractor:
    """Extract and engineer features from raw metrics for ML models"""
    
    def __init__(self):
        self.feature_columns = []
        self.scaler_params = {}
        
    def extract_features(self, df: pd.DataFrame, training: bool = False) -> pd.DataFrame:
        """
        Extract features from raw metrics DataFrame
        
        Args:
            df: DataFrame with columns from metrics_history table
            training: If True, fit scalers; if False, use existing scalers
            
        Returns:
            DataFrame with engineered features
        """
        if df.empty:
            return df
            
        df = df.copy()
        
        # Ensure timestamp is datetime
        if 'timestamp' in df.columns:
            df['timestamp'] = pd.to_datetime(df['timestamp'])
            df = df.sort_values('timestamp').reset_index(drop=True)
        
        # 1. Time-based features
        df = self._add_time_features(df)
        
        # 2. Rolling statistics
        df = self._add_rolling_features(df)
        
        # 3. Lag features
        df = self._add_lag_features(df)
        
        # 4. Rate of change (already in raw data, but recalculate for consistency)
        df = self._add_rate_features(df)
        
        # 5. Interaction features
        df = self._add_interaction_features(df)
        
        # 6. Anomaly indicators
        df = self._add_anomaly_indicators(df)
        
        # Drop rows with NaN from rolling/lag calculations
        df = df.dropna()
        
        # Store feature columns
        if training:
            self.feature_columns = self._get_feature_columns(df)
            logger.info(f"Extracted {len(self.feature_columns)} features for training")
        
        return df
    
    def _add_time_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Add time-based features"""
        if 'timestamp' not in df.columns:
            return df
            
        df['hour'] = df['timestamp'].dt.hour
        df['day_of_week'] = df['timestamp'].dt.dayofweek
        df['is_weekend'] = (df['day_of_week'] >= 5).astype(int)
        df['is_business_hours'] = ((df['hour'] >= 9) & (df['hour'] <= 17)).astype(int)
        
        # Cyclical encoding for hour (sine/cosine to preserve circular nature)
        df['hour_sin'] = np.sin(2 * np.pi * df['hour'] / 24)
        df['hour_cos'] = np.cos(2 * np.pi * df['hour'] / 24)
        
        # Cyclical encoding for day of week
        df['day_sin'] = np.sin(2 * np.pi * df['day_of_week'] / 7)
        df['day_cos'] = np.cos(2 * np.pi * df['day_of_week'] / 7)
        
        return df
    
    def _add_rolling_features(self, df: pd.DataFrame, windows: List[int] = [5, 10, 30]) -> pd.DataFrame:
        """Add rolling statistics for key metrics"""
        metrics = ['cpu_usage_percent', 'memory_usage_mb', 'error_rate', 
                   'response_time_p50', 'response_time_p95']
        
        for metric in metrics:
            if metric not in df.columns:
                continue
                
            for window in windows:
                # Rolling mean
                df[f'{metric}_rolling_mean_{window}'] = df[metric].rolling(window=window, min_periods=1).mean()
                
                # Rolling std
                df[f'{metric}_rolling_std_{window}'] = df[metric].rolling(window=window, min_periods=1).std()
                
                # Rolling min/max
                df[f'{metric}_rolling_min_{window}'] = df[metric].rolling(window=window, min_periods=1).min()
                df[f'{metric}_rolling_max_{window}'] = df[metric].rolling(window=window, min_periods=1).max()
                
                # Distance from rolling mean (z-score like)
                rolling_mean = df[f'{metric}_rolling_mean_{window}']
                rolling_std = df[f'{metric}_rolling_std_{window}']
                df[f'{metric}_zscore_{window}'] = (df[metric] - rolling_mean) / (rolling_std + 1e-6)
        
        return df
    
    def _add_lag_features(self, df: pd.DataFrame, lags: List[int] = [1, 5, 10, 30]) -> pd.DataFrame:
        """Add lagged values of key metrics"""
        metrics = ['cpu_usage_percent', 'memory_usage_mb', 'error_rate', 'response_time_p95']
        
        for metric in metrics:
            if metric not in df.columns:
                continue
                
            for lag in lags:
                df[f'{metric}_lag_{lag}'] = df[metric].shift(lag)
        
        return df
    
    def _add_rate_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Add rate of change features"""
        metrics = ['cpu_usage_percent', 'memory_usage_mb', 'error_rate', 'disk_usage_percent']
        
        for metric in metrics:
            if metric not in df.columns:
                continue
                
            # Simple difference
            df[f'{metric}_diff'] = df[metric].diff()
            
            # Percentage change
            df[f'{metric}_pct_change'] = df[metric].pct_change()
            
            # Acceleration (second derivative)
            df[f'{metric}_acceleration'] = df[f'{metric}_diff'].diff()
        
        return df
    
    def _add_interaction_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Add interaction features between metrics"""
        
        # CPU * Error Rate (high CPU with high errors is concerning)
        if 'cpu_usage_percent' in df.columns and 'error_rate' in df.columns:
            df['cpu_error_interaction'] = df['cpu_usage_percent'] * df['error_rate']
        
        # Memory * Response Time (memory pressure affecting latency)
        if 'memory_usage_mb' in df.columns and 'response_time_p95' in df.columns:
            df['memory_latency_interaction'] = df['memory_usage_mb'] * df['response_time_p95']
        
        # CPU + Memory combined load
        if 'cpu_usage_percent' in df.columns and 'memory_usage_percent' in df.columns:
            df['combined_load'] = (df['cpu_usage_percent'] + df['memory_usage_percent']) / 2
        
        # Error rate * Response time (errors with high latency)
        if 'error_rate' in df.columns and 'response_time_p95' in df.columns:
            df['error_latency_interaction'] = df['error_rate'] * df['response_time_p95']
        
        return df
    
    def _add_anomaly_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        """Add simple rule-based anomaly indicators"""
        
        # High CPU indicator
        if 'cpu_usage_percent' in df.columns:
            df['high_cpu_indicator'] = (df['cpu_usage_percent'] > 80).astype(int)
        
        # High memory indicator
        if 'memory_usage_percent' in df.columns:
            df['high_memory_indicator'] = (df['memory_usage_percent'] > 85).astype(int)
        
        # High error rate indicator
        if 'error_rate' in df.columns:
            df['high_error_indicator'] = (df['error_rate'] > 0.05).astype(int)
        
        # High latency indicator
        if 'response_time_p95' in df.columns:
            df['high_latency_indicator'] = (df['response_time_p95'] > 1000).astype(int)
        
        # Multiple issues at once (compound indicator)
        indicator_cols = [col for col in df.columns if col.endswith('_indicator')]
        if indicator_cols:
            df['multiple_issues_indicator'] = df[indicator_cols].sum(axis=1) >= 2
        
        return df
    
    def _get_feature_columns(self, df: pd.DataFrame) -> List[str]:
        """Get list of feature columns (exclude ID, timestamp, label)"""
        exclude = ['id', 'timestamp', 'label']
        return [col for col in df.columns if col not in exclude]
    
    def prepare_for_training(self, df: pd.DataFrame) -> Tuple[np.ndarray, np.ndarray]:
        """
        Prepare features and labels for training
        
        Args:
            df: DataFrame with extracted features and 'label' column
            
        Returns:
            X: Feature matrix (numpy array)
            y: Label vector (numpy array)
        """
        df_features = self.extract_features(df, training=True)
        
        if 'label' not in df_features.columns:
            raise ValueError("DataFrame must have 'label' column for training")
        
        # Encode labels: normal=0, anomaly=1
        label_map = {'normal': 0}
        y = df_features['label'].map(lambda x: label_map.get(x, 1)).values
        
        # Get feature matrix
        X = df_features[self.feature_columns].values
        
        logger.info(f"Training data prepared: X shape {X.shape}, y distribution: {np.bincount(y)}")
        
        return X, y
    
    def prepare_for_prediction(self, df: pd.DataFrame) -> np.ndarray:
        """
        Prepare features for prediction
        
        Args:
            df: DataFrame with raw metrics
            
        Returns:
            X: Feature matrix (numpy array)
        """
        if not self.feature_columns:
            raise ValueError("Must call prepare_for_training first to define feature columns")
        
        df_features = self.extract_features(df, training=False)
        
        # Ensure all required features exist
        missing_features = set(self.feature_columns) - set(df_features.columns)
        if missing_features:
            logger.warning(f"Missing features: {missing_features}. Filling with zeros.")
            for feature in missing_features:
                df_features[feature] = 0
        
        X = df_features[self.feature_columns].values
        
        return X
    
    def get_feature_importance_names(self) -> List[str]:
        """Get names of feature columns for importance analysis"""
        return self.feature_columns.copy()
    
    def get_feature_stats(self, df: pd.DataFrame) -> Dict:
        """Get statistics about extracted features"""
        df_features = self.extract_features(df, training=False)
        
        stats = {
            'total_samples': len(df_features),
            'total_features': len(self.feature_columns),
            'feature_groups': {
                'time_features': len([c for c in df_features.columns if 'hour' in c or 'day' in c or 'weekend' in c]),
                'rolling_features': len([c for c in df_features.columns if 'rolling' in c]),
                'lag_features': len([c for c in df_features.columns if 'lag' in c]),
                'rate_features': len([c for c in df_features.columns if 'diff' in c or 'pct_change' in c]),
                'interaction_features': len([c for c in df_features.columns if 'interaction' in c]),
                'indicator_features': len([c for c in df_features.columns if 'indicator' in c])
            }
        }
        
        return stats


def extract_recent_window(df: pd.DataFrame, window_minutes: int = 60) -> pd.DataFrame:
    """
    Extract recent window of data for prediction
    
    Args:
        df: DataFrame with timestamp column
        window_minutes: Number of minutes to look back
        
    Returns:
        DataFrame with recent data
    """
    if df.empty or 'timestamp' not in df.columns:
        return df
    
    df = df.copy()
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    
    cutoff_time = df['timestamp'].max() - timedelta(minutes=window_minutes)
    recent_df = df[df['timestamp'] >= cutoff_time].copy()
    
    logger.debug(f"Extracted {len(recent_df)} samples from last {window_minutes} minutes")
    
    return recent_df


def split_train_test(df: pd.DataFrame, test_size: float = 0.2, 
                     temporal: bool = True) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """
    Split data into train and test sets
    
    Args:
        df: DataFrame to split
        test_size: Proportion of data for testing
        temporal: If True, use temporal split (test is most recent data)
                 If False, random split
        
    Returns:
        train_df, test_df
    """
    if temporal and 'timestamp' in df.columns:
        df = df.sort_values('timestamp')
        split_idx = int(len(df) * (1 - test_size))
        train_df = df.iloc[:split_idx].copy()
        test_df = df.iloc[split_idx:].copy()
    else:
        # Random split
        test_df = df.sample(frac=test_size, random_state=42)
        train_df = df.drop(test_df.index)
    
    logger.info(f"Split data: train={len(train_df)}, test={len(test_df)}")
    
    return train_df, test_df
