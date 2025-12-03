-- Sample seed data for testing and demos
-- Run this after init.sql

-- Insert sample historical incidents
INSERT INTO incidents (timestamp, type, severity, details, status, resolved_at, resolution_time_seconds, affected_service)
VALUES 
    (NOW() - INTERVAL '2 hours', 'health_check_failed', 'CRITICAL', '{"reason": "connection_timeout", "timeout_ms": 3000}'::jsonb, 'RESOLVED', NOW() - INTERVAL '2 hours' + INTERVAL '45 seconds', 45, 'ar_app'),
    (NOW() - INTERVAL '1 hour', 'high_error_rate', 'WARNING', '{"error_rate": 0.25, "threshold": 0.2}'::jsonb, 'RESOLVED', NOW() - INTERVAL '1 hour' + INTERVAL '2 minutes', 120, 'ar_app'),
    (NOW() - INTERVAL '30 minutes', 'cpu_spike', 'WARNING', '{"cpu_percent": 85, "threshold": 80}'::jsonb, 'RESOLVED', NOW() - INTERVAL '30 minutes' + INTERVAL '1 minute', 60, 'ar_app'),
    (NOW() - INTERVAL '10 minutes', 'high_response_time', 'INFO', '{"p95_ms": 650, "threshold": 500}'::jsonb, 'RESOLVED', NOW() - INTERVAL '10 minutes' + INTERVAL '30 seconds', 30, 'ar_app');

-- Insert corresponding remediation actions
INSERT INTO remediation_actions (incident_id, timestamp, action_type, target, success, execution_time_ms, triggered_by)
VALUES 
    (1, NOW() - INTERVAL '2 hours' + INTERVAL '5 seconds', 'restart_container', 'ar_app', true, 3456, 'bot'),
    (2, NOW() - INTERVAL '1 hour' + INTERVAL '5 seconds', 'start_replica', 'ar_app_replica', true, 5234, 'bot'),
    (2, NOW() - INTERVAL '1 hour' + INTERVAL '1 minute', 'restart_container', 'ar_app', true, 3122, 'bot'),
    (3, NOW() - INTERVAL '30 minutes' + INTERVAL '5 seconds', 'start_replica', 'ar_app_replica', true, 4987, 'bot'),
    (4, NOW() - INTERVAL '10 minutes' + INTERVAL '5 seconds', 'restart_container', 'ar_app', true, 3345, 'bot');

-- Insert sample metrics snapshots (last hour, every 5 minutes)
INSERT INTO metrics_snapshots (timestamp, service_name, total_requests, total_errors, error_rate, cpu_usage_percent, memory_usage_mb, response_time_p50_ms, response_time_p95_ms, response_time_p99_ms, uptime_seconds)
SELECT 
    NOW() - (interval '5 minutes' * generate_series(12, 0, -1)),
    'ar_app',
    1000 + (random() * 500)::int,
    (random() * 50)::int,
    (random() * 0.1)::decimal(5,4),
    (50 + random() * 40)::decimal(5,2),
    (400 + random() * 200)::int,
    (80 + random() * 40)::int,
    (200 + random() * 300)::int,
    (500 + random() * 500)::int,
    (3600 + generate_series(12, 0, -1) * 300);
