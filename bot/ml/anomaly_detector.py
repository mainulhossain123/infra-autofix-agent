"""
Isolation Forest Anomaly Detector

Real-time anomaly detection using Isolation Forest algorithm.
- Unsupervised learning (no labeled data required)
- Fast inference (< 10ms)
- Automatic threshold tuning
- Per-feature contribution analysis
"""

import numpy as np
import pandas as pd
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler
from datetime import datetime
import joblib
import json
import logging
from pathlib import Path
from typing import Dict, List, Optional, Tuple

from .feature_extractor import FeatureExtractor

logger = logging.getLogger(__name__)


class AnomalyDetector:
    """Isolation Forest-based anomaly detection"""
    
    def __init__(self, contamination: float = 0.05, n_estimators: int = 100, 
                 random_state: int = 42):
        """
        Initialize Anomaly Detector
        
        Args:
            contamination: Expected proportion of anomalies (0.01-0.15)
            n_estimators: Number of trees in forest
            random_state: Random seed for reproducibility
        """
        self.contamination = contamination
        self.n_estimators = n_estimators
        self.random_state = random_state
        
        self.model = IsolationForest(
            contamination=contamination,
            n_estimators=n_estimators,
            random_state=random_state,
            n_jobs=-1,  # Use all CPU cores
            warm_start=False
        )
        
        self.scaler = StandardScaler()
        self.feature_extractor = FeatureExtractor()
        
        self.is_trained = False
        self.training_stats = {}
        self.feature_names = []
        
    def train(self, df: pd.DataFrame) -> Dict:
        """
        Train the anomaly detector
        
        Args:
            df: DataFrame with metrics_history data (including 'label' column optional)
            
        Returns:
            Training statistics
        """
        logger.info(f"Training anomaly detector on {len(df)} samples...")
        
        # Extract features
        X, _ = self.feature_extractor.prepare_for_training(df)
        
        if len(X) < 100:
            raise ValueError(f"Need at least 100 samples for training, got {len(X)}")
        
        # Standardize features
        X_scaled = self.scaler.fit_transform(X)
        
        # Train Isolation Forest
        self.model.fit(X_scaled)
        
        # Calculate anomaly scores on training data
        scores = self.model.decision_function(X_scaled)
        predictions = self.model.predict(X_scaled)
        
        # Store feature names
        self.feature_names = self.feature_extractor.get_feature_importance_names()
        
        # Calculate statistics
        self.training_stats = {
            'samples': len(X),
            'features': X.shape[1],
            'contamination': self.contamination,
            'n_estimators': self.n_estimators,
            'score_mean': float(np.mean(scores)),
            'score_std': float(np.std(scores)),
            'score_min': float(np.min(scores)),
            'score_max': float(np.max(scores)),
            'anomalies_detected': int(np.sum(predictions == -1)),
            'normal_detected': int(np.sum(predictions == 1)),
            'trained_at': datetime.now().isoformat()
        }
        
        self.is_trained = True
        
        logger.info(f"Training complete: {self.training_stats['anomalies_detected']} anomalies detected in training data")
        
        return self.training_stats
    
    def predict(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Predict anomalies for new data
        
        Args:
            df: DataFrame with raw metrics
            
        Returns:
            DataFrame with predictions and scores
        """
        if not self.is_trained:
            raise ValueError("Model not trained. Call train() first.")
        
        # Extract features
        X = self.feature_extractor.prepare_for_prediction(df)
        
        if len(X) == 0:
            logger.warning("No data to predict")
            return pd.DataFrame()
        
        # Standardize
        X_scaled = self.scaler.transform(X)
        
        # Predict
        predictions = self.model.predict(X_scaled)
        scores = self.model.decision_function(X_scaled)
        
        # Create results DataFrame
        results = df.copy()
        results['anomaly_prediction'] = predictions
        results['anomaly_score'] = scores
        results['is_anomaly'] = (predictions == -1).astype(int)
        
        # Calculate anomaly severity (normalize scores to 0-100)
        results['anomaly_severity'] = self._calculate_severity(scores)
        
        logger.debug(f"Predicted {np.sum(predictions == -1)} anomalies out of {len(predictions)} samples")
        
        return results
    
    def predict_single(self, metrics: Dict) -> Dict:
        """
        Predict anomaly for a single metrics sample
        
        Args:
            metrics: Dictionary with metric values
            
        Returns:
            Prediction dictionary with score and severity
        """
        # Convert to DataFrame
        df = pd.DataFrame([metrics])
        
        # Predict
        results = self.predict(df)
        
        if results.empty:
            return {'error': 'Prediction failed'}
        
        result = results.iloc[0]
        
        return {
            'is_anomaly': bool(result['is_anomaly']),
            'anomaly_score': float(result['anomaly_score']),
            'anomaly_severity': float(result['anomaly_severity']),
            'prediction': 'anomaly' if result['is_anomaly'] else 'normal',
            'timestamp': metrics.get('timestamp', datetime.now().isoformat())
        }
    
    def get_feature_contributions(self, metrics: Dict) -> Dict[str, float]:
        """
        Calculate which features contribute most to anomaly score
        
        Args:
            metrics: Dictionary with metric values
            
        Returns:
            Dictionary of feature contributions
        """
        if not self.is_trained:
            raise ValueError("Model not trained")
        
        # Extract features
        df = pd.DataFrame([metrics])
        X = self.feature_extractor.prepare_for_prediction(df)
        X_scaled = self.scaler.transform(X)
        
        # Get path lengths for each tree
        # Lower path length = more anomalous
        path_lengths = np.zeros(len(self.feature_names))
        
        # Calculate feature importance by looking at splits
        # This is an approximation - Isolation Forest doesn't have built-in feature importance
        # We use the deviation from mean as a proxy
        X_mean = np.zeros(len(self.feature_names))
        
        for i, feature_name in enumerate(self.feature_names):
            # How much does this feature deviate from training mean?
            deviation = abs(X_scaled[0, i])
            path_lengths[i] = deviation
        
        # Normalize to sum to 1
        total = np.sum(path_lengths)
        if total > 0:
            contributions = path_lengths / total
        else:
            contributions = path_lengths
        
        # Get top contributing features
        contribution_dict = {
            self.feature_names[i]: float(contributions[i])
            for i in range(len(self.feature_names))
        }
        
        # Sort by contribution
        contribution_dict = dict(sorted(contribution_dict.items(), 
                                       key=lambda x: x[1], reverse=True))
        
        return contribution_dict
    
    def _calculate_severity(self, scores: np.ndarray) -> np.ndarray:
        """
        Calculate anomaly severity (0-100 scale)
        
        Args:
            scores: Anomaly scores from model
            
        Returns:
            Severity scores (0=normal, 100=severe anomaly)
        """
        # Scores are negative for anomalies
        # More negative = more anomalous
        
        # Normalize using training statistics
        mean_score = self.training_stats.get('score_mean', 0)
        std_score = self.training_stats.get('score_std', 1)
        
        # Z-score
        z_scores = (scores - mean_score) / (std_score + 1e-6)
        
        # Convert to 0-100 scale (inverted, so low scores = high severity)
        severity = np.clip(50 - (z_scores * 20), 0, 100)
        
        return severity
    
    def evaluate(self, df: pd.DataFrame) -> Dict:
        """
        Evaluate model performance on labeled data
        
        Args:
            df: DataFrame with 'label' column
            
        Returns:
            Evaluation metrics
        """
        if not self.is_trained:
            raise ValueError("Model not trained")
        
        if 'label' not in df.columns:
            raise ValueError("DataFrame must have 'label' column for evaluation")
        
        # Get predictions
        results = self.predict(df)
        
        # True labels (normal=0, anomaly=1)
        y_true = (df['label'] != 'normal').astype(int).values
        y_pred = results['is_anomaly'].values
        
        # Calculate metrics
        true_positives = np.sum((y_true == 1) & (y_pred == 1))
        false_positives = np.sum((y_true == 0) & (y_pred == 1))
        true_negatives = np.sum((y_true == 0) & (y_pred == 0))
        false_negatives = np.sum((y_true == 1) & (y_pred == 0))
        
        precision = true_positives / (true_positives + false_positives + 1e-6)
        recall = true_positives / (true_positives + false_negatives + 1e-6)
        f1_score = 2 * (precision * recall) / (precision + recall + 1e-6)
        accuracy = (true_positives + true_negatives) / len(y_true)
        
        metrics = {
            'accuracy': float(accuracy),
            'precision': float(precision),
            'recall': float(recall),
            'f1_score': float(f1_score),
            'true_positives': int(true_positives),
            'false_positives': int(false_positives),
            'true_negatives': int(true_negatives),
            'false_negatives': int(false_negatives),
            'total_samples': len(y_true),
            'total_anomalies': int(np.sum(y_true))
        }
        
        logger.info(f"Evaluation: Accuracy={accuracy:.3f}, Precision={precision:.3f}, "
                   f"Recall={recall:.3f}, F1={f1_score:.3f}")
        
        return metrics
    
    def save(self, filepath: str) -> None:
        """Save trained model to disk"""
        if not self.is_trained:
            raise ValueError("Cannot save untrained model")
        
        model_data = {
            'model': self.model,
            'scaler': self.scaler,
            'feature_extractor': self.feature_extractor,
            'training_stats': self.training_stats,
            'feature_names': self.feature_names,
            'contamination': self.contamination,
            'n_estimators': self.n_estimators
        }
        
        Path(filepath).parent.mkdir(parents=True, exist_ok=True)
        joblib.dump(model_data, filepath)
        
        logger.info(f"Model saved to {filepath}")
    
    @classmethod
    def load(cls, filepath: str) -> 'AnomalyDetector':
        """Load trained model from disk"""
        model_data = joblib.load(filepath)
        
        detector = cls(
            contamination=model_data['contamination'],
            n_estimators=model_data['n_estimators']
        )
        
        detector.model = model_data['model']
        detector.scaler = model_data['scaler']
        detector.feature_extractor = model_data['feature_extractor']
        detector.training_stats = model_data['training_stats']
        detector.feature_names = model_data['feature_names']
        detector.is_trained = True
        
        logger.info(f"Model loaded from {filepath}")
        
        return detector
    
    def get_model_info(self) -> Dict:
        """Get information about the trained model"""
        return {
            'is_trained': self.is_trained,
            'contamination': self.contamination,
            'n_estimators': self.n_estimators,
            'n_features': len(self.feature_names),
            'feature_names': self.feature_names[:10],  # First 10 features
            'training_stats': self.training_stats
        }
    
    def auto_tune_threshold(self, df: pd.DataFrame, target_fpr: float = 0.05) -> float:
        """
        Automatically tune anomaly threshold for target false positive rate
        
        Args:
            df: Validation DataFrame with labels
            target_fpr: Target false positive rate (0.01-0.10)
            
        Returns:
            Optimal threshold
        """
        if not self.is_trained:
            raise ValueError("Model not trained")
        
        # Get predictions
        results = self.predict(df)
        scores = results['anomaly_score'].values
        
        # True labels
        y_true = (df['label'] != 'normal').astype(int).values
        
        # Try different thresholds
        thresholds = np.percentile(scores, np.linspace(0, 100, 100))
        
        best_threshold = None
        best_diff = float('inf')
        
        for threshold in thresholds:
            y_pred = (scores < threshold).astype(int)
            
            false_positives = np.sum((y_true == 0) & (y_pred == 1))
            fpr = false_positives / np.sum(y_true == 0)
            
            diff = abs(fpr - target_fpr)
            if diff < best_diff:
                best_diff = diff
                best_threshold = threshold
        
        logger.info(f"Auto-tuned threshold: {best_threshold:.4f} (target FPR={target_fpr})")
        
        return float(best_threshold)


def create_default_detector() -> AnomalyDetector:
    """Create detector with default settings"""
    return AnomalyDetector(
        contamination=0.05,  # Expect 5% anomalies
        n_estimators=100,
        random_state=42
    )
