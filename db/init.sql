-- Auto-Remediation Bot Database Schema
-- PostgreSQL 15+

-- Enable extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Incidents table: stores all detected incidents
CREATE TABLE IF NOT EXISTS incidents (
    id SERIAL PRIMARY KEY,
    incident_uuid UUID DEFAULT uuid_generate_v4() UNIQUE NOT NULL,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
    type VARCHAR(50) NOT NULL, -- 'health_check_failed', 'high_error_rate', 'cpu_spike', 'high_response_time', 'memory_leak'
    severity VARCHAR(20) NOT NULL CHECK (severity IN ('CRITICAL', 'WARNING', 'INFO')),
    details JSONB DEFAULT '{}', -- Flexible metadata (error_rate value, cpu_percent, etc.)
    status VARCHAR(20) DEFAULT 'ACTIVE' CHECK (status IN ('ACTIVE', 'RESOLVED', 'ESCALATED')),
    resolved_at TIMESTAMP,
    resolution_time_seconds INTEGER,
    affected_service VARCHAR(100), -- 'ar_app', 'ar_app_replica', etc.
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Index for common queries
CREATE INDEX IF NOT EXISTS idx_incidents_timestamp ON incidents(timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_incidents_status ON incidents(status);
CREATE INDEX IF NOT EXISTS idx_incidents_type ON incidents(type);
CREATE INDEX IF NOT EXISTS idx_incidents_severity ON incidents(severity);

-- Remediation actions table: stores all remediation attempts
CREATE TABLE IF NOT EXISTS remediation_actions (
    id SERIAL PRIMARY KEY,
    action_uuid UUID DEFAULT uuid_generate_v4() UNIQUE NOT NULL,
    incident_id INTEGER REFERENCES incidents(id) ON DELETE CASCADE,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
    action_type VARCHAR(50) NOT NULL, -- 'restart_container', 'start_replica', 'stop_replica', 'scale_up', 'scale_down', 'manual'
    target VARCHAR(100) NOT NULL, -- 'ar_app', 'ar_app_replica', etc.
    success BOOLEAN NOT NULL,
    error_message TEXT,
    execution_time_ms INTEGER,
    triggered_by VARCHAR(50) DEFAULT 'bot', -- 'bot', 'manual', 'scheduled'
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Index for performance
CREATE INDEX IF NOT EXISTS idx_remediation_incident ON remediation_actions(incident_id);
CREATE INDEX IF NOT EXISTS idx_remediation_timestamp ON remediation_actions(timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_remediation_action_type ON remediation_actions(action_type);

-- Metrics snapshots table: stores periodic system metrics
CREATE TABLE IF NOT EXISTS metrics_snapshots (
    id SERIAL PRIMARY KEY,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
    service_name VARCHAR(100) DEFAULT 'ar_app',
    total_requests INTEGER DEFAULT 0,
    total_errors INTEGER DEFAULT 0,
    error_rate DECIMAL(5,4) DEFAULT 0.0000,
    cpu_usage_percent DECIMAL(5,2) DEFAULT 0.00,
    memory_usage_mb INTEGER DEFAULT 0,
    response_time_p50_ms INTEGER,
    response_time_p95_ms INTEGER,
    response_time_p99_ms INTEGER,
    active_connections INTEGER DEFAULT 0,
    uptime_seconds INTEGER DEFAULT 0,
    metadata JSONB DEFAULT '{}'
);

-- Index for time-series queries
CREATE INDEX IF NOT EXISTS idx_metrics_timestamp ON metrics_snapshots(timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_metrics_service ON metrics_snapshots(service_name, timestamp DESC);

-- ML metrics history table: stores time-series data for ML training
CREATE TABLE IF NOT EXISTS metrics_history (
    id SERIAL PRIMARY KEY,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
    service_name VARCHAR(100) DEFAULT 'ar_app',
    error_rate DECIMAL(5,4) DEFAULT 0.0000,
    cpu_usage DECIMAL(5,2) DEFAULT 0.00,
    memory_usage DECIMAL(10,2) DEFAULT 0.00,
    response_time DECIMAL(10,2) DEFAULT 0.00,
    request_count INTEGER DEFAULT 0,
    error_count INTEGER DEFAULT 0,
    is_anomaly BOOLEAN DEFAULT FALSE,
    anomaly_score DECIMAL(5,4),
    metadata JSONB DEFAULT '{}'
);

-- Index for ML queries
CREATE INDEX IF NOT EXISTS idx_metrics_history_timestamp ON metrics_history(timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_metrics_history_service ON metrics_history(service_name, timestamp DESC);

-- ML models table: stores trained ML model metadata and binaries
CREATE TABLE IF NOT EXISTS ml_models (
    id SERIAL PRIMARY KEY,
    model_type VARCHAR(100) NOT NULL,
    model_name VARCHAR(200),
    version VARCHAR(50),
    model_data BYTEA,
    accuracy DECIMAL(5,4),
    precision_score DECIMAL(5,4),
    recall DECIMAL(5,4),
    f1_score DECIMAL(5,4),
    training_samples INTEGER,
    is_active BOOLEAN DEFAULT TRUE,
    trained_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    metadata JSONB DEFAULT '{}'
);

-- Index for ML model queries
CREATE INDEX IF NOT EXISTS idx_ml_models_type ON ml_models(model_type);
CREATE INDEX IF NOT EXISTS idx_ml_models_active ON ml_models(is_active);

-- Configuration table: dynamic bot configuration
CREATE TABLE IF NOT EXISTS config (
    id SERIAL PRIMARY KEY,
    key VARCHAR(100) UNIQUE NOT NULL,
    value JSONB NOT NULL,
    description TEXT,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_by VARCHAR(100) DEFAULT 'system'
);

-- Insert default configuration
INSERT INTO config (key, value, description) VALUES
    ('thresholds', '{
        "error_rate": 0.2,
        "cpu_percent": 80,
        "response_time_ms": 500,
        "memory_mb": 1024
    }'::jsonb, 'Detection thresholds for incidents'),
    ('remediation', '{
        "max_restarts_per_5min": 3,
        "cooldown_seconds": 120,
        "enable_auto_scale": true,
        "max_replicas": 3
    }'::jsonb, 'Remediation behavior settings'),
    ('notifications', '{
        "slack_enabled": false,
        "pagerduty_enabled": false,
        "console_logs": true
    }'::jsonb, 'Notification channel settings')
ON CONFLICT (key) DO NOTHING;

-- Circuit breaker state table: tracks circuit breaker status per service
CREATE TABLE IF NOT EXISTS circuit_breaker_state (
    id SERIAL PRIMARY KEY,
    service_name VARCHAR(100) UNIQUE NOT NULL,
    state VARCHAR(20) DEFAULT 'CLOSED' CHECK (state IN ('CLOSED', 'OPEN', 'HALF_OPEN')),
    failure_count INTEGER DEFAULT 0,
    last_failure_time TIMESTAMP,
    opened_at TIMESTAMP,
    last_success_time TIMESTAMP,
    metadata JSONB DEFAULT '{}',
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Insert default circuit breaker states
INSERT INTO circuit_breaker_state (service_name, state) VALUES
    ('ar_app', 'CLOSED'),
    ('ar_app_replica', 'CLOSED')
ON CONFLICT (service_name) DO NOTHING;

-- Action history for rate limiting (sliding window)
CREATE TABLE IF NOT EXISTS action_history (
    id SERIAL PRIMARY KEY,
    service_name VARCHAR(100) NOT NULL,
    action_type VARCHAR(50) NOT NULL,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
    success BOOLEAN NOT NULL
);

-- Index for sliding window queries
CREATE INDEX IF NOT EXISTS idx_action_history_window ON action_history(service_name, action_type, timestamp DESC);

-- Auto-cleanup old action history (keep last 24 hours)
-- This can be run as a periodic job or cron
CREATE OR REPLACE FUNCTION cleanup_old_action_history() RETURNS void AS $$
BEGIN
    DELETE FROM action_history WHERE timestamp < NOW() - INTERVAL '24 hours';
END;
$$ LANGUAGE plpgsql;

-- Function to auto-update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Triggers for auto-updating timestamps
CREATE TRIGGER update_incidents_updated_at BEFORE UPDATE ON incidents
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_config_updated_at BEFORE UPDATE ON config
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_circuit_breaker_updated_at BEFORE UPDATE ON circuit_breaker_state
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Views for common queries

-- Recent incidents view (last 24 hours)
CREATE OR REPLACE VIEW recent_incidents AS
SELECT 
    i.id,
    i.incident_uuid,
    i.timestamp,
    i.type,
    i.severity,
    i.status,
    i.affected_service,
    i.resolution_time_seconds,
    COUNT(ra.id) as remediation_attempts
FROM incidents i
LEFT JOIN remediation_actions ra ON ra.incident_id = i.id
WHERE i.timestamp > NOW() - INTERVAL '24 hours'
GROUP BY i.id
ORDER BY i.timestamp DESC;

-- Remediation success rate view
CREATE OR REPLACE VIEW remediation_stats AS
SELECT 
    action_type,
    target,
    COUNT(*) as total_attempts,
    SUM(CASE WHEN success THEN 1 ELSE 0 END) as successful,
    ROUND(100.0 * SUM(CASE WHEN success THEN 1 ELSE 0 END) / COUNT(*), 2) as success_rate,
    AVG(execution_time_ms) as avg_execution_time_ms
FROM remediation_actions
WHERE timestamp > NOW() - INTERVAL '7 days'
GROUP BY action_type, target
ORDER BY total_attempts DESC;

-- System health summary
CREATE OR REPLACE VIEW system_health_summary AS
SELECT 
    service_name,
    MAX(timestamp) as last_updated,
    (SELECT error_rate FROM metrics_snapshots m2 
     WHERE m2.service_name = m1.service_name 
     ORDER BY timestamp DESC LIMIT 1) as current_error_rate,
    (SELECT cpu_usage_percent FROM metrics_snapshots m2 
     WHERE m2.service_name = m1.service_name 
     ORDER BY timestamp DESC LIMIT 1) as current_cpu_percent,
    (SELECT uptime_seconds FROM metrics_snapshots m2 
     WHERE m2.service_name = m1.service_name 
     ORDER BY timestamp DESC LIMIT 1) as uptime_seconds
FROM metrics_snapshots m1
GROUP BY service_name;

-- Grant permissions (adjust user as needed)
-- GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO remediation_user;
-- GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO remediation_user;
-- GRANT EXECUTE ON ALL FUNCTIONS IN SCHEMA public TO remediation_user;
