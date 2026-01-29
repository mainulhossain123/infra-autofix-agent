"""
Prometheus metrics endpoint for the remediation bot.
"""
from flask import Flask, Response
from prometheus_client import Counter, Histogram, Gauge, Info, generate_latest, CONTENT_TYPE_LATEST
import psutil
import time

app = Flask(__name__)

# Bot start time for uptime calculation
BOT_START_TIME = time.time()

# Remediation metrics
REMEDIATION_ACTIONS = Counter(
    'remediation_actions_total',
    'Total number of remediation actions performed',
    ['action_type', 'target']
)

REMEDIATION_FAILURES = Counter(
    'remediation_failures_total',
    'Total number of failed remediation actions',
    ['action_type', 'error_type']
)

REMEDIATION_DURATION = Histogram(
    'remediation_duration_seconds',
    'Time taken to complete remediation actions',
    ['action_type'],
    buckets=[1, 5, 10, 30, 60, 120, 300]
)

# Circuit breaker metrics
CIRCUIT_BREAKER_STATE = Gauge(
    'circuit_breaker_state',
    'Circuit breaker state (0=closed, 1=open)',
    ['service']
)

CIRCUIT_BREAKER_TRIPS = Counter(
    'circuit_breaker_trips_total',
    'Number of times circuit breaker tripped',
    ['service', 'reason']
)

# Detection metrics
DETECTIONS_TOTAL = Counter(
    'detections_total',
    'Total number of anomalies detected',
    ['detector_type']
)

FALSE_POSITIVES = Counter(
    'false_positives_total',
    'Number of false positive detections',
    ['detector_type']
)

# System health metrics
BOT_CPU_USAGE = Gauge(
    'bot_cpu_usage_percent',
    'Bot CPU usage percentage'
)

BOT_MEMORY_USAGE = Gauge(
    'bot_memory_usage_mb',
    'Bot memory usage in MB'
)

BOT_UPTIME = Gauge(
    'bot_uptime_seconds',
    'Bot uptime in seconds'
)

# Docker metrics
DOCKER_CONTAINERS_MONITORED = Gauge(
    'docker_containers_monitored',
    'Number of Docker containers being monitored'
)

DOCKER_API_ERRORS = Counter(
    'docker_api_errors_total',
    'Number of Docker API errors',
    ['error_type']
)

# Notification metrics
NOTIFICATIONS_SENT = Counter(
    'notifications_sent_total',
    'Total number of notifications sent',
    ['channel', 'type']
)

NOTIFICATION_FAILURES = Counter(
    'notification_failures_total',
    'Number of failed notification attempts',
    ['channel', 'error_type']
)

# Bot info
BOT_INFO = Info(
    'bot_info',
    'Bot information'
)


def update_system_metrics():
    """Update system resource metrics"""
    try:
        # CPU usage
        cpu_percent = psutil.cpu_percent(interval=1)
        BOT_CPU_USAGE.set(cpu_percent)
        
        # Memory usage
        process = psutil.Process()
        memory_mb = process.memory_info().rss / 1024 / 1024
        BOT_MEMORY_USAGE.set(memory_mb)
        
        # Uptime
        uptime = time.time() - BOT_START_TIME
        BOT_UPTIME.set(uptime)
        
    except Exception as e:
        print(f"Error updating system metrics: {e}")


@app.route('/metrics')
def metrics():
    """Expose Prometheus metrics"""
    update_system_metrics()
    return Response(generate_latest(), mimetype=CONTENT_TYPE_LATEST)


@app.route('/health')
def health():
    """Health check endpoint"""
    return {'status': 'healthy', 'uptime': time.time() - BOT_START_TIME}, 200


if __name__ == '__main__':
    # Set bot info
    BOT_INFO.info({
        'version': '1.0.0',
        'name': 'infra-autofix-bot',
        'python_version': '3.11'
    })
    
    # Run metrics server on port 8000
    app.run(host='0.0.0.0', port=8000, debug=False)
