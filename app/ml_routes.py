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


# ==================== Forecasting Endpoints ====================

@ml_bp.route('/train/forecaster', methods=['POST'])
def train_forecaster():
    """
    Train Prophet forecaster models for metrics.
    Request body:
        - metrics: List of metrics to forecast (optional, default: all)
        - hours_ahead: Forecast horizon (optional, default: 6)
    """
    try:
        from bot.ml.forecaster import MetricForecaster
        
        data = request.get_json() or {}
        metrics = data.get('metrics')
        
        # Load training data
        db = get_db_session()
        try:
            query = "SELECT * FROM metrics_history ORDER BY timestamp"
            result = db.execute(text(query))
            rows = result.fetchall()
            columns = result.keys()
            
            if len(rows) < 1000:
                return jsonify({
                    'status': 'error',
                    'message': f'Need at least 1000 samples for forecasting, got {len(rows)}'
                }), 400
            
            df = pd.DataFrame(rows, columns=columns)
            
            logger.info(f"Training forecaster on {len(df)} samples...")
            
            # Train forecaster
            forecaster = MetricForecaster()
            training_stats = forecaster.train(df, metrics=metrics)
            
            # Save model
            model_path = '/app/data/models/forecaster_latest.joblib'
            forecaster.save(model_path)
            
            # Save metadata to database
            db.execute(text("""
                INSERT INTO ml_models (name, version, model_type, status, performance_metrics,
                                      training_samples, trained_at, file_path, is_active)
                VALUES (:name, :version, :model_type, :status, :performance_metrics,
                       :training_samples, :trained_at, :file_path, :is_active)
            """), {
                'name': 'forecaster',
                'version': datetime.now().strftime('%Y%m%d_%H%M%S'),
                'model_type': 'prophet',
                'status': 'active',
                'performance_metrics': str(training_stats),
                'training_samples': len(df),
                'trained_at': datetime.now(),
                'file_path': model_path,
                'is_active': True
            })
            db.commit()
            
            return jsonify({
                'status': 'success',
                'message': 'Forecaster trained successfully',
                'training_stats': training_stats,
                'model_path': model_path
            })
            
        finally:
            db.close()
            
    except Exception as e:
        logger.error(f"Error training forecaster: {e}", exc_info=True)
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500


@ml_bp.route('/forecast', methods=['GET'])
def get_forecast():
    """
    Get forecast for specified metrics.
    Query params:
        - hours_ahead: Forecast horizon (1-24, default: 6)
        - metric: Specific metric to forecast (optional, default: all)
    """
    try:
        from bot.ml.forecaster import MetricForecaster
        
        hours_ahead = int(request.args.get('hours_ahead', 6))
        metric = request.args.get('metric')
        
        if not (1 <= hours_ahead <= 24):
            return jsonify({'error': 'hours_ahead must be between 1 and 24'}), 400
        
        # Load model
        model_path = '/app/data/models/forecaster_latest.joblib'
        
        try:
            forecaster = MetricForecaster.load(model_path)
        except FileNotFoundError:
            return jsonify({
                'status': 'error',
                'message': 'No trained forecaster found. Train first using /api/ml/train/forecaster'
            }), 404
        
        # Generate forecast
        if metric:
            if metric not in forecaster.models:
                return jsonify({'error': f'No model for metric: {metric}'}), 400
            
            forecast_df = forecaster.forecast_single_metric(metric, hours_ahead)
            
            # Store forecasts in database
            db = get_db_session()
            try:
                for _, row in forecast_df.iterrows():
                    db.execute(text("""
                        INSERT INTO metric_forecasts (metric_name, forecast_timestamp, 
                                                      forecasted_value, lower_bound, upper_bound,
                                                      created_at, horizon_hours)
                        VALUES (:metric, :timestamp, :forecast, :lower, :upper, :created, :horizon)
                    """), {
                        'metric': metric,
                        'timestamp': row['timestamp'],
                        'forecast': float(row['forecast']),
                        'lower': float(row['lower_bound']),
                        'upper': float(row['upper_bound']),
                        'created': datetime.now(),
                        'horizon': hours_ahead
                    })
                db.commit()
            finally:
                db.close()
            
            result = forecast_df.to_dict('records')
        else:
            forecast_df = forecaster.forecast(hours_ahead)
            result = forecast_df.to_dict('records')
        
        # Convert timestamps to ISO format
        for item in result:
            if 'timestamp' in item:
                item['timestamp'] = item['timestamp'].isoformat()
        
        return jsonify({
            'status': 'success',
            'forecast': result,
            'hours_ahead': hours_ahead,
            'generated_at': datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Error generating forecast: {e}", exc_info=True)
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500


@ml_bp.route('/forecast/next-hour', methods=['GET'])
def get_next_hour_forecast():
    """
    Get average predicted values for next hour (quick summary).
    """
    try:
        from bot.ml.forecaster import MetricForecaster
        
        model_path = '/app/data/models/forecaster_latest.joblib'
        
        try:
            forecaster = MetricForecaster.load(model_path)
        except FileNotFoundError:
            return jsonify({
                'status': 'error',
                'message': 'No trained forecaster found'
            }), 404
        
        predictions = forecaster.predict_next_hour()
        
        return jsonify({
            'status': 'success',
            'predictions': predictions,
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Error getting next hour forecast: {e}", exc_info=True)
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500


@ml_bp.route('/forecast/alerts', methods=['GET'])
def get_forecast_alerts():
    """
    Check if forecasts predict threshold breaches.
    """
    try:
        from bot.ml.forecaster import MetricForecaster
        
        model_path = '/app/data/models/forecaster_latest.joblib'
        
        try:
            forecaster = MetricForecaster.load(model_path)
        except FileNotFoundError:
            return jsonify({
                'status': 'error',
                'message': 'No trained forecaster found'
            }), 404
        
        # Define thresholds (can be made configurable)
        thresholds = {
            'cpu_usage_percent': 80.0,
            'memory_usage_mb': 7000,
            'error_rate': 0.10,
            'response_time_p95': 2000
        }
        
        alerts = forecaster.detect_anomalous_forecast(thresholds)
        
        return jsonify({
            'status': 'success',
            'alerts': alerts,
            'alert_count': len(alerts),
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Error checking forecast alerts: {e}", exc_info=True)
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500


@ml_bp.route('/forecast/trend/<metric>', methods=['GET'])
def get_trend_analysis(metric: str):
    """
    Get trend analysis for a specific metric.
    """
    try:
        from bot.ml.forecaster import MetricForecaster
        
        model_path = '/app/data/models/forecaster_latest.joblib'
        
        try:
            forecaster = MetricForecaster.load(model_path)
        except FileNotFoundError:
            return jsonify({
                'status': 'error',
                'message': 'No trained forecaster found'
            }), 404
        
        trend = forecaster.get_trend_analysis(metric)
        
        return jsonify({
            'status': 'success',
            'trend': trend
        })
        
    except ValueError as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 404
    except Exception as e:
        logger.error(f"Error getting trend analysis: {e}", exc_info=True)
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


# ==================== LLM Analysis Endpoints ====================

@ml_bp.route('/analyze/incident/<int:incident_id>', methods=['POST'])
def analyze_incident_with_llm(incident_id: int):
    """
    Analyze incident using LLM and store insights.
    """
    try:
        from bot.ml.llm_analyzer import LLMAnalyzer
        
        # Get incident from database
        db = get_db_session()
        try:
            result = db.execute(text("""
                SELECT id, type, severity, details, timestamp, status
                FROM incidents
                WHERE id = :id
            """), {'id': incident_id})
            
            row = result.fetchone()
            if not row:
                return jsonify({'error': f'Incident {incident_id} not found'}), 404
            
            incident = {
                'id': row[0],
                'type': row[1],
                'severity': row[2],
                'details': row[3],
                'timestamp': row[4].isoformat() if row[4] else None,
                'status': row[5]
            }
            
            # Analyze with LLM
            analyzer = LLMAnalyzer()
            analysis = analyzer.analyze_incident(incident)
            
            # Store analysis in database
            db.execute(text("""
                INSERT INTO llm_analyses (incident_id, root_cause, suggested_actions,
                                         explanation, confidence, model_used, analyzed_at)
                VALUES (:incident_id, :root_cause, :suggestions, :explanation,
                       :confidence, :model, :analyzed_at)
            """), {
                'incident_id': incident_id,
                'root_cause': analysis.get('root_cause', ''),
                'suggestions': str(analysis.get('suggestions', [])),
                'explanation': analysis.get('explanation', ''),
                'confidence': analysis.get('confidence', 'medium'),
                'model': analysis.get('model', 'llama3.2:3b'),
                'analyzed_at': datetime.now()
            })
            db.commit()
            
            return jsonify({
                'status': 'success',
                'incident_id': incident_id,
                'analysis': analysis
            })
            
        finally:
            db.close()
            
    except Exception as e:
        logger.error(f"Error analyzing incident: {e}", exc_info=True)
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500


@ml_bp.route('/analyze/metrics-pattern', methods=['POST'])
def analyze_metrics_pattern():
    """
    Analyze metrics pattern using LLM.
    Request body:
        - hours: Number of hours of history to analyze (default: 24)
    """
    try:
        from bot.ml.llm_analyzer import LLMAnalyzer
        
        data = request.get_json() or {}
        hours = data.get('hours', 24)
        
        # Get recent metrics
        db = get_db_session()
        try:
            result = db.execute(text("""
                SELECT timestamp, cpu_usage_percent, memory_usage_mb, error_rate,
                       response_time_p95
                FROM metrics_history
                WHERE timestamp > NOW() - INTERVAL ':hours hours'
                ORDER BY timestamp DESC
                LIMIT 1000
            """), {'hours': hours})
            
            rows = result.fetchall()
            columns = result.keys()
            
            if not rows:
                return jsonify({'error': 'No metrics data available'}), 404
            
            metrics = [dict(zip(columns, row)) for row in rows]
            
            # Analyze with LLM
            analyzer = LLMAnalyzer()
            analysis = analyzer.analyze_metrics_pattern(metrics)
            
            return jsonify({
                'status': 'success',
                'analysis': analysis,
                'metrics_analyzed': len(metrics),
                'time_range_hours': hours
            })
            
        finally:
            db.close()
            
    except Exception as e:
        logger.error(f"Error analyzing metrics pattern: {e}", exc_info=True)
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500


@ml_bp.route('/suggest-remediation', methods=['POST'])
def suggest_remediation():
    """
    Get LLM-powered remediation suggestions.
    Request body:
        - incident_type: Type of incident
        - context: Additional context dictionary
    """
    try:
        from bot.ml.llm_analyzer import LLMAnalyzer
        
        data = request.get_json()
        if not data:
            return jsonify({'error': 'Request body required'}), 400
        
        incident_type = data.get('incident_type')
        context = data.get('context', {})
        
        if not incident_type:
            return jsonify({'error': 'incident_type required'}), 400
        
        analyzer = LLMAnalyzer()
        suggestions = analyzer.suggest_remediation(incident_type, context)
        
        return jsonify({
            'status': 'success',
            'incident_type': incident_type,
            'suggestions': suggestions
        })
        
    except Exception as e:
        logger.error(f"Error suggesting remediation: {e}", exc_info=True)
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500


@ml_bp.route('/generate-report/<int:incident_id>', methods=['GET'])
def generate_incident_report(incident_id: int):
    """
    Generate natural language incident report using LLM.
    """
    try:
        from bot.ml.llm_analyzer import LLMAnalyzer
        
        db = get_db_session()
        try:
            # Get incident
            result = db.execute(text("""
                SELECT id, type, severity, details, timestamp, status
                FROM incidents
                WHERE id = :id
            """), {'id': incident_id})
            
            row = result.fetchone()
            if not row:
                return jsonify({'error': f'Incident {incident_id} not found'}), 404
            
            incident = {
                'id': row[0],
                'type': row[1],
                'severity': row[2],
                'details': row[3],
                'timestamp': row[4].isoformat() if row[4] else None,
                'status': row[5]
            }
            
            # Get LLM analysis
            result = db.execute(text("""
                SELECT root_cause, suggested_actions, explanation, confidence
                FROM llm_analyses
                WHERE incident_id = :id
                ORDER BY analyzed_at DESC
                LIMIT 1
            """), {'id': incident_id})
            
            analysis_row = result.fetchone()
            analysis = {}
            if analysis_row:
                analysis = {
                    'root_cause': analysis_row[0],
                    'suggestions': analysis_row[1],
                    'explanation': analysis_row[2],
                    'confidence': analysis_row[3]
                }
            
            # Get remediation actions
            result = db.execute(text("""
                SELECT action_type, target, success, error_message, timestamp
                FROM remediation_actions
                WHERE incident_id = :id
                ORDER BY timestamp
            """), {'id': incident_id})
            
            actions = []
            for action_row in result.fetchall():
                actions.append({
                    'action_type': action_row[0],
                    'target': action_row[1],
                    'success': action_row[2],
                    'error_message': action_row[3],
                    'timestamp': action_row[4].isoformat() if action_row[4] else None
                })
            
            # Generate report
            analyzer = LLMAnalyzer()
            report = analyzer.generate_incident_report(incident, analysis, actions)
            
            return jsonify({
                'status': 'success',
                'incident_id': incident_id,
                'report': report,
                'generated_at': datetime.now().isoformat()
            })
            
        finally:
            db.close()
            
    except Exception as e:
        logger.error(f"Error generating report: {e}", exc_info=True)
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500


@ml_bp.route('/llm/health', methods=['GET'])
def llm_health():
    """
    Check LLM service health.
    """
    try:
        from bot.ml.llm_analyzer import LLMAnalyzer
        
        analyzer = LLMAnalyzer()
        
        return jsonify({
            'status': 'available' if analyzer.is_available else 'unavailable',
            'ollama_url': analyzer.ollama_url,
            'model': analyzer.model,
            'message': 'LLM ready for analysis' if analyzer.is_available else 'Ollama service not accessible'
        })
        
    except Exception as e:
        logger.error(f"Error checking LLM health: {e}", exc_info=True)
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500


# ============================================================================
# PHASE 5: FAILURE PREDICTION ENDPOINTS
# ============================================================================

@ml_bp.route('/failure-prediction/train', methods=['POST'])
def train_failure_predictor():
    """
    Train the failure prediction model.
    
    Request body (optional):
        {
            "hours_back": 168,  // Hours of historical data (default: 7 days)
            "num_iterations": 100  // Boosting iterations (default: 100)
        }
    """
    try:
        from bot.ml.failure_predictor import FailurePredictor
        
        data = request.get_json() or {}
        hours_back = data.get('hours_back', 168)  # 7 days default
        num_iterations = data.get('num_iterations', 100)
        
        predictor = FailurePredictor(db.session.connection())
        metrics = predictor.train(hours_back=hours_back, num_iterations=num_iterations)
        
        # Store model metadata
        from sqlalchemy import text
        store_query = text("""
            INSERT INTO ml_models (model_name, model_type, version, accuracy, metadata, trained_at)
            VALUES ('failure_predictor', 'lightgbm', 1, :accuracy, :metadata, NOW())
            ON DUPLICATE KEY UPDATE
                accuracy = :accuracy,
                metadata = :metadata,
                trained_at = NOW()
        """)
        
        db.session.execute(store_query, {
            'accuracy': metrics.get('train_accuracy', 0.0),
            'metadata': str(metrics)
        })
        db.session.commit()
        
        return jsonify({
            'status': 'success',
            'message': 'Failure predictor trained successfully',
            'metrics': metrics
        })
        
    except ImportError:
        return jsonify({
            'status': 'error',
            'message': 'LightGBM not available. Install with: pip install lightgbm'
        }), 500
        
    except Exception as e:
        logger.error(f"Error training failure predictor: {e}", exc_info=True)
        db.session.rollback()
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500


@ml_bp.route('/failure-prediction/predict', methods=['POST'])
def predict_failure():
    """
    Predict failure probability for the next hour.
    
    Request body (optional):
        {
            "lookback_hours": 1  // Hours of recent data to analyze
        }
    """
    try:
        from bot.ml.failure_predictor import FailurePredictor
        
        data = request.get_json() or {}
        lookback_hours = data.get('lookback_hours', 1)
        
        predictor = FailurePredictor(db.session.connection())
        
        # Load model if exists (in production, cache this)
        from sqlalchemy import text
        check_query = text("""
            SELECT COUNT(*) as count FROM ml_models 
            WHERE model_name = 'failure_predictor'
        """)
        result = db.session.execute(check_query).fetchone()
        
        if result[0] == 0:
            return jsonify({
                'status': 'error',
                'message': 'Model not trained. Train first using /api/ml/failure-prediction/train'
            }), 400
        
        # Note: In production, load actual model from disk
        # For now, we'll train a quick model if needed
        if not predictor.is_trained:
            logger.info("Training quick model for prediction...")
            predictor.train(hours_back=24, num_iterations=50)
        
        prediction = predictor.predict(lookback_hours=lookback_hours)
        
        # Store prediction
        if prediction.get('status') == 'success':
            store_query = text("""
                INSERT INTO failure_predictions 
                (prediction_time, failure_probability, risk_level, lookback_hours, metadata)
                VALUES (NOW(), :probability, :risk_level, :lookback_hours, :metadata)
            """)
            
            db.session.execute(store_query, {
                'probability': prediction['probability'],
                'risk_level': prediction['risk_level'],
                'lookback_hours': lookback_hours,
                'metadata': str(prediction)
            })
            db.session.commit()
        
        return jsonify(prediction)
        
    except Exception as e:
        logger.error(f"Error predicting failure: {e}", exc_info=True)
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500


@ml_bp.route('/failure-prediction/forecast', methods=['POST'])
def forecast_failures():
    """
    Forecast failure probabilities for multiple hours ahead.
    
    Request body (optional):
        {
            "hours_ahead": 24  // How many hours to forecast
        }
    """
    try:
        from bot.ml.failure_predictor import FailurePredictor
        
        data = request.get_json() or {}
        hours_ahead = min(data.get('hours_ahead', 24), 72)  # Max 72 hours
        
        predictor = FailurePredictor(db.session.connection())
        
        # Quick train if needed
        if not predictor.is_trained:
            logger.info("Training quick model for forecast...")
            predictor.train(hours_back=24, num_iterations=50)
        
        predictions = predictor.predict_batch(hours_ahead=hours_ahead)
        
        return jsonify({
            'status': 'success',
            'hours_ahead': hours_ahead,
            'predictions': predictions
        })
        
    except Exception as e:
        logger.error(f"Error forecasting failures: {e}", exc_info=True)
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500


@ml_bp.route('/failure-prediction/alerts', methods=['GET'])
def get_failure_alerts():
    """
    Get recent failure predictions that exceed alert thresholds.
    """
    try:
        from sqlalchemy import text
        
        query = text("""
            SELECT 
                prediction_time,
                failure_probability,
                risk_level,
                lookback_hours,
                metadata
            FROM failure_predictions
            WHERE risk_level IN ('high', 'medium')
            ORDER BY prediction_time DESC
            LIMIT 50
        """)
        
        result = db.session.execute(query)
        alerts = []
        
        for row in result:
            alerts.append({
                'prediction_time': row[0].isoformat(),
                'failure_probability': float(row[1]),
                'risk_level': row[2],
                'lookback_hours': row[3],
                'metadata': row[4]
            })
        
        return jsonify({
            'status': 'success',
            'count': len(alerts),
            'alerts': alerts
        })
        
    except Exception as e:
        logger.error(f"Error getting failure alerts: {e}", exc_info=True)
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500


@ml_bp.route('/failure-prediction/model-info', methods=['GET'])
def get_predictor_info():
    """
    Get information about the trained failure prediction model.
    """
    try:
        from bot.ml.failure_predictor import FailurePredictor
        
        predictor = FailurePredictor(db.session.connection())
        
        # Try to train a quick model if not trained
        if not predictor.is_trained:
            try:
                predictor.train(hours_back=24, num_iterations=50)
            except:
                pass
        
        info = predictor.get_model_info()
        
        # Get training history from database
        from sqlalchemy import text
        history_query = text("""
            SELECT trained_at, accuracy, metadata
            FROM ml_models
            WHERE model_name = 'failure_predictor'
            ORDER BY trained_at DESC
            LIMIT 5
        """)
        
        result = db.session.execute(history_query)
        training_history = []
        
        for row in result:
            training_history.append({
                'trained_at': row[0].isoformat() if row[0] else None,
                'accuracy': float(row[1]) if row[1] else 0.0,
                'metadata': row[2]
            })
        
        info['training_history'] = training_history
        
        return jsonify(info)
        
    except Exception as e:
        logger.error(f"Error getting predictor info: {e}", exc_info=True)
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500


# ============================================================================
# PHASE 6: CONTINUOUS LEARNING ENDPOINTS
# ============================================================================

@ml_bp.route('/continuous-learning/status', methods=['GET'])
def get_continuous_learning_status():
    """
    Get current status of all ML models (training state, performance, etc.).
    """
    try:
        from bot.ml.continuous_learning import ContinuousLearning
        
        cl = ContinuousLearning(db.session.connection())
        status = cl.get_model_status()
        
        return jsonify(status)
        
    except Exception as e:
        logger.error(f"Error getting continuous learning status: {e}", exc_info=True)
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500


@ml_bp.route('/continuous-learning/check-retrain', methods=['POST'])
def check_and_retrain():
    """
    Check if models need retraining and retrain if necessary.
    
    This is automatically done by the bot, but can be manually triggered.
    """
    try:
        from bot.ml.continuous_learning import ContinuousLearning
        
        cl = ContinuousLearning(db.session.connection())
        actions = cl.check_and_retrain()
        
        return jsonify(actions)
        
    except Exception as e:
        logger.error(f"Error in check and retrain: {e}", exc_info=True)
        db.session.rollback()
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500


@ml_bp.route('/continuous-learning/retrain-all', methods=['POST'])
def retrain_all_models():
    """
    Force retrain all ML models regardless of criteria.
    
    Use with caution - this can take several minutes.
    """
    try:
        from bot.ml.continuous_learning import ContinuousLearning
        
        cl = ContinuousLearning(db.session.connection())
        results = cl.retrain_all_models()
        
        return jsonify(results)
        
    except Exception as e:
        logger.error(f"Error retraining all models: {e}", exc_info=True)
        db.session.rollback()
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500


@ml_bp.route('/continuous-learning/evaluate/<model_name>', methods=['POST'])
def evaluate_model(model_name):
    """
    Evaluate model performance on recent data.
    
    Args:
        model_name: 'anomaly_detector', 'failure_predictor', or 'forecaster'
    
    Request body (optional):
        {
            "hours_back": 24  // Hours of data to evaluate
        }
    """
    try:
        from bot.ml.continuous_learning import ContinuousLearning
        
        data = request.get_json() or {}
        hours_back = data.get('hours_back', 24)
        
        cl = ContinuousLearning(db.session.connection())
        performance = cl.evaluate_model_performance(model_name, hours_back)
        
        return jsonify(performance)
        
    except Exception as e:
        logger.error(f"Error evaluating model {model_name}: {e}", exc_info=True)
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500


@ml_bp.route('/continuous-learning/training-history', methods=['GET'])
def get_training_history():
    """
    Get training history for all models or a specific model.
    
    Query params:
        model_name: Optional model name filter
        limit: Maximum records to return (default: 10)
    """
    try:
        from bot.ml.continuous_learning import ContinuousLearning
        
        model_name = request.args.get('model_name')
        limit = int(request.args.get('limit', 10))
        
        cl = ContinuousLearning(db.session.connection())
        history = cl.get_training_history(model_name=model_name, limit=limit)
        
        return jsonify({
            'status': 'success',
            'count': len(history),
            'history': history
        })
        
    except Exception as e:
        logger.error(f"Error getting training history: {e}", exc_info=True)
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500


@ml_bp.route('/continuous-learning/metrics-summary', methods=['GET'])
def get_ml_metrics_summary():
    """
    Get summary of ML system performance across all models.
    """
    try:
        from sqlalchemy import text
        
        # Get overall stats
        stats_query = text("""
            SELECT 
                COUNT(DISTINCT model_name) as total_models,
                SUM(CASE WHEN trained_at > NOW() - INTERVAL '24 hours' THEN 1 ELSE 0 END) as recently_trained,
                AVG(accuracy) as avg_accuracy
            FROM ml_models
            WHERE model_name IN ('anomaly_detector', 'failure_predictor')
        """)
        
        stats = db.session.execute(stats_query).fetchone()
        
        # Get recent predictions count
        predictions_query = text("""
            SELECT 
                (SELECT COUNT(*) FROM anomaly_scores WHERE timestamp > NOW() - INTERVAL '24 hours') as anomaly_predictions,
                (SELECT COUNT(*) FROM failure_predictions WHERE prediction_time > NOW() - INTERVAL '24 hours') as failure_predictions,
                (SELECT COUNT(*) FROM metric_forecasts WHERE forecast_time > NOW() - INTERVAL '24 hours') as forecasts
        """)
        
        predictions = db.session.execute(predictions_query).fetchone()
        
        # Get incidents detected by ML
        ml_incidents_query = text("""
            SELECT COUNT(*) 
            FROM incidents 
            WHERE type IN ('ml_anomaly', 'predicted_breach', 'predicted_failure')
                AND detected_at > NOW() - INTERVAL '24 hours'
        """)
        
        ml_incidents = db.session.execute(ml_incidents_query).scalar()
        
        summary = {
            'status': 'success',
            'period': '24 hours',
            'timestamp': datetime.now().isoformat(),
            'models': {
                'total': int(stats[0]) if stats else 0,
                'recently_trained': int(stats[1]) if stats else 0,
                'avg_accuracy': float(stats[2]) if stats and stats[2] else 0.0
            },
            'predictions': {
                'anomaly_detections': int(predictions[0]) if predictions else 0,
                'failure_predictions': int(predictions[1]) if predictions else 0,
                'forecasts': int(predictions[2]) if predictions else 0
            },
            'ml_incidents_detected': int(ml_incidents) if ml_incidents else 0
        }
        
        return jsonify(summary)
        
    except Exception as e:
        logger.error(f"Error getting ML metrics summary: {e}", exc_info=True)
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500


