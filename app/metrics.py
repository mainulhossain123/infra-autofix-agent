"""
Prometheus metrics setup for the Flask application.
"""
from prometheus_client import Counter, Histogram, Gauge, Info, generate_latest, CONTENT_TYPE_LATEST

# HTTP Request metrics
REQUEST_COUNT = Counter(
    'http_requests_total',
    'Total number of HTTP requests',
    ['method', 'endpoint', 'status']
)

ERROR_COUNT = Counter(
    'http_errors_total',
    'Total number of HTTP errors',
    ['endpoint', 'error_type']
)

REQUEST_DURATION = Histogram(
    'http_request_duration_seconds',
    'HTTP request duration in seconds',
    ['method', 'endpoint'],
    buckets=[0.01, 0.05, 0.1, 0.5, 1.0, 2.5, 5.0, 10.0]
)

# System metrics
CPU_USAGE = Gauge(
    'app_cpu_usage_percent',
    'Application CPU usage percentage'
)

MEMORY_USAGE = Gauge(
    'app_memory_usage_bytes',
    'Application memory usage in bytes'
)

ACTIVE_CONNECTIONS = Gauge(
    'app_active_connections',
    'Number of active connections'
)

UPTIME = Gauge(
    'app_uptime_seconds',
    'Application uptime in seconds'
)

# Database metrics
DB_QUERY_DURATION = Histogram(
    'database_query_duration_seconds',
    'Database query duration in seconds',
    ['operation'],
    buckets=[0.001, 0.005, 0.01, 0.05, 0.1, 0.5, 1.0]
)

DB_ERRORS = Counter(
    'database_errors_total',
    'Total number of database errors',
    ['operation', 'error_type']
)

DB_CONNECTIONS = Gauge(
    'database_connection_pool_size',
    'Number of database connections in pool'
)

# Incident metrics
INCIDENTS_TOTAL = Gauge(
    'incidents_total',
    'Total number of incidents'
)

INCIDENTS_BY_TYPE = Gauge(
    'incidents_by_type',
    'Number of incidents by type',
    ['type']
)

INCIDENTS_BY_SEVERITY = Gauge(
    'incidents_by_severity',
    'Number of incidents by severity',
    ['severity']
)

# WebSocket metrics
WEBSOCKET_CONNECTIONS = Gauge(
    'websocket_connections_active',
    'Number of active WebSocket connections'
)

WEBSOCKET_MESSAGES = Counter(
    'websocket_messages_total',
    'Total number of WebSocket messages',
    ['direction', 'event_type']
)

# Application info
APP_INFO = Info(
    'app_info',
    'Application information'
)

# Simulation metrics
SIMULATED_CPU_SPIKE = Gauge(
    'app_simulated_cpu_spike',
    'Whether CPU spike is being simulated (0 or 1)'
)

SIMULATED_ERROR_SPIKE = Gauge(
    'app_simulated_error_spike',
    'Whether error spike is being simulated (0 or 1)'
)


def get_metrics():
    """Get Prometheus metrics in text format"""
    return generate_latest(), 200, {'Content-Type': CONTENT_TYPE_LATEST}
