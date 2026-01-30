"""
ML API Endpoints for Auto-Remediation Platform

Provides REST API endpoints for:
- Metrics export/import
- Model training/retraining
- Anomaly detection
- Forecasting
- Failure prediction
- Model management
"""

import logging
from flask import Blueprint, jsonify, request
from datetime import datetime, timedelta
from sqlalchemy import desc
import pandas as pd

from models import get_db_session, text

logger = logging.getLogger(__name__)

# Create blueprint for ML routes
ml_bp = Blueprint('ml', __name__, url_prefix='/api/ml')


# ==================== Metrics & Data Endpoints ====================

@ml_bp.route('/metrics/export', methods=['GET'])
def export_metrics():
    """
    Export metrics data for external analysis.
    Query params:
        - start_date: ISO format datetime (default: 30 days ago)
        - end_date: ISO format datetime (default: now)
        - format: csv or json (default: json)
    """
    try:
        # Get query parameters
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        format_type = request.args.get('format', 'json')
        
        # Default to last 30 days
        if not start_date:
            start_date = (datetime.utcnow() - timedelta(days=30)).isoformat()
        if not end_date:
            end_date = datetime.utcnow().isoformat()
        
        db = get_db_session()
        try:
            result = db.execute(text("""
                SELECT 
                    timestamp,
                    cpu_percent,
                    memory_percent,
                    error_rate,
                    response_time_p50,
                    response_time_p95,
                    response_time_p99,
                    request_count,
                    error_count,
                    active_connections
                FROM metrics_history
                WHERE timestamp BETWEEN :start_date AND :end_date
                ORDER BY timestamp ASC
            """), {'start_date': start_date, 'end_date': end_date})
            
            metrics = []
            for row in result:
                metrics.append({
                    'timestamp': row[0].isoformat() if row[0] else None,
                    'cpu_percent': row[1],
                    'memory_percent': row[2],
                    'error_rate': row[3],
                    'response_time_p50': row[4],
                    'response_time_p95': row[5],
                    'response_time_p99': row[6],
                    'request_count': row[7],
                    'error_count': row[8],
                    'active_connections': row[9]
                })
            
            if format_type == 'csv':
                # Convert to CSV
                df = pd.DataFrame(metrics)
                csv_data = df.to_csv(index=False)
                return csv_data, 200, {'Content-Type': 'text/csv',
                                       'Content-Disposition': 'attachment; filename=metrics.csv'}
            
            return jsonify({
                'count': len(metrics),
                'start_date': start_date,
                'end_date': end_date,
                'metrics': metrics
            })
        finally:
            db.close()
            
    except Exception as e:
        logger.error(f"Error exporting metrics: {e}", exc_info=True)
        return jsonify({'error': str(e)}), 500


@ml_bp.route('/metrics/stats', methods=['GET'])
def metrics_stats():
    """
    Get statistical summary of collected metrics.
    """
    try:
        db = get_db_session()
        try:
            result = db.execute(text("""
                SELECT 
                    COUNT(*) as total_samples,
                    MIN(timestamp) as first_sample,
                    MAX(timestamp) as last_sample,
                    AVG(cpu_percent) as avg_cpu,
                    AVG(memory_percent) as avg_memory,
                    AVG(error_rate) as avg_error_rate,
                    STDDEV(cpu_percent) as std_cpu,
                    STDDEV(memory_percent) as std_memory
                FROM metrics_history
            """))
            
            row = result.fetchone()
            
            return jsonify({
                'total_samples': row[0],
                'first_sample': row[1].isoformat() if row[1] else None,
                'last_sample': row[2].isoformat() if row[2] else None,
                'data_duration_hours': (row[2] - row[1]).total_seconds() / 3600 if row[1] and row[2] else 0,
                'averages': {
                    'cpu_percent': round(float(row[3]) if row[3] else 0, 2),
                    'memory_percent': round(float(row[4]) if row[4] else 0, 2),
                    'error_rate': round(float(row[5]) if row[5] else 0, 4)
                },
                'std_deviation': {
                    'cpu_percent': round(float(row[6]) if row[6] else 0, 2),
                    'memory_percent': round(float(row[7]) if row[7] else 0, 2)
                }
            })
        finally:
            db.close()
            
    except Exception as e:
        logger.error(f"Error getting metrics stats: {e}", exc_info=True)
        return jsonify({'error': str(e)}), 500


# ==================== Model Management Endpoints ====================

@ml_bp.route('/models', methods=['GET'])
def list_models():
    """
    List all ML models with their versions and status.
    Query params:
        - active_only: true/false (default: false)
    """
    try:
        active_only = request.args.get('active_only', 'false').lower() == 'true'
        
        db = get_db_session()
        try:
            query = """
                SELECT 
                    id,
                    model_name,
                    model_type,
                    version,
                    trained_at,
                    is_active,
                    metrics,
                    training_samples_count
                FROM ml_models
            """
            
            if active_only:
                query += " WHERE is_active = TRUE"
            
            query += " ORDER BY trained_at DESC"
            
            result = db.execute(text(query))
            
            models = []
            for row in result:
                models.append({
                    'id': row[0],
                    'model_name': row[1],
                    'model_type': row[2],
                    'version': row[3],
                    'trained_at': row[4].isoformat() if row[4] else None,
                    'is_active': row[5],
                    'performance_metrics': row[6],
                    'training_samples': row[7]
                })
            
            return jsonify({
                'count': len(models),
                'models': models
            })
        finally:
            db.close()
            
    except Exception as e:
        logger.error(f"Error listing models: {e}", exc_info=True)
        return jsonify({'error': str(e)}), 500


@ml_bp.route('/models/<int:model_id>', methods=['GET'])
def get_model_details(model_id):
    """Get detailed information about a specific model."""
    try:
        db = get_db_session()
        try:
            result = db.execute(text("""
                SELECT 
                    id,
                    model_name,
                    model_type,
                    version,
                    trained_at,
                    training_data_start,
                    training_data_end,
                    training_samples_count,
                    metrics,
                    file_path,
                    is_active,
                    deployed_at,
                    training_config,
                    notes
                FROM ml_models
                WHERE id = :model_id
            """), {'model_id': model_id})
            
            row = result.fetchone()
            
            if not row:
                return jsonify({'error': 'Model not found'}), 404
            
            return jsonify({
                'id': row[0],
                'model_name': row[1],
                'model_type': row[2],
                'version': row[3],
                'trained_at': row[4].isoformat() if row[4] else None,
                'training_data_start': row[5].isoformat() if row[5] else None,
                'training_data_end': row[6].isoformat() if row[6] else None,
                'training_samples_count': row[7],
                'performance_metrics': row[8],
                'file_path': row[9],
                'is_active': row[10],
                'deployed_at': row[11].isoformat() if row[11] else None,
                'training_config': row[12],
                'notes': row[13]
            })
        finally:
            db.close()
            
    except Exception as e:
        logger.error(f"Error getting model details: {e}", exc_info=True)
        return jsonify({'error': str(e)}), 500


# ==================== Training Endpoints ====================

@ml_bp.route('/train/generate-synthetic', methods=['POST'])
def generate_synthetic_data():
    """
    Generate synthetic training data.
    Request body:
        - days: number of days (default: 30)
        - seed: random seed (default: 42)
    """
    try:
        data = request.get_json() or {}
        days = data.get('days', 30)
        seed = data.get('seed', 42)
        
        # Import generator (delayed to avoid circular imports)
        from ml.synthetic_data_generator import SyntheticDataGenerator
        
        generator = SyntheticDataGenerator(random_seed=seed)
        synthetic_data = generator.generate_full_training_set(normal_days=days)
        
        # Save to database
        db = get_db_session()
        try:
            # Convert DataFrame to dict records and insert
            for _, row in synthetic_data.iterrows():
                db.execute(text("""
                    INSERT INTO metrics_history (
                        timestamp, cpu_percent, memory_percent, memory_mb,
                        disk_usage_percent, request_count, error_count, error_rate,
                        active_connections, response_time_p50, response_time_p95,
                        response_time_p99, response_time_avg, cpu_rate_of_change,
                        memory_rate_of_change, error_rate_trend
                    ) VALUES (
                        :timestamp, :cpu_percent, :memory_percent, :memory_mb,
                        :disk_usage_percent, :request_count, :error_count, :error_rate,
                        :active_connections, :response_time_p50, :response_time_p95,
                        :response_time_p99, :response_time_avg, :cpu_rate_of_change,
                        :memory_rate_of_change, :error_rate_trend
                    )
                """), {
                    'timestamp': row['timestamp'],
                    'cpu_percent': row['cpu_percent'],
                    'memory_percent': row['memory_percent'],
                    'memory_mb': row['memory_mb'],
                    'disk_usage_percent': row['disk_usage_percent'],
                    'request_count': row['request_count'],
                    'error_count': row['error_count'],
                    'error_rate': row['error_rate'],
                    'active_connections': row['active_connections'],
                    'response_time_p50': row['response_time_p50'],
                    'response_time_p95': row['response_time_p95'],
                    'response_time_p99': row['response_time_p99'],
                    'response_time_avg': row['response_time_avg'],
                    'cpu_rate_of_change': row.get('cpu_rate_of_change', 0),
                    'memory_rate_of_change': row.get('memory_rate_of_change', 0),
                    'error_rate_trend': row.get('error_rate_trend', 0)
                })
            
            db.commit()
            
            return jsonify({
                'success': True,
                'message': f'Generated and stored {len(synthetic_data)} synthetic samples',
                'samples_count': len(synthetic_data),
                'label_distribution': synthetic_data['label'].value_counts().to_dict()
            })
        finally:
            db.close()
            
    except Exception as e:
        logger.error(f"Error generating synthetic data: {e}", exc_info=True)
        return jsonify({'error': str(e)}), 500


# ==================== ML Training & Prediction Endpoints ====================

@ml_bp.route('/train/anomaly-detector', methods=['POST'])
def train_anomaly_detector():
    """
    Train Isolation Forest anomaly detector on collected metrics.
    Request body:
        - contamination: Expected anomaly proportion (0.01-0.15, default: 0.05)
        - n_estimators: Number of trees (default: 100)
        - use_synthetic: Whether to include synthetic data (default: true)
    """
    try:
        # Import ML modules
        try:
            from bot.ml.anomaly_detector import AnomalyDetector
            from bot.ml.feature_extractor import split_train_test
        except ImportError as e:
            return jsonify({
                'status': 'error',
                'message': f'ML dependencies not installed: {e}'
            }), 500
        
        # Get request parameters
        data = request.get_json() or {}
        contamination = data.get('contamination', 0.05)
        n_estimators = data.get('n_estimators', 100)
        use_synthetic = data.get('use_synthetic', True)
        
        # Validate parameters
        if not (0.01 <= contamination <= 0.15):
            return jsonify({'error': 'contamination must be between 0.01 and 0.15'}), 400
        
        db = get_db_session()
        try:
            # Load training data
            query = "SELECT * FROM metrics_history ORDER BY timestamp"
            if not use_synthetic:
                query += " WHERE label = 'normal'"
            
            result = db.execute(text(query))
            rows = result.fetchall()
            columns = result.keys()
            
            if len(rows) < 1000:
                return jsonify({
                    'status': 'error',
                    'message': f'Need at least 1000 samples for training, got {len(rows)}. Generate synthetic data first.'
                }), 400
            
            # Convert to DataFrame
            df = pd.DataFrame(rows, columns=columns)
            
            logger.info(f"Training anomaly detector on {len(df)} samples...")
            
            # Split train/test
            train_df, test_df = split_train_test(df, test_size=0.2, temporal=True)
            
            # Train model
            detector = AnomalyDetector(
                contamination=contamination,
                n_estimators=n_estimators
            )
            
            training_stats = detector.train(train_df)
            
            # Evaluate on test set
            eval_metrics = detector.evaluate(test_df)
            
            # Save model
            model_path = '/app/data/models/anomaly_detector_latest.joblib'
            detector.save(model_path)
            
            # Save model metadata to database
            db.execute(text("""
                INSERT INTO ml_models (name, version, model_type, status, performance_metrics, 
                                      training_samples, trained_at, file_path, is_active)
                VALUES (:name, :version, :model_type, :status, :performance_metrics,
                       :training_samples, :trained_at, :file_path, :is_active)
            """), {
                'name': 'anomaly_detector',
                'version': datetime.now().strftime('%Y%m%d_%H%M%S'),
                'model_type': 'isolation_forest',
                'status': 'active',
                'performance_metrics': str(eval_metrics),
                'training_samples': len(train_df),
                'trained_at': datetime.now(),
                'file_path': model_path,
                'is_active': True
            })
            db.commit()
            
            return jsonify({
                'status': 'success',
                'message': 'Anomaly detector trained successfully',
                'training_stats': training_stats,
                'evaluation': eval_metrics,
                'model_path': model_path
            })
            
        finally:
            db.close()
            
    except Exception as e:
        logger.error(f"Error training anomaly detector: {e}", exc_info=True)
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500


@ml_bp.route('/predict/anomaly', methods=['POST'])
def predict_anomaly():
    """
    Predict if current metrics indicate an anomaly.
    Request body: Dictionary with current metric values
    """
    try:
        from bot.ml.anomaly_detector import AnomalyDetector
        
        # Load latest model
        model_path = '/app/data/models/anomaly_detector_latest.joblib'
        
        try:
            detector = AnomalyDetector.load(model_path)
        except FileNotFoundError:
            return jsonify({
                'status': 'error',
                'message': 'No trained model found. Train a model first using /api/ml/train/anomaly-detector'
            }), 404
        
        # Get metrics from request
        metrics = request.get_json()
        if not metrics:
            return jsonify({'error': 'No metrics provided in request body'}), 400
        
        # Predict
        prediction = detector.predict_single(metrics)
        
        # Get feature contributions
        contributions = detector.get_feature_contributions(metrics)
        top_contributors = dict(list(contributions.items())[:5])
        
        # Store prediction in database
        db = get_db_session()
        try:
            db.execute(text("""
                INSERT INTO anomaly_scores (timestamp, anomaly_score, is_anomaly, severity,
                                           contributing_features, model_version)
                VALUES (:timestamp, :score, :is_anomaly, :severity, :features, :version)
            """), {
                'timestamp': datetime.now(),
                'score': prediction['anomaly_score'],
                'is_anomaly': prediction['is_anomaly'],
                'severity': prediction['anomaly_severity'],
                'features': str(top_contributors),
                'version': 'latest'
            })
            db.commit()
        finally:
            db.close()
        
        return jsonify({
            'status': 'success',
            'prediction': prediction,
            'top_contributing_features': top_contributors
        })
        
    except Exception as e:
        logger.error(f"Error predicting anomaly: {e}", exc_info=True)
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500


@ml_bp.route('/anomaly-scores', methods=['GET'])
def get_anomaly_scores():
    """
    Get recent anomaly scores.
    Query params:
        - limit: Number of recent scores to return (default: 100)
        - threshold: Filter scores above this threshold (default: all)
    """
    try:
        limit = int(request.args.get('limit', 100))
        threshold = request.args.get('threshold')
        
        db = get_db_session()
        try:
            query = """
                SELECT id, timestamp, anomaly_score, is_anomaly, severity,
                       contributing_features, model_version
                FROM anomaly_scores
                ORDER BY timestamp DESC
                LIMIT :limit
            """
            
            result = db.execute(text(query), {'limit': limit})
            rows = result.fetchall()
            columns = result.keys()
            
            scores = []
            for row in rows:
                score_dict = dict(zip(columns, row))
                score_dict['timestamp'] = score_dict['timestamp'].isoformat()
                
                # Filter by threshold if provided
                if threshold and score_dict['severity'] < float(threshold):
                    continue
                    
                scores.append(score_dict)
            
            return jsonify({
                'status': 'success',
                'scores': scores,
                'count': len(scores)
            })
            
        finally:
            db.close()
            
    except Exception as e:
        logger.error(f"Error retrieving anomaly scores: {e}", exc_info=True)
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500


# ==================== Health Endpoint ====================

@ml_bp.route('/health', methods=['GET'])
def ml_health():
    """
    Check ML module health and status.
    """
    try:
        db = get_db_session()
        try:
            # Check if we have any data
            result = db.execute(text("SELECT COUNT(*) FROM metrics_history"))
            metrics_count = result.fetchone()[0]
            
            # Check active models
            result = db.execute(text("SELECT COUNT(*) FROM ml_models WHERE is_active = TRUE"))
            active_models = result.fetchone()[0]
            
            # Check latest metrics
            result = db.execute(text("SELECT MAX(timestamp) FROM metrics_history"))
            latest_metric = result.fetchone()[0]
            
            data_age_minutes = None
            if latest_metric:
                data_age_minutes = (datetime.utcnow() - latest_metric).total_seconds() / 60
            
            return jsonify({
                'status': 'healthy',
                'ml_module_version': '1.0.0',
                'metrics_collected': metrics_count,
                'active_models': active_models,
                'latest_metric_timestamp': latest_metric.isoformat() if latest_metric else None,
                'data_age_minutes': round(data_age_minutes, 1) if data_age_minutes else None,
                'data_collection_active': data_age_minutes < 5 if data_age_minutes else False
            })
        finally:
            db.close()
            
    except Exception as e:
        logger.error(f"Error checking ML health: {e}", exc_info=True)
        return jsonify({
            'status': 'unhealthy',
            'error': str(e)
        }), 500


# Export blueprint
__all__ = ['ml_bp']
