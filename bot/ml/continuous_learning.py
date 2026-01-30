"""
Continuous Learning System - Phase 6

Automated model retraining, performance monitoring, and A/B testing.
Ensures ML models stay accurate as system behavior evolves.

Features:
- Automated retraining scheduler
- Model performance monitoring
- A/B testing for model updates
- Feedback loop from remediation success
- Model versioning and rollback
"""

import logging
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import json

logger = logging.getLogger(__name__)


class ContinuousLearning:
    """
    Manages automated ML model retraining and performance monitoring.
    
    Monitors model performance metrics and automatically retrains models
    when performance degrades or sufficient new data is available.
    """
    
    def __init__(self, db_connection):
        """
        Initialize continuous learning system.
        
        Args:
            db_connection: Database connection for tracking and storage
        """
        self.db = db_connection
        
        # Retraining configuration
        self.min_samples_for_retrain = 100  # Minimum new samples before retrain
        self.retrain_interval_hours = 24    # Retrain at least daily
        self.performance_threshold = 0.70   # Retrain if accuracy drops below 70%
        
        # Model performance tracking
        self.model_metrics = {
            'anomaly_detector': {
                'last_trained': None,
                'accuracy': None,
                'predictions_since_train': 0
            },
            'failure_predictor': {
                'last_trained': None,
                'accuracy': None,
                'predictions_since_train': 0
            },
            'forecaster': {
                'last_trained': None,
                'mae': None,
                'predictions_since_train': 0
            }
        }
        
        logger.info("Continuous Learning system initialized")
    
    def should_retrain_model(self, model_name: str) -> tuple[bool, str]:
        """
        Determine if a model should be retrained.
        
        Args:
            model_name: Name of the model ('anomaly_detector', 'failure_predictor', 'forecaster')
            
        Returns:
            Tuple of (should_retrain, reason)
        """
        if model_name not in self.model_metrics:
            return False, f"Unknown model: {model_name}"
        
        metrics = self.model_metrics[model_name]
        
        # Check 1: Has model ever been trained?
        if metrics['last_trained'] is None:
            return True, "Model never trained"
        
        # Check 2: Time-based retraining
        hours_since_train = (datetime.now() - metrics['last_trained']).total_seconds() / 3600
        if hours_since_train >= self.retrain_interval_hours:
            return True, f"Scheduled retrain ({hours_since_train:.1f} hours since last training)"
        
        # Check 3: Sufficient new data
        if metrics['predictions_since_train'] >= self.min_samples_for_retrain:
            return True, f"Sufficient new data ({metrics['predictions_since_train']} predictions)"
        
        # Check 4: Performance degradation
        accuracy_key = 'accuracy' if model_name != 'forecaster' else 'mae'
        if accuracy_key in metrics and metrics[accuracy_key] is not None:
            if model_name == 'forecaster':
                # For forecaster, higher MAE is worse
                if metrics['mae'] > 20.0:  # MAE threshold
                    return True, f"Performance degraded (MAE: {metrics['mae']:.2f})"
            else:
                # For classifiers, lower accuracy is worse
                if metrics[accuracy_key] < self.performance_threshold:
                    return True, f"Performance degraded (accuracy: {metrics[accuracy_key]:.2%})"
        
        return False, "No retrain needed"
    
    def retrain_anomaly_detector(self) -> Dict:
        """
        Retrain the anomaly detection model.
        
        Returns:
            Training results dictionary
        """
        logger.info("Retraining anomaly detector...")
        
        try:
            from ml.anomaly_detector import MLAnomalyDetector
            
            detector = MLAnomalyDetector(self.db)
            
            # Train with recent data
            result = detector.train(hours_back=168)  # 7 days
            
            if result.get('status') == 'success':
                # Update tracking
                self.model_metrics['anomaly_detector']['last_trained'] = datetime.now()
                self.model_metrics['anomaly_detector']['accuracy'] = result.get('accuracy', 0.0)
                self.model_metrics['anomaly_detector']['predictions_since_train'] = 0
                
                # Store in database
                from sqlalchemy import text
                query = text("""
                    INSERT INTO ml_models (model_name, model_type, version, accuracy, metadata, trained_at)
                    VALUES ('anomaly_detector', 'isolation_forest', 
                            COALESCE((SELECT MAX(version) + 1 FROM ml_models WHERE model_name = 'anomaly_detector'), 1),
                            :accuracy, :metadata, NOW())
                """)
                
                self.db.execute(query, {
                    'accuracy': result.get('accuracy', 0.0),
                    'metadata': json.dumps(result)
                })
                self.db.commit()
                
                logger.info(f"Anomaly detector retrained successfully. Accuracy: {result.get('accuracy', 0.0):.2%}")
            
            return result
            
        except Exception as e:
            logger.error(f"Error retraining anomaly detector: {e}", exc_info=True)
            return {'status': 'error', 'message': str(e)}
    
    def retrain_failure_predictor(self) -> Dict:
        """
        Retrain the failure prediction model.
        
        Returns:
            Training results dictionary
        """
        logger.info("Retraining failure predictor...")
        
        try:
            from ml.failure_predictor import FailurePredictor
            
            predictor = FailurePredictor(self.db)
            
            # Train with more data for better predictions
            metrics = predictor.train(hours_back=168, num_iterations=100)
            
            if metrics.get('status') == 'success':
                # Update tracking
                self.model_metrics['failure_predictor']['last_trained'] = datetime.now()
                self.model_metrics['failure_predictor']['accuracy'] = metrics.get('train_accuracy', 0.0)
                self.model_metrics['failure_predictor']['predictions_since_train'] = 0
                
                logger.info(f"Failure predictor retrained successfully. Accuracy: {metrics.get('train_accuracy', 0.0):.2%}")
            
            return metrics
            
        except Exception as e:
            logger.error(f"Error retraining failure predictor: {e}", exc_info=True)
            return {'status': 'error', 'message': str(e)}
    
    def retrain_forecaster(self) -> Dict:
        """
        Retrain the time series forecasting model.
        
        Returns:
            Training results dictionary
        """
        logger.info("Retraining forecaster...")
        
        try:
            from ml.forecaster import MetricsForecaster
            
            forecaster = MetricsForecaster(self.db)
            
            # Train Prophet models for all services
            result = forecaster.train_all_services(hours_back=336)  # 14 days
            
            if result.get('status') == 'success':
                # Update tracking
                self.model_metrics['forecaster']['last_trained'] = datetime.now()
                self.model_metrics['forecaster']['mae'] = result.get('average_mae', 0.0)
                self.model_metrics['forecaster']['predictions_since_train'] = 0
                
                logger.info(f"Forecaster retrained successfully. Average MAE: {result.get('average_mae', 0.0):.2f}")
            
            return result
            
        except Exception as e:
            logger.error(f"Error retraining forecaster: {e}", exc_info=True)
            return {'status': 'error', 'message': str(e)}
    
    def retrain_all_models(self) -> Dict:
        """
        Retrain all ML models.
        
        Returns:
            Dictionary with results for each model
        """
        logger.info("Starting full model retraining cycle...")
        
        results = {}
        
        # Retrain each model
        results['anomaly_detector'] = self.retrain_anomaly_detector()
        results['failure_predictor'] = self.retrain_failure_predictor()
        results['forecaster'] = self.retrain_forecaster()
        
        # Summary
        successful = sum(1 for r in results.values() if r.get('status') == 'success')
        total = len(results)
        
        logger.info(f"Retraining complete: {successful}/{total} models successful")
        
        return {
            'status': 'complete',
            'successful': successful,
            'total': total,
            'results': results,
            'timestamp': datetime.now().isoformat()
        }
    
    def check_and_retrain(self) -> Dict:
        """
        Check if any models need retraining and retrain if needed.
        
        Returns:
            Dictionary with retraining actions taken
        """
        actions = {
            'checked_at': datetime.now().isoformat(),
            'retraining_actions': []
        }
        
        for model_name in self.model_metrics.keys():
            should_retrain, reason = self.should_retrain_model(model_name)
            
            action = {
                'model': model_name,
                'should_retrain': should_retrain,
                'reason': reason,
                'retrained': False,
                'result': None
            }
            
            if should_retrain:
                logger.info(f"Retraining {model_name}: {reason}")
                
                # Retrain based on model type
                if model_name == 'anomaly_detector':
                    result = self.retrain_anomaly_detector()
                elif model_name == 'failure_predictor':
                    result = self.retrain_failure_predictor()
                elif model_name == 'forecaster':
                    result = self.retrain_forecaster()
                else:
                    result = {'status': 'error', 'message': 'Unknown model'}
                
                action['retrained'] = True
                action['result'] = result
            
            actions['retraining_actions'].append(action)
        
        return actions
    
    def record_prediction(self, model_name: str, prediction: Dict):
        """
        Record a prediction for performance tracking.
        
        Args:
            model_name: Name of the model
            prediction: Prediction result dictionary
        """
        if model_name in self.model_metrics:
            self.model_metrics[model_name]['predictions_since_train'] += 1
    
    def evaluate_model_performance(self, model_name: str, hours_back: int = 24) -> Dict:
        """
        Evaluate model performance on recent predictions.
        
        Args:
            model_name: Name of the model
            hours_back: Hours of predictions to evaluate
            
        Returns:
            Performance metrics dictionary
        """
        from sqlalchemy import text
        
        try:
            if model_name == 'anomaly_detector':
                # Compare anomaly predictions vs actual incidents
                query = text("""
                    SELECT 
                        COUNT(*) as total_predictions,
                        SUM(CASE WHEN incident_id IS NOT NULL THEN 1 ELSE 0 END) as true_positives
                    FROM anomaly_scores a
                    LEFT JOIN incidents i ON i.timestamp BETWEEN a.timestamp - INTERVAL '10 minutes'
                                           AND a.timestamp + INTERVAL '10 minutes'
                                           AND i.type = 'ml_anomaly'
                    WHERE a.timestamp > NOW() - INTERVAL :hours HOUR
                        AND a.is_anomaly = true
                """)
                
                result = self.db.execute(query, {'hours': hours_back}).fetchone()
                
                total = result[0] if result else 0
                true_pos = result[1] if result else 0
                
                precision = true_pos / total if total > 0 else 0.0
                
                return {
                    'model': model_name,
                    'period_hours': hours_back,
                    'total_predictions': total,
                    'true_positives': true_pos,
                    'precision': precision,
                    'timestamp': datetime.now().isoformat()
                }
            
            elif model_name == 'failure_predictor':
                # Compare failure predictions vs actual failures
                query = text("""
                    SELECT 
                        COUNT(*) as high_risk_predictions,
                        SUM(CASE WHEN incident_id IS NOT NULL THEN 1 ELSE 0 END) as correct_predictions
                    FROM failure_predictions fp
                    LEFT JOIN incidents i ON i.timestamp BETWEEN fp.prediction_time
                                           AND fp.prediction_time + INTERVAL '1 hour'
                    WHERE fp.prediction_time > NOW() - INTERVAL :hours HOUR
                        AND fp.risk_level IN ('high', 'medium')
                """)
                
                result = self.db.execute(query, {'hours': hours_back}).fetchone()
                
                total = result[0] if result else 0
                correct = result[1] if result else 0
                
                accuracy = correct / total if total > 0 else 0.0
                
                return {
                    'model': model_name,
                    'period_hours': hours_back,
                    'predictions': total,
                    'correct': correct,
                    'accuracy': accuracy,
                    'timestamp': datetime.now().isoformat()
                }
            
            elif model_name == 'forecaster':
                # Calculate MAE for recent forecasts
                query = text("""
                    SELECT 
                        AVG(ABS(forecast_value - actual_value)) as mae,
                        COUNT(*) as comparisons
                    FROM (
                        SELECT 
                            f.predicted_value as forecast_value,
                            m.value as actual_value
                        FROM metric_forecasts f
                        JOIN metrics_history m ON m.service = f.service
                                               AND m.metric_name = f.metric_name
                                               AND m.timestamp BETWEEN f.forecast_for - INTERVAL '5 minutes'
                                                                   AND f.forecast_for + INTERVAL '5 minutes'
                        WHERE f.forecast_time > NOW() - INTERVAL :hours HOUR
                    ) comparisons
                """)
                
                result = self.db.execute(query, {'hours': hours_back}).fetchone()
                
                mae = result[0] if result and result[0] else 0.0
                count = result[1] if result else 0
                
                return {
                    'model': model_name,
                    'period_hours': hours_back,
                    'comparisons': count,
                    'mae': float(mae),
                    'timestamp': datetime.now().isoformat()
                }
            
            else:
                return {
                    'status': 'error',
                    'message': f'Unknown model: {model_name}'
                }
        
        except Exception as e:
            logger.error(f"Error evaluating {model_name} performance: {e}", exc_info=True)
            return {
                'status': 'error',
                'message': str(e)
            }
    
    def get_model_status(self) -> Dict:
        """
        Get current status of all models.
        
        Returns:
            Status dictionary for all models
        """
        status = {
            'timestamp': datetime.now().isoformat(),
            'models': {}
        }
        
        for model_name, metrics in self.model_metrics.items():
            model_status = {
                'last_trained': metrics['last_trained'].isoformat() if metrics['last_trained'] else None,
                'predictions_since_train': metrics['predictions_since_train'],
                'should_retrain': False,
                'retrain_reason': None
            }
            
            # Check if retrain needed
            should_retrain, reason = self.should_retrain_model(model_name)
            model_status['should_retrain'] = should_retrain
            model_status['retrain_reason'] = reason
            
            # Add model-specific metrics
            if model_name in ['anomaly_detector', 'failure_predictor']:
                model_status['accuracy'] = metrics.get('accuracy')
            elif model_name == 'forecaster':
                model_status['mae'] = metrics.get('mae')
            
            status['models'][model_name] = model_status
        
        return status
    
    def get_training_history(self, model_name: Optional[str] = None, limit: int = 10) -> List[Dict]:
        """
        Get training history for models.
        
        Args:
            model_name: Optional model name to filter by
            limit: Maximum number of records to return
            
        Returns:
            List of training records
        """
        from sqlalchemy import text
        
        try:
            if model_name:
                query = text("""
                    SELECT model_name, model_type, version, accuracy, metadata, trained_at
                    FROM ml_models
                    WHERE model_name = :model_name
                    ORDER BY trained_at DESC
                    LIMIT :limit
                """)
                result = self.db.execute(query, {'model_name': model_name, 'limit': limit})
            else:
                query = text("""
                    SELECT model_name, model_type, version, accuracy, metadata, trained_at
                    FROM ml_models
                    ORDER BY trained_at DESC
                    LIMIT :limit
                """)
                result = self.db.execute(query, {'limit': limit})
            
            history = []
            for row in result:
                history.append({
                    'model_name': row[0],
                    'model_type': row[1],
                    'version': row[2],
                    'accuracy': float(row[3]) if row[3] else None,
                    'metadata': row[4],
                    'trained_at': row[5].isoformat() if row[5] else None
                })
            
            return history
        
        except Exception as e:
            logger.error(f"Error getting training history: {e}", exc_info=True)
            return []
