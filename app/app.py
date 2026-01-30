"""
Main Flask application for Auto-Remediation Platform.
Provides REST API endpoints for health monitoring, metrics, incidents, and remediation.
"""
import os
import sys
import time
import random
import logging
import threading
import psutil
from datetime import datetime, timedelta
from flask import Flask, jsonify, request
from flask_cors import CORS
from flasgger import Swagger
from sqlalchemy import desc, and_

from config import Config
from models import (
    init_db, get_db_session, Incident, RemediationAction,
    MetricsSnapshot, ConfigEntry, ActionHistory, text
)
from metrics import (
    REQUEST_COUNT, ERROR_COUNT, REQUEST_DURATION, CPU_USAGE,
    MEMORY_USAGE, ACTIVE_CONNECTIONS, UPTIME, APP_INFO,
    SIMULATED_CPU_SPIKE, get_metrics
)
from simulate import start_simulator
from websocket import init_socketio, broadcast_metric_update, broadcast_health_update
from db_monitor import DatabaseMonitor

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)
app.config.from_object(Config)
CORS(app)  # Enable CORS for frontend

# Initialize Swagger UI
swagger_config = {
    "headers": [],
    "specs": [
        {
            "endpoint": 'apispec',
            "route": '/apispec.json',
            "rule_filter": lambda rule: True,
            "model_filter": lambda tag: True,
        }
    ],
    "static_url_path": "/flasgger_static",
    "swagger_ui": True,
    "specs_route": "/api/docs"
}

swagger_template = {
    "swagger": "2.0",
    "info": {
        "title": "Auto-Remediation Platform API",
        "description": "REST API for infrastructure auto-remediation, monitoring, and incident management. "
                      "This API provides endpoints for health checks, incident tracking, remediation actions, "
                      "configuration management, and real-time metrics via WebSocket.",
        "contact": {
            "name": "API Support",
            "url": "https://github.com/mainulhossain123/infra-autofix-agent"
        },
        "version": "1.0.0"
    },
    "host": os.getenv("SWAGGER_HOST", "localhost:5000"),
    "basePath": "/",
    "schemes": ["http", "https"],
    "securityDefinitions": {},
    "tags": [
        {
            "name": "Health",
            "description": "Health check and service status endpoints"
        },
        {
            "name": "Incidents",
            "description": "Incident tracking and management"
        },
        {
            "name": "Remediation",
            "description": "Remediation actions and history"
        },
        {
            "name": "Configuration",
            "description": "System configuration and thresholds"
        },
        {
            "name": "Metrics",
            "description": "Prometheus metrics and monitoring"
        },
        {
            "name": "Triggers",
            "description": "Manual incident triggers for testing"
        }
    ]
}

swagger = Swagger(app, config=swagger_config, template=swagger_template)

# Initialize WebSocket
socketio = init_socketio(app)

# Initialize Database Monitor
db_monitor = DatabaseMonitor()

# Application state
app_state = {
    'requests': 0,
    'errors': 0,
    'last_error_timestamp': None,
    'cpu_spike': False,
    'error_spike': False,
    'error_probability': Config.RANDOM_ERROR_PROBABILITY,
    'start_time': time.time(),
    'response_times': []  # Track recent response times
}

# Service name
SERVICE_NAME = Config.get_service_name()


@app.before_request
def before_request():
    """Track request start time"""
    request._start_time = time.time()


@app.after_request
def after_request(response):
    """Track request metrics after each request"""
    # Update request count
    app_state['requests'] += 1
    
    # Track response time
    if hasattr(request, '_start_time'):
        duration = time.time() - request._start_time
        app_state['response_times'].append(duration * 1000)  # Convert to ms
        # Keep only last 100 response times
        if len(app_state['response_times']) > 100:
            app_state['response_times'] = app_state['response_times'][-100:]
        
        # Update Prometheus metrics
        REQUEST_DURATION.labels(
            method=request.method,
            endpoint=request.endpoint or 'unknown'
        ).observe(duration)
    
    # Update request count metric
    REQUEST_COUNT.labels(
        method=request.method,
        endpoint=request.endpoint or 'unknown',
        status=response.status_code
    ).inc()
    
    return response


# ==================== Health & Status Endpoints ====================

@app.route('/')
def index():
    """Basic health check endpoint"""
    app_state['requests'] += 1
    
    # Simulate random errors based on error_probability
    if random.random() < app_state['error_probability']:
        app_state['errors'] += 1
        app_state['last_error_timestamp'] = time.time()
        ERROR_COUNT.labels(endpoint='index', error_type='simulated').inc()
        
        logger.warning(f"[{SERVICE_NAME}] Simulated error occurred")
        return jsonify({'error': 'Internal Server Error', 'service': SERVICE_NAME}), 500
    
    return jsonify({
        'status': 'ok',
        'service': SERVICE_NAME,
        'message': f'OK from {SERVICE_NAME}'
    }), 200


@app.route('/health')
@app.route('/api/health')
def health():
    """
    Health Check Endpoint
    ---
    tags:
      - Health
    summary: Get application health status and metrics
    description: Returns detailed health information including system metrics, request counts, error rates, and response times
    responses:
      200:
        description: Health check successful
        schema:
          type: object
          properties:
            status:
              type: string
              example: ok
            service:
              type: string
              example: auto-remediation-app
            timestamp:
              type: string
              format: date-time
            uptime_seconds:
              type: integer
              example: 3600
            metrics:
              type: object
              properties:
                total_requests:
                  type: integer
                  example: 1234
                total_errors:
                  type: integer
                  example: 5
                error_rate:
                  type: number
                  format: float
                  example: 0.0041
                cpu_usage_percent:
                  type: number
                  format: float
                  example: 45.32
                memory_usage_mb:
                  type: number
                  format: float
                  example: 128.5
                response_time_p50_ms:
                  type: number
                  format: float
                  example: 15.2
                response_time_p95_ms:
                  type: number
                  format: float
                  example: 45.8
                response_time_p99_ms:
                  type: number
                  format: float
                  example: 98.5
            flags:
              type: object
              properties:
                cpu_spike:
                  type: boolean
                  example: false
                error_spike:
                  type: boolean
                  example: false
    """
    error_rate = app_state['errors'] / app_state['requests'] if app_state['requests'] > 0 else 0
    uptime = int(time.time() - app_state['start_time'])
    
    # Get CPU and memory usage
    try:
        cpu_percent = psutil.cpu_percent(interval=0.1)
        memory_info = psutil.Process().memory_info()
        memory_mb = memory_info.rss / (1024 * 1024)
    except Exception as e:
        logger.error(f"Error getting system metrics: {e}")
        cpu_percent = 0
        memory_mb = 0
    
    # Update Prometheus gauges
    CPU_USAGE.set(cpu_percent)
    MEMORY_USAGE.set(memory_mb)
    UPTIME.set(uptime)
    
    # Calculate response time percentiles
    p50 = p95 = p99 = None
    if app_state['response_times']:
        sorted_times = sorted(app_state['response_times'])
        p50 = sorted_times[int(len(sorted_times) * 0.5)]
        p95 = sorted_times[int(len(sorted_times) * 0.95)]
        p99 = sorted_times[int(len(sorted_times) * 0.99)]
    
    health_data = {
        'status': 'ok',
        'service': SERVICE_NAME,
        'timestamp': datetime.utcnow().isoformat(),
        'uptime_seconds': uptime,
        'metrics': {
            'total_requests': app_state['requests'],
            'total_errors': app_state['errors'],
            'error_rate': round(error_rate, 4),
            'cpu_usage_percent': round(cpu_percent, 2),
            'memory_usage_mb': round(memory_mb, 2),
            'response_time_p50_ms': round(p50, 2) if p50 else None,
            'response_time_p95_ms': round(p95, 2) if p95 else None,
            'response_time_p99_ms': round(p99, 2) if p99 else None,
        },
        'flags': {
            'cpu_spike': app_state['cpu_spike'],  # Only from manual triggers, not background simulator
            'error_spike': app_state['error_spike']
        }
    }
    
    return jsonify(health_data), 200


@app.route('/api/metrics')
def api_metrics():
    """Get current metrics in JSON format"""
    return health()


@app.route('/metrics')
def prometheus_metrics():
    """Prometheus metrics endpoint"""
    return get_metrics()


# ==================== Database Health Endpoints ====================

@app.route('/api/database/health')
def database_health():
    """Get comprehensive database health metrics"""
    try:
        health = db_monitor.check_health()
        return jsonify(health), 200
    except Exception as e:
        logger.error(f"Database health check error: {e}")
        return jsonify({
            'status': 'error',
            'error': str(e),
            'timestamp': datetime.utcnow().isoformat()
        }), 500

@app.route('/api/database/connections')
def database_connections():
    """Get database connection pool statistics"""
    try:
        stats = db_monitor.get_connection_stats()
        return jsonify(stats), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/alerts', methods=['POST'])
def receive_alert():
    """Receive alerts from AlertManager and create incidents"""
    try:
        alert_data = request.json
        logger.info(f"Received alert from AlertManager: {alert_data}")
        
        # Process alerts from AlertManager
        alerts = alert_data.get('alerts', [])
        created_incidents = []
        
        for alert in alerts:
            if alert.get('status') == 'firing':
                # Map alert to incident
                alert_name = alert.get('labels', {}).get('alertname', 'Unknown')
                severity = alert.get('labels', {}).get('severity', 'warning').upper()
                description = alert.get('annotations', {}).get('summary', alert_name)
                
                # Determine incident type
                incident_type = 'SYSTEM_ERROR'
                if 'cpu' in alert_name.lower():
                    incident_type = 'CPU_SPIKE'
                elif 'error' in alert_name.lower():
                    incident_type = 'ERROR_RATE'
                elif 'connection' in alert_name.lower():
                    incident_type = 'DATABASE_CONNECTION'
                elif 'down' in alert_name.lower():
                    incident_type = 'SERVICE_DOWN'
                
                # Create incident
                session = get_db_session()
                incident = Incident(
                    type=incident_type,
                    severity=severity,
                    status='ACTIVE',
                    description=description,
                    detected_at=datetime.utcnow(),
                    metadata={'alert': alert}
                )
                session.add(incident)
                session.commit()
                created_incidents.append(incident.id)
                session.close()
                
                logger.info(f"Created incident {incident.id} from alert {alert_name}")
        
        return jsonify({
            'status': 'ok',
            'incidents_created': len(created_incidents),
            'incident_ids': created_incidents
        }), 200
    except Exception as e:
        logger.error(f"Error processing alert: {e}")
        return jsonify({'error': str(e)}), 500


# ==================== Incident Endpoints ====================

@app.route('/api/incidents')
def get_incidents():
    """
    List Incidents
    ---
    tags:
      - Incidents
    summary: Get list of incidents with filtering and pagination
    description: Retrieve incidents with optional filters for status, severity, type, and time range
    parameters:
      - name: status
        in: query
        type: string
        enum: [ACTIVE, RESOLVED, ESCALATED]
        description: Filter by incident status
      - name: severity
        in: query
        type: string
        enum: [CRITICAL, WARNING, INFO]
        description: Filter by severity level
      - name: type
        in: query
        type: string
        description: Filter by incident type (e.g., CPU_SPIKE, ERROR_SPIKE)
      - name: limit
        in: query
        type: integer
        default: 50
        description: Maximum number of results to return
      - name: offset
        in: query
        type: integer
        default: 0
        description: Pagination offset
      - name: hours
        in: query
        type: integer
        default: 24
        description: Filter incidents from last N hours
    responses:
      200:
        description: List of incidents
        schema:
          type: object
          properties:
            total:
              type: integer
              example: 42
            limit:
              type: integer
              example: 50
            offset:
              type: integer
              example: 0
            incidents:
              type: array
              items:
                type: object
                properties:
                  id:
                    type: integer
                  type:
                    type: string
                  severity:
                    type: string
                  status:
                    type: string
                  timestamp:
                    type: string
                    format: date-time
                  description:
                    type: string
                  metadata:
                    type: object
      500:
        description: Server error
    """
    db = get_db_session()
    try:
        # Parse query parameters
        status = request.args.get('status')
        severity = request.args.get('severity')
        incident_type = request.args.get('type')
        limit = int(request.args.get('limit', 50))
        offset = int(request.args.get('offset', 0))
        hours = int(request.args.get('hours', 24))
        
        # Build query
        query = db.query(Incident)
        
        # Filter by time
        time_filter = datetime.utcnow() - timedelta(hours=hours)
        query = query.filter(Incident.timestamp >= time_filter)
        
        # Apply filters
        if status:
            query = query.filter(Incident.status == status.upper())
        if severity:
            query = query.filter(Incident.severity == severity.upper())
        if incident_type:
            query = query.filter(Incident.type == incident_type)
        
        # Get total count
        total = query.count()
        
        # Apply pagination and ordering
        incidents = query.order_by(desc(Incident.timestamp)).limit(limit).offset(offset).all()
        
        return jsonify({
            'total': total,
            'limit': limit,
            'offset': offset,
            'incidents': [inc.to_dict() for inc in incidents]
        }), 200
        
    except Exception as e:
        logger.error(f"Error fetching incidents: {e}")
        return jsonify({'error': str(e)}), 500
    finally:
        db.close()


@app.route('/api/incidents/<int:incident_id>')
def get_incident(incident_id):
    """Get single incident by ID with remediation actions"""
    db = get_db_session()
    try:
        incident = db.query(Incident).filter(Incident.id == incident_id).first()
        
        if not incident:
            return jsonify({'error': 'Incident not found'}), 404
        
        # Get remediation actions
        actions = db.query(RemediationAction).filter(
            RemediationAction.incident_id == incident_id
        ).order_by(RemediationAction.timestamp).all()
        
        result = incident.to_dict()
        result['remediation_actions'] = [action.to_dict() for action in actions]
        
        return jsonify(result), 200
        
    except Exception as e:
        logger.error(f"Error fetching incident {incident_id}: {e}")
        return jsonify({'error': str(e)}), 500
    finally:
        db.close()


# ==================== Remediation Endpoints ====================

@app.route('/api/remediation/history')
def remediation_history():
    """
    Get remediation action history.
    Query params:
        - limit: number of results (default 50)
        - offset: pagination offset (default 0)
        - hours: filter actions from last N hours (default 24)
    """
    db = get_db_session()
    try:
        limit = int(request.args.get('limit', 50))
        offset = int(request.args.get('offset', 0))
        hours = int(request.args.get('hours', 24))
        
        time_filter = datetime.utcnow() - timedelta(hours=hours)
        
        query = db.query(RemediationAction).filter(
            RemediationAction.timestamp >= time_filter
        )
        
        total = query.count()
        actions = query.order_by(desc(RemediationAction.timestamp)).limit(limit).offset(offset).all()
        
        return jsonify({
            'total': total,
            'limit': limit,
            'offset': offset,
            'actions': [action.to_dict() for action in actions]
        }), 200
        
    except Exception as e:
        logger.error(f"Error fetching remediation history: {e}")
        return jsonify({'error': str(e)}), 500
    finally:
        db.close()


@app.route('/api/remediation/manual', methods=['POST'])
def manual_remediation():
    """
    Trigger manual remediation action.
    Expected JSON body:
        {
            "action_type": "restart_container|start_replica|stop_replica",
            "target": "ar_app|ar_app_replica",
            "reason": "optional reason"
        }
    """
    try:
        data = request.get_json()
        action_type = data.get('action_type')
        target = data.get('target')
        reason = data.get('reason', 'Manual trigger from API')
        
        if not action_type or not target:
            return jsonify({'error': 'action_type and target are required'}), 400
        
        logger.info(f"Manual remediation triggered: {action_type} on {target}")
        
        # Note: Actual remediation is handled by the bot
        # This endpoint just logs the request
        return jsonify({
            'status': 'accepted',
            'message': f'Manual remediation request received: {action_type} on {target}',
            'action_type': action_type,
            'target': target,
            'reason': reason
        }), 202
        
    except Exception as e:
        logger.error(f"Error in manual remediation: {e}")
        return jsonify({'error': str(e)}), 500


# ==================== Configuration Endpoints ====================

@app.route('/api/config')
def get_config():
    """
    Get Configuration
    ---
    tags:
      - Configuration
    summary: Get all configuration entries
    description: Returns current system configuration including thresholds and circuit breaker settings
    responses:
      200:
        description: Configuration retrieved successfully
        schema:
          type: object
          properties:
            thresholds:
              type: object
              properties:
                cpu_warning:
                  type: integer
                  example: 70
                cpu_critical:
                  type: integer
                  example: 80
                error_rate_threshold:
                  type: number
                  example: 0.2
                response_time_threshold_ms:
                  type: integer
                  example: 500
            circuit_breaker:
              type: object
              properties:
                failure_threshold:
                  type: integer
                  example: 3
                timeout_seconds:
                  type: integer
                  example: 60
                half_open_retry_delay:
                  type: integer
                  example: 30
      500:
        description: Server error
    """
    db = get_db_session()
    try:
        configs = db.query(ConfigEntry).all()
        
        # Convert array to structured object for frontend
        config_dict = {}
        for cfg in configs:
            config_dict[cfg.key] = cfg.value
        
        # Transform to match frontend expectations
        frontend_config = {}
        
        # Map thresholds to frontend format
        if 'thresholds' in config_dict:
            thresholds = config_dict['thresholds']
            frontend_config['thresholds'] = {
                'cpu_warning': thresholds.get('cpu_percent', 70),  # Map cpu_percent to cpu_warning
                'cpu_critical': thresholds.get('cpu_percent', 80),  # Default critical slightly higher
                'memory_warning': 75,  # Add missing values
                'memory_critical': 85,
                'error_rate': thresholds.get('error_rate', 0.2)
            }
        else:
            # Default thresholds
            frontend_config['thresholds'] = {
                'cpu_warning': 70,
                'cpu_critical': 80,
                'memory_warning': 75,
                'memory_critical': 85,
                'error_rate': 0.2
            }
        
        # Map circuit_breaker (use remediation values if no circuit_breaker exists)
        if 'circuit_breaker' in config_dict:
            frontend_config['circuit_breaker'] = config_dict['circuit_breaker']
        elif 'remediation' in config_dict:
            remediation = config_dict['remediation']
            frontend_config['circuit_breaker'] = {
                'failure_threshold': remediation.get('max_restarts_per_5min', 3),
                'recovery_timeout': remediation.get('cooldown_seconds', 60),
                'success_threshold': 2
            }
        else:
            # Default circuit breaker
            frontend_config['circuit_breaker'] = {
                'failure_threshold': 3,
                'recovery_timeout': 60,
                'success_threshold': 2
            }
        
        # If database was empty, initialize with defaults
        if not config_dict:
            for key, value in frontend_config.items():
                new_config = ConfigEntry(
                    key=key,
                    value=value,
                    description=f"Default {key} configuration",
                    updated_by='system'
                )
                db.add(new_config)
            db.commit()
        
        return jsonify(frontend_config), 200
    except Exception as e:
        logger.error(f"Error fetching config: {e}")
        return jsonify({'error': str(e)}), 500
    finally:
        db.close()


@app.route('/api/config', methods=['PUT'])
def update_config():
    """
    Update configuration.
    Expected JSON body: full config object with thresholds and circuit_breaker
        {
            "thresholds": {
                "cpu_warning": 70,
                "cpu_critical": 80,
                ...
            },
            "circuit_breaker": {
                "failure_threshold": 3,
                ...
            }
        }
    """
    db = get_db_session()
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'Request body is required'}), 400
        
        updated_keys = []
        
        # Update each top-level key (thresholds, circuit_breaker, etc.)
        for key, value in data.items():
            config = db.query(ConfigEntry).filter(ConfigEntry.key == key).first()
            
            if config:
                # Update existing
                config.value = value
                config.updated_at = datetime.utcnow()
                config.updated_by = 'api'
            else:
                # Create new
                config = ConfigEntry(
                    key=key,
                    value=value,
                    description=f"{key.replace('_', ' ').title()} configuration",
                    updated_by='api'
                )
                db.add(config)
            
            updated_keys.append(key)
        
        db.commit()
        
        logger.info(f"Config updated: {', '.join(updated_keys)}")
        
        return jsonify({
            'status': 'updated',
            'message': f'Configuration updated successfully',
            'updated_keys': updated_keys
        }), 200
        
    except Exception as e:
        db.rollback()
        logger.error(f"Error updating config: {e}")
        return jsonify({'error': str(e)}), 500
    finally:
        db.close()


# ==================== Simulation Endpoints ====================

@app.route('/crash', methods=['POST'])
@app.route('/api/crash', methods=['POST'])
def crash():
    """Endpoint to force application crash (for testing)"""
    logger.warning(f"[{SERVICE_NAME}] Crash endpoint called - shutting down in 1 second")
    
    def do_exit():
        time.sleep(1)
        logger.critical(f"[{SERVICE_NAME}] Exiting process")
        os._exit(1)
    
    threading.Thread(target=do_exit, daemon=True).start()
    
    return jsonify({
        'status': 'crashing',
        'message': f'{SERVICE_NAME} will crash in 1 second'
    }), 200


@app.route('/spike/cpu', methods=['POST'])
@app.route('/api/spike/cpu', methods=['POST'])
def spike_cpu():
    """
    Trigger CPU Spike
    ---
    tags:
      - Triggers
    summary: Manually trigger a CPU spike for testing
    description: Simulates high CPU usage for a specified duration. Used for testing auto-remediation
    parameters:
      - name: duration
        in: query
        type: integer
        default: 10
        description: Duration of CPU spike in seconds
    responses:
      200:
        description: CPU spike triggered successfully
        schema:
          type: object
          properties:
            status:
              type: string
              example: triggered
            message:
              type: string
              example: CPU spike triggered for 10 seconds
            duration:
              type: integer
              example: 10
    """
    from simulate import cpu_burn
    
    duration = int(request.args.get('duration', 10))
    app_state['cpu_spike'] = True
    
    def run_spike():
        cpu_burn(duration)
        # Keep flag active briefly after spike to ensure bot detects it
        time.sleep(5)  # 5 seconds should be enough for bot to detect (polls every 5s)
        app_state['cpu_spike'] = False
        logger.info(f"[{SERVICE_NAME}] CPU spike flag cleared")
    
    threading.Thread(target=run_spike, daemon=True).start()
    
    logger.info(f"[{SERVICE_NAME}] Manual CPU spike triggered for {duration}s")
    
    return jsonify({
        'status': 'triggered',
        'type': 'cpu_spike',
        'duration_seconds': duration,
        'note': 'Flag will remain active for bot detection then auto-clear'
    }), 200


@app.route('/spike/errors', methods=['POST'])
@app.route('/api/spike/errors', methods=['POST'])
def spike_errors():
    """Trigger error rate spike simulation (manual trigger for demo/testing)"""
    from simulate import error_spike
    
    duration = int(request.args.get('duration', 15))
    app_state['error_spike'] = True
    
    def run_spike():
        error_spike(duration, app_state)
        # Keep flag active briefly after spike to ensure bot detects it
        time.sleep(5)  # 5 seconds should be enough for bot to detect (polls every 5s)
        app_state['error_spike'] = False
        logger.info(f"[{SERVICE_NAME}] Error spike flag cleared")
    
    threading.Thread(target=run_spike, daemon=True).start()
    
    logger.info(f"[{SERVICE_NAME}] Manual error spike triggered for {duration}s")
    
    return jsonify({
        'status': 'triggered',
        'type': 'error_spike',
        'duration_seconds': duration,
        'note': 'Flag will remain active for bot detection then auto-clear'
    }), 200


# ==================== Application Initialization ====================

def init_app():
    """Initialize application"""
    logger.info(f"Initializing {SERVICE_NAME}")
    
    # Set app info for Prometheus
    APP_INFO.info({
        'version': '1.0.0',
        'service': SERVICE_NAME,
        'environment': Config.FLASK_ENV
    })
    
    # Wait for database to be ready
    max_retries = 10
    for i in range(max_retries):
        try:
            db = get_db_session()
            db.execute(text('SELECT 1'))
            db.close()
            logger.info("Database connection successful")
            break
        except Exception as e:
            if i < max_retries - 1:
                logger.warning(f"Database not ready, retrying in 2s... ({i+1}/{max_retries})")
                time.sleep(2)
            else:
                logger.error(f"Failed to connect to database after {max_retries} attempts")
                raise
    
    # Start background simulator if enabled
    if Config.ENABLE_SIMULATOR and not Config.REPLICA:
        logger.info("Starting background failure simulator")
        threading.Thread(target=start_simulator, args=(app_state,), daemon=True).start()
    else:
        logger.info("Simulator disabled or replica mode - skipping simulator")
    
    # Start WebSocket metric broadcaster
    def metric_broadcaster():
        """Background thread to broadcast metrics via WebSocket"""
        while True:
            try:
                time.sleep(2)  # Broadcast every 2 seconds
                metrics = {
                    'cpu_usage_percent': round(psutil.cpu_percent(interval=0.1), 2),
                    'memory_usage_mb': round(psutil.Process().memory_info().rss / 1024 / 1024, 2),
                    'total_requests': app_state['requests'],
                    'total_errors': app_state['errors'],
                    'error_rate': app_state['errors'] / max(app_state['requests'], 1)
                }
                broadcast_metric_update(metrics)
            except Exception as e:
                logger.error(f"Metric broadcaster error: {e}")
                time.sleep(5)
    
    threading.Thread(target=metric_broadcaster, daemon=True).start()
    logger.info("WebSocket metric broadcaster started")


if __name__ == '__main__':
    init_app()
    
    logger.info(f"Starting {SERVICE_NAME} on port {Config.APP_PORT}")
    socketio.run(
        app,
        host='0.0.0.0',
        port=Config.APP_PORT,
        debug=Config.DEBUG,
        allow_unsafe_werkzeug=True
    )
