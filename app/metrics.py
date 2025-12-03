"""
Prometheus metrics setup for the Flask application.
"""
from prometheus_client import Counter, Histogram, Gauge, Info, generate_latest, CONTENT_TYPE_LATEST

# Request metrics
REQUEST_COUNT = Counter(
    'app_requests_total',
    'Total number of requests',
    ['method', 'endpoint', 'status']
)

ERROR_COUNT = Counter(
    'app_errors_total',
    'Total number of errors',
    ['endpoint', 'error_type']
)

REQUEST_DURATION = Histogram(
    'app_request_duration_seconds',
    'Request duration in seconds',
    ['method', 'endpoint']
)

# System metrics
CPU_USAGE = Gauge(
    'app_cpu_usage_percent',
    'CPU usage percentage'
)

MEMORY_USAGE = Gauge(
    'app_memory_usage_mb',
    'Memory usage in MB'
)

ACTIVE_CONNECTIONS = Gauge(
    'app_active_connections',
    'Number of active connections'
)

UPTIME = Gauge(
    'app_uptime_seconds',
    'Application uptime in seconds'
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
