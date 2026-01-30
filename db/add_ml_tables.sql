-- ML Tables for Anomaly Detection and Predictive Analytics
-- Run this after initial schema setup

-- Metrics history - stores time series data for ML training
CREATE TABLE IF NOT EXISTS metrics_history (
    id SERIAL PRIMARY KEY,
    timestamp TIMESTAMP NOT NULL,
    
    -- System metrics
    cpu_percent REAL NOT NULL,
    memory_percent REAL NOT NULL,
    memory_mb REAL NOT NULL,
    disk_usage_percent REAL,
    
    -- Application metrics
    request_count INTEGER NOT NULL DEFAULT 0,
    error_count INTEGER NOT NULL DEFAULT 0,
    error_rate REAL NOT NULL DEFAULT 0.0,
    active_connections INTEGER DEFAULT 0,
    
    -- Performance metrics
    response_time_p50 REAL,
    response_time_p95 REAL,
    response_time_p99 REAL,
    response_time_avg REAL,
    
    -- Derived features for ML
    cpu_rate_of_change REAL,
    memory_rate_of_change REAL,
    error_rate_trend REAL,
    
    created_at TIMESTAMP DEFAULT NOW()
);

-- Indexes for time-based queries
CREATE INDEX IF NOT EXISTS idx_metrics_history_timestamp ON metrics_history(timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_metrics_history_created_at ON metrics_history(created_at DESC);

-- Anomaly scores - stores ML model predictions
CREATE TABLE IF NOT EXISTS anomaly_scores (
    id SERIAL PRIMARY KEY,
    timestamp TIMESTAMP NOT NULL,
    
    -- Anomaly detection results
    anomaly_score REAL NOT NULL,  -- -1.0 (normal) to 1.0 (anomaly)
    is_anomaly BOOLEAN NOT NULL DEFAULT FALSE,
    severity VARCHAR(20),  -- LOW, MEDIUM, HIGH, CRITICAL
    
    -- Model information
    model_name VARCHAR(100) NOT NULL,
    model_version VARCHAR(50),
    
    -- Contributing features (JSON array)
    contributing_features JSONB,
    
    -- Linked metrics
    metrics_snapshot JSONB,
    
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_anomaly_scores_timestamp ON anomaly_scores(timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_anomaly_scores_is_anomaly ON anomaly_scores(is_anomaly);

-- ML models registry - tracks model versions and performance
CREATE TABLE IF NOT EXISTS ml_models (
    id SERIAL PRIMARY KEY,
    
    -- Model identification
    model_name VARCHAR(100) NOT NULL,
    model_type VARCHAR(50) NOT NULL,  -- isolation_forest, prophet, lightgbm, etc.
    version VARCHAR(50) NOT NULL,
    
    -- Training information
    trained_at TIMESTAMP NOT NULL,
    training_data_start TIMESTAMP,
    training_data_end TIMESTAMP,
    training_samples_count INTEGER,
    
    -- Model performance metrics (JSON)
    metrics JSONB,  -- accuracy, precision, recall, f1_score, etc.
    
    -- Model storage
    file_path VARCHAR(255),
    file_size_mb REAL,
    
    -- Deployment status
    is_active BOOLEAN DEFAULT FALSE,
    deployed_at TIMESTAMP,
    
    -- Metadata
    training_config JSONB,
    notes TEXT,
    
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_ml_models_name_version ON ml_models(model_name, version);
CREATE INDEX IF NOT EXISTS idx_ml_models_active ON ml_models(is_active);

-- Failure predictions - stores predictions from failure predictor
CREATE TABLE IF NOT EXISTS failure_predictions (
    id SERIAL PRIMARY KEY,
    timestamp TIMESTAMP NOT NULL,
    
    -- Prediction results
    failure_probability REAL NOT NULL,  -- 0.0 to 1.0
    time_to_failure_minutes INTEGER,
    confidence_score REAL,
    
    -- Contributing patterns (JSON)
    contributing_patterns JSONB,
    risk_level VARCHAR(20),  -- LOW, MEDIUM, HIGH, CRITICAL
    
    -- Model information
    model_version VARCHAR(50),
    
    -- Current metrics snapshot
    current_metrics JSONB,
    
    -- Action taken
    action_taken VARCHAR(100),
    action_timestamp TIMESTAMP,
    
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_failure_predictions_timestamp ON failure_predictions(timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_failure_predictions_probability ON failure_predictions(failure_probability DESC);

-- Forecasts - stores time series predictions
CREATE TABLE IF NOT EXISTS metric_forecasts (
    id SERIAL PRIMARY KEY,
    
    -- Forecast information
    metric_name VARCHAR(100) NOT NULL,  -- cpu_percent, memory_percent, etc.
    forecast_timestamp TIMESTAMP NOT NULL,  -- When forecast was generated
    predicted_timestamp TIMESTAMP NOT NULL,  -- Time point being predicted
    
    -- Prediction values
    predicted_value REAL NOT NULL,
    lower_bound REAL,
    upper_bound REAL,
    
    -- Model information
    model_name VARCHAR(100),
    model_version VARCHAR(50),
    
    -- Trend analysis
    trend VARCHAR(20),  -- increasing, decreasing, stable
    seasonality_detected BOOLEAN,
    
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_forecasts_metric_timestamp ON metric_forecasts(metric_name, forecast_timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_forecasts_predicted_timestamp ON metric_forecasts(predicted_timestamp);

-- LLM analysis results - stores AI-generated insights
CREATE TABLE IF NOT EXISTS llm_analyses (
    id SERIAL PRIMARY KEY,
    
    -- Linked entity
    incident_id INTEGER REFERENCES incidents(id),
    analysis_type VARCHAR(50),  -- incident_summary, root_cause, remediation_suggestion
    
    -- LLM information
    llm_provider VARCHAR(50),  -- ollama, huggingface, etc.
    llm_model VARCHAR(100),
    
    -- Analysis results
    summary TEXT,
    root_cause TEXT,
    suggested_actions JSONB,  -- Array of action strings
    confidence_score REAL,
    
    -- Context used
    input_context JSONB,
    
    -- User feedback
    user_rating INTEGER,  -- 1-5 stars
    user_feedback TEXT,
    
    -- Timing
    processing_time_ms INTEGER,
    
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_llm_analyses_incident ON llm_analyses(incident_id);
CREATE INDEX IF NOT EXISTS idx_llm_analyses_type ON llm_analyses(analysis_type);

-- Create view for recent metrics (last 24 hours) for quick access
CREATE OR REPLACE VIEW recent_metrics AS
SELECT 
    timestamp,
    cpu_percent,
    memory_percent,
    error_rate,
    response_time_p95,
    active_connections
FROM metrics_history
WHERE timestamp > NOW() - INTERVAL '24 hours'
ORDER BY timestamp DESC;

-- Create view for active models
CREATE OR REPLACE VIEW active_ml_models AS
SELECT 
    model_name,
    model_type,
    version,
    trained_at,
    metrics,
    deployed_at
FROM ml_models
WHERE is_active = TRUE
ORDER BY deployed_at DESC;

-- Function to clean old metrics data (retention policy)
CREATE OR REPLACE FUNCTION cleanup_old_metrics(retention_days INTEGER DEFAULT 90)
RETURNS INTEGER AS $$
DECLARE
    deleted_count INTEGER;
BEGIN
    DELETE FROM metrics_history 
    WHERE timestamp < NOW() - (retention_days || ' days')::INTERVAL;
    
    GET DIAGNOSTICS deleted_count = ROW_COUNT;
    RETURN deleted_count;
END;
$$ LANGUAGE plpgsql;

-- Function to get latest anomaly score
CREATE OR REPLACE FUNCTION get_latest_anomaly_score()
RETURNS TABLE (
    timestamp TIMESTAMP,
    anomaly_score REAL,
    is_anomaly BOOLEAN,
    severity VARCHAR(20)
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        a.timestamp,
        a.anomaly_score,
        a.is_anomaly,
        a.severity
    FROM anomaly_scores a
    ORDER BY a.timestamp DESC
    LIMIT 1;
END;
$$ LANGUAGE plpgsql;

-- Grant permissions
GRANT SELECT, INSERT, UPDATE ON metrics_history TO remediation_user;
GRANT SELECT, INSERT, UPDATE ON anomaly_scores TO remediation_user;
GRANT SELECT, INSERT, UPDATE ON ml_models TO remediation_user;
GRANT SELECT, INSERT, UPDATE ON failure_predictions TO remediation_user;
GRANT SELECT, INSERT, UPDATE ON metric_forecasts TO remediation_user;
GRANT SELECT, INSERT, UPDATE ON llm_analyses TO remediation_user;

GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public TO remediation_user;

-- Success message
DO $$
BEGIN
    RAISE NOTICE 'ML tables created successfully!';
    RAISE NOTICE 'Tables: metrics_history, anomaly_scores, ml_models, failure_predictions, metric_forecasts, llm_analyses';
    RAISE NOTICE 'Views: recent_metrics, active_ml_models';
    RAISE NOTICE 'Functions: cleanup_old_metrics(), get_latest_anomaly_score()';
END $$;
