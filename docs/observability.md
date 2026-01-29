# Observability & Monitoring Guide

Complete guide to monitoring your infra-autofix-agent with Prometheus, Grafana, and Loki.

## 🚀 Quick Start for Beginners

**New to monitoring? Start here!**

### 1. Verify Everything is Running

```powershell
# Check all services are up
docker compose ps

# You should see these running:
# ar_app, ar_bot, ar_frontend, ar_postgres
# ar_prometheus, ar_grafana, ar_loki, ar_promtail
```

### 2. Open Your Monitoring Tools

```powershell
# Main dashboard (for daily use)
start http://localhost:3001
# Login: admin / admin

# Metrics database (for detailed queries)
start http://localhost:9090

# Application frontend
start http://localhost:3000
```

### 3. Your First 5 Minutes

**In Grafana (http://localhost:3001):**
1. Click **Dashboards** (four squares icon) → Select **"Infrastructure Auto-Fix Overview"**
2. Watch real-time graphs update every 5 seconds
3. Change time range (top-right) to see historical data
4. Hover over graphs to see exact values

**In Prometheus (http://localhost:9090):**
1. Type `http_requests_total` in query box
2. Click **Execute**
3. Click **Graph** tab to visualize
4. Try: `app_cpu_usage_percent` to see CPU usage

### 4. Test the System

Trigger a fake incident to see monitoring in action:

```powershell
# Simulate high CPU for 30 seconds
curl -X POST http://localhost:5000/api/trigger/cpu-spike?duration=30

# Now watch in Grafana:
# - CPU graph should spike
# - After ~5 minutes, alert might fire
# - Bot should detect and log the issue
```

### 5. Common Tasks

| Want to... | Where to Go | What to Do |
|------------|-------------|------------|
| See if system is healthy | Grafana → Infrastructure Overview | Check all graphs trending normal |
| Find error logs | Grafana → Explore → Loki | Query: `{service="app"} \|= "ERROR"` |
| Check bot activity | Grafana → Incident Analysis | View "Remediation Activity" panel |
| Measure performance | Prometheus | Query: `histogram_quantile(0.95, rate(http_request_duration_seconds_bucket[5m]))` |
| View active alerts | Prometheus → Alerts | See red items = firing alerts |

---

## Table of Contents

- [Overview](#overview)
- [Architecture](#architecture)
- [Grafana Dashboards](#grafana-dashboards)
- [Prometheus Metrics](#prometheus-metrics)
- [Loki Logs](#loki-logs)
- [Alerting](#alerting)
- [Best Practices](#best-practices)
- [Troubleshooting](#troubleshooting)

---

## Overview

The observability stack consists of:

1. **Prometheus** - Metrics collection and storage
2. **Grafana** - Visualization and dashboards
3. **Loki** - Log aggregation
4. **Promtail** - Log shipping
5. **Custom metrics** - Application-specific instrumentation

### Why Observability Matters

- **Detect issues before users do** - Real-time monitoring catches problems early
- **Debug faster** - Correlated metrics and logs speed up troubleshooting
- **Understand system behavior** - Historical data reveals patterns and trends
- **Capacity planning** - Resource usage metrics guide infrastructure decisions
- **Compliance & auditing** - Centralized logs meet regulatory requirements

---

## Architecture

```
┌─────────────┐     ┌──────────────┐     ┌──────────────┐
│   Flask App │────▶│  Prometheus  │────▶│   Grafana    │
│  (port 5000)│     │  (port 9090) │     │ (port 3001)  │
└─────────────┘     └──────────────┘     └──────────────┘
       │                                          │
       │                                          ▼
       │            ┌──────────────┐     ┌──────────────┐
       │            │     Loki     │────▶│   Grafana    │
       │            │  (port 3100) │     │    Explore   │
       │            └──────────────┘     └──────────────┘
       │                     ▲
       │                     │
       ▼                     │
┌─────────────┐     ┌──────────────┐
│     Bot     │     │   Promtail   │
│  (port 8000)│     │  (log agent) │
└─────────────┘     └──────────────┘
       │                     ▲
       │                     │
       └─────────────────────┘
         Docker container logs
```

---

## Grafana Dashboards

### Quick Start (Step-by-Step)

**1. Open Grafana:**
```powershell
# In your browser, navigate to:
start http://localhost:3001
```

**2. Login:**
- Username: `admin`
- Password: `admin`
- (You'll be prompted to change password on first login)

**3. View Pre-built Dashboards:**
- Click **Dashboards** icon (four squares) in left sidebar
- Select **"Infrastructure Auto-Fix Overview"** or **"Incident & Remediation Analysis"**

**4. Explore Data:**
- Use time picker (top right) to change range: Last 5m, 15m, 1h, 6h, 24h
- Click on any graph to zoom into that time period
- Hover over data points to see exact values

### Pre-built Dashboards

#### 1. Infrastructure Auto-Fix Overview

**Purpose**: High-level system health and performance

**Panels**:
- Application Status (up/down)
- Request Rate (requests/second by status code)
- P95 Response Time (95th percentile latency)
- Total Incidents
- CPU Usage (percentage over time)
- Memory Usage (bytes over time)
- Remediation Activity (actions and failures)

**Use cases**:
- Daily health checks
- Performance monitoring during load tests
- Capacity planning
- Executive dashboards

**Refresh interval**: 5 seconds

#### 2. Incident & Remediation Analysis

**Purpose**: Deep dive into incidents and bot activity

**Panels**:
- Application Error Logs (real-time from Loki)
- Incidents Over Time (histogram by hour)
- Incidents by Type (pie chart)
- Remediation Bot Logs (filtered by "remediation" keyword)

**Use cases**:
- Incident investigation
- Post-mortem analysis
- Bot effectiveness evaluation
- Anomaly detection tuning

**Refresh interval**: 10 seconds

### Creating Custom Dashboards

1. Click **+ Create** → **Dashboard**
2. **Add panel** → Select data source (Prometheus or Loki)
3. Write PromQL or LogQL query
4. Configure visualization (time series, gauge, stat, logs, etc.)
5. **Save dashboard**

**Example query** (Prometheus):
```promql
rate(http_requests_total[5m])
```

**Example query** (Loki):
```logql
{service="app"} |= "ERROR" | json
```

---

## Prometheus Metrics

### Quick Start (Step-by-Step)

**1. Open Prometheus:**
```powershell
start http://localhost:9090
```

**2. Check Targets (Verify Data Collection):**
- Click **Status** → **Targets** in top menu
- You should see:
  - `app:5000/metrics` - State: **UP** ✅
  - `bot:8000/metrics` - State: **UP** ✅
- If "DOWN", check Docker containers are running: `docker compose ps`

**3. Run Your First Query:**
- Click **Query** in top menu
- In the expression box, type: `http_requests_total`
- Click **Execute** button
- Click **Graph** tab to visualize

**4. Try These Beginner-Friendly Queries:**

```promql
# How many requests per second?
rate(http_requests_total[5m])

# What's my app's memory usage in MB?
app_memory_usage_bytes / 1024 / 1024

# How many incidents have been detected?
incidents_total

# What's the error rate percentage?
(rate(http_requests_total{status=~"5.."}[5m]) / rate(http_requests_total[5m])) * 100
```

**5. Change Time Range:**
- Use dropdown in top-right corner
- Select: Last 5m, 15m, 1h, 6h, 24h, or custom range

### Common Use Cases with Commands

#### Use Case 1: Check if App is Running Normally

**Query:**
```promql
up{job="app"}
```
**Result:** `1` = running, `0` = down

#### Use Case 2: Find Performance Bottlenecks

**Query for 95th percentile latency (slowest 5% of requests):**
```promql
histogram_quantile(0.95, rate(http_request_duration_seconds_bucket[5m]))
```
**Good:** < 0.5 seconds | **Investigate:** > 1 second

#### Use Case 3: Monitor Bot Activity

**Query for remediations per minute:**
```promql
rate(remediation_actions_total[1m]) * 60
```
**Result:** Number of container restarts/fixes per minute

#### Use Case 4: Detect High Error Rate

**Query for error percentage:**
```promql
(
  sum(rate(http_requests_total{status=~"5.."}[5m])) 
  / 
  sum(rate(http_requests_total[5m]))
) * 100
```
**Alert if:** > 5%

### Available Metrics

#### HTTP Metrics

| Metric | Type | Description | Labels |
|--------|------|-------------|--------|
| `http_requests_total` | Counter | Total HTTP requests | method, endpoint, status |
| `http_errors_total` | Counter | Total HTTP errors | endpoint, error_type |
| `http_request_duration_seconds` | Histogram | Request duration | method, endpoint |

**Example queries**:
```promql
# Request rate by status code
rate(http_requests_total[5m])

# Error rate
rate(http_requests_total{status=~"5.."}[5m]) / rate(http_requests_total[5m])

# P95 latency
histogram_quantile(0.95, rate(http_request_duration_seconds_bucket[5m]))
```

#### System Metrics

| Metric | Type | Description |
|--------|------|-------------|
| `process_cpu_seconds_total` | Gauge | Total CPU time |
| `process_resident_memory_bytes` | Gauge | Memory usage in bytes |
| `app_uptime_seconds` | Gauge | Application uptime |
| `app_active_connections` | Gauge | Active connections |

**Example queries**:
```promql
# CPU usage rate
rate(process_cpu_seconds_total[1m])

# Memory in MB
process_resident_memory_bytes / 1024 / 1024

# Uptime in hours
app_uptime_seconds / 3600
```

#### Incident Metrics

| Metric | Type | Description | Labels |
|--------|------|-------------|--------|
| `incidents_total` | Gauge | Total incidents | - |
| `incidents_by_type` | Gauge | Incidents by type | type |
| `incidents_by_severity` | Gauge | Incidents by severity | severity |

#### Remediation Metrics (Bot)

| Metric | Type | Description | Labels |
|--------|------|-------------|--------|
| `remediation_actions_total` | Counter | Total actions performed | action_type, target |
| `remediation_failures_total` | Counter | Failed actions | action_type, error_type |
| `remediation_duration_seconds` | Histogram | Action duration | action_type |
| `circuit_breaker_state` | Gauge | Circuit breaker status (0=closed, 1=open) | service |
| `detections_total` | Counter | Anomalies detected | detector_type |

**Example queries**:
```promql
# Remediation rate
rate(remediation_actions_total[10m])

# Failure rate
rate(remediation_failures_total[5m]) / rate(remediation_actions_total[5m])

# Circuit breaker open count
count(circuit_breaker_state == 1)
```

#### Database Metrics

| Metric | Type | Description | Labels |
|--------|------|-------------|--------|
| `database_query_duration_seconds` | Histogram | Query duration | operation |
| `database_errors_total` | Counter | Database errors | operation, error_type |
| `database_connection_pool_size` | Gauge | Connection pool size | - |

### Writing PromQL Queries

**Rate functions** (for counters):
```promql
rate(http_requests_total[5m])  # Per-second rate over 5 minutes
increase(incidents_total[1h])   # Total increase over 1 hour
```

**Aggregation**:
```promql
sum(rate(http_requests_total[5m])) by (status)      # Sum by status
avg(http_request_duration_seconds) by (endpoint)    # Average by endpoint
```

**Filtering**:
```promql
http_requests_total{status="200"}              # Only 200s
http_requests_total{status=~"5.."}             # All 5xx codes
http_requests_total{endpoint!="/health"}       # Exclude health
```

---

## Loki Logs

### Quick Start (Step-by-Step)

**1. Open Grafana Explore:**
```powershell
start http://localhost:3001/explore
```

**2. Select Loki Data Source:**
- In dropdown at top, select **"Loki"**

**3. Run Your First Log Query:**
- In the query box, type: `{service="app"}`
- Click **Run query** button
- You'll see live logs from your Flask application

**4. Try These Useful Log Queries:**

```logql
# All error logs
{service="app"} |= "ERROR"

# Bot activity logs
{service="bot"} |= "remediation"

# Logs from last 5 minutes with "incident"
{service="app"} |= "incident"

# Count errors per minute
rate({service="app"} |= "ERROR" [1m])
```

**5. Filter by Time:**
- Use time picker in top-right
- Select: Last 5m, 15m, 1h, 3h, or custom

### Common Log Investigation Tasks

#### Task 1: Find What Caused Recent Errors

**Steps:**
1. Open Grafana Explore → Select Loki
2. Run query: `{service="app"} |= "ERROR"`
3. Set time to "Last 15 minutes"
4. Read error messages and stack traces
5. Note timestamps for correlation with Prometheus metrics

#### Task 2: Check if Bot Successfully Restarted Containers

**Query:**
```logql
{service="bot"} |= "restart_container" |= "success"
```

**Look for log lines like:**
```
Successfully restarted container ar_app
```

#### Task 3: Monitor Real-time Application Activity

**Query for live tail (updates automatically):**
```logql
{service="app"}
```

Click the **Live** button in top-right to enable live streaming logs.

#### Task 4: Find Slow Database Queries

**Query:**
```logql
{service="app"} |= "database_query_duration" | json | duration > 1.0
```

### LogQL Query Language

**Basic syntax**:
```logql
{label="value"} |= "search text" | parser | filter
```

**Examples**:

```logql
# All app logs
{service="app"}

# Error logs from all services
{service=~"app|bot"} |= "ERROR"

# Bot remediation logs
{service="bot"} |= "remediation"

# JSON parsing
{service="app"} | json | level="error"

# Rate calculation
rate({service="app"} |= "ERROR" [5m])
```

### Log Labels

Automatic labels from Docker:
- `container` - Container name
- `service` - Docker Compose service name
- `stream` - stdout or stderr

### Log Retention

Configured in `loki/loki-config.yml`:
- **Retention period**: 168 hours (7 days)
- **Old sample rejection**: 168 hours

To change retention:
```yaml
limits_config:
  retention_period: 720h  # 30 days
```

---

## Alerting

### Quick Start (Step-by-Step)

**1. View Active Alerts in Prometheus:**
```powershell
start http://localhost:9090/alerts
```

**2. Check Alert Status:**
- **Green (Inactive):** Everything normal
- **Yellow (Pending):** Condition met but waiting for duration
- **Red (Firing):** Alert triggered! Take action

**3. Test an Alert:**

Trigger high CPU (manual test):
```powershell
# In another terminal, trigger CPU spike
curl -X POST http://localhost:5000/api/trigger/cpu-spike?duration=10
```

Then watch Prometheus alerts page - "HighCPUUsage" should turn yellow, then red.

### Configured Alerts

Located in `prometheus/alerts.yml`:

#### Application Alerts

1. **HighErrorRate**
   - Condition: Error rate > 5% for 2 minutes
   - Severity: Critical

2. **HighCPUUsage**
   - Condition: CPU > 80% for 5 minutes
   - Severity: Warning

3. **ApplicationDown**
   - Condition: App unreachable for 1 minute
   - Severity: Critical

4. **HighResponseTime**
   - Condition: P95 > 500ms for 3 minutes
   - Severity: Warning

#### Remediation Alerts

1. **FrequentRemediations**
   - Condition: >0.5 actions/sec for 5 minutes
   - Severity: Warning

2. **RemediationFailures**
   - Condition: >0.1 failures/sec for 2 minutes
   - Severity: Critical

3. **CircuitBreakerOpen**
   - Condition: Circuit breaker open for 1 minute
   - Severity: Warning

### Viewing Alerts

**In Prometheus**:
1. Go to http://localhost:9090/alerts
2. View active, pending, and firing alerts

**In Grafana**:
1. Alerting → Alert rules
2. Create alert rules from dashboard panels

### Setting Up Alertmanager (Optional)

To send notifications (Slack, email, PagerDuty):

1. Add Alertmanager to `docker-compose.yml`:
```yaml
alertmanager:
  image: prom/alertmanager:latest
  ports:
    - "9093:9093"
  volumes:
    - ./alertmanager/config.yml:/etc/alertmanager/config.yml
  networks:
    - remediation_network
```

2. Configure `alertmanager/config.yml`:
```yaml
route:
  receiver: 'slack'
  group_wait: 10s
  group_interval: 10s
  repeat_interval: 1h

receivers:
  - name: 'slack'
    slack_configs:
      - api_url: 'YOUR_SLACK_WEBHOOK_URL'
        channel: '#alerts'
        text: '{{ range .Alerts }}{{ .Annotations.summary }}\n{{ end }}'
```

3. Uncomment alerting section in `prometheus/prometheus.yml`

---

## Best Practices

### Metrics

✅ **DO**:
- Use counters for things that only increase (requests, errors)
- Use gauges for values that can go up and down (memory, connections)
- Use histograms for latency measurements
- Add meaningful labels (but not too many - avoid high cardinality)
- Expose health check endpoints

❌ **DON'T**:
- Use high-cardinality labels (user IDs, timestamps)
- Create too many metrics (aim for <100 per service)
- Forget to instrument new endpoints

### Dashboards

✅ **DO**:
- Start with pre-built dashboards
- Use consistent color schemes
- Add annotations for deployments
- Set appropriate refresh intervals
- Include context in panel titles

❌ **DON'T**:
- Cram too many panels on one dashboard
- Use complex queries without testing
- Forget to save changes

### Alerts

✅ **DO**:
- Alert on symptoms, not causes
- Use appropriate severity levels
- Add runbook links in annotations
- Test alerts before deploying
- Group related alerts

❌ **DON'T**:
- Alert on everything (alert fatigue)
- Use overly sensitive thresholds
- Forget to handle flapping

### Logs

✅ **DO**:
- Use structured logging (JSON)
- Include correlation IDs
- Log at appropriate levels
- Add context to error logs

❌ **DON'T**:
- Log sensitive data (passwords, tokens)
- Log too verbosely in production
- Forget to rotate logs

---

## Troubleshooting

### Common Issues with Step-by-Step Fixes

#### Issue 1: Grafana Shows "No Data"

**Symptom:** Dashboard panels are empty or show "No data"

**Fix Steps:**
```powershell
# Step 1: Verify Grafana is running
docker ps | Select-String grafana
# Should show: ar_grafana ... Up

# Step 2: Check Prometheus targets are UP
start http://localhost:9090/targets
# Both app:5000 and bot:8000 should show State: UP

# Step 3: Test if metrics exist
start http://localhost:9090
# Run query: http_requests_total
# Should return data

# Step 4: Verify Grafana data source
start http://localhost:3001/datasources
# Prometheus should show green checkmark "Data source is working"

# Step 5: If still broken, restart Grafana
docker restart ar_grafana
```

#### Issue 2: Prometheus Not Collecting Metrics

**Symptom:** Targets show "DOWN" in http://localhost:9090/targets

**Fix Steps:**
```powershell
# Check if app/bot containers are running
docker compose ps
# Should show ar_app and ar_bot as "running"

# Check app metrics endpoint
curl http://localhost:5000/metrics
# Should return Prometheus format metrics

# Check bot metrics endpoint  
curl http://localhost:8000/metrics
# Should return Prometheus format metrics

# If containers aren't running, restart stack
docker compose restart

# View container logs for errors
docker logs ar_app
docker logs ar_bot
```

#### Issue 3: Loki Logs Not Appearing

**Symptom:** No logs in Grafana Explore when querying Loki

**Fix Steps:**
```powershell
# Step 1: Check Loki is running
docker ps | Select-String loki
# Should show ar_loki and ar_promtail

# Step 2: Check Loki health
curl http://localhost:3100/ready
# Should return "ready"

# Step 3: Check Promtail is shipping logs
docker logs ar_promtail
# Should see: "Successfully sent batch"

# Step 4: Restart Promtail if needed
docker restart ar_promtail

# Step 5: Verify Loki data source in Grafana
start http://localhost:3001/datasources
```

#### Issue 4: Alerts Not Firing

**Symptom:** High CPU but no alert showing in Prometheus

**Fix Steps:**
```powershell
# Step 1: Check alert rules loaded
start http://localhost:9090/rules
# Should see list of alert rules

# Step 2: Check if condition is actually met
start http://localhost:9090
# Run: app_cpu_usage_percent > 80
# If returns nothing, CPU isn't actually high

# Step 3: Manually trigger test
curl -X POST http://localhost:5000/api/trigger/cpu-spike?duration=600
# Wait 5 minutes, check alerts page

# Step 4: Check Prometheus config
docker exec ar_prometheus cat /etc/prometheus/prometheus.yml | Select-String alert
```

#### Issue 5: Container Keeps Restarting

**Symptom:** `docker ps` shows container constantly restarting

**Fix Steps:**
```powershell
# Check logs for error
docker logs ar_app --tail 50

# Common fixes:
# 1. Database not ready - wait 30 seconds
# 2. Port already in use - check: netstat -ano | Select-String 5000
# 3. Config error - check .env file exists

# Force rebuild if needed
docker compose up --build ar_app
```

### Quick Diagnostic Commands

**Full system health check:**
```powershell
# All containers running?
docker compose ps

# Any errors in logs?
docker compose logs --tail 20

# Check ports
netstat -ano | Select-String "3000|5000|8000|9090|3001|3100"

# Resource usage
docker stats --no-stream
```

### Grafana Issues

**Problem**: Can't access Grafana at localhost:3001

**Solutions**:
```powershell
# Check if container is running
docker ps | Select-String grafana

# View Grafana logs
docker logs ar_grafana

# Restart Grafana
docker restart ar_grafana
```

**Problem**: Dashboards show "No data"

**Solutions**:
1. Check data source connection: Configuration → Data sources
2. Verify Prometheus is scraping: http://localhost:9090/targets
3. Check metric names in Prometheus: http://localhost:9090/graph
4. Ensure time range is appropriate

### Prometheus Issues

**Problem**: Targets are down

**Solutions**:
```powershell
# Check target status
curl http://localhost:9090/api/v1/targets

# Verify app is exposing metrics
curl http://localhost:5000/metrics
curl http://localhost:8000/metrics

# Check network connectivity
docker exec ar_prometheus ping app
```

**Problem**: Metrics not appearing

**Solutions**:
1. Check `prometheus.yml` configuration
2. Restart Prometheus to reload config:
```powershell
docker restart ar_prometheus
```
3. Verify scrape interval hasn't expired

### Loki Issues

**Problem**: Logs not showing in Grafana

**Solutions**:
```powershell
# Check Loki is running
curl http://localhost:3100/ready

# View Promtail logs
docker logs ar_promtail

# Test Loki query API
curl -G -s "http://localhost:3100/loki/api/v1/query_range" --data-urlencode 'query={service="app"}' | jq
```

**Problem**: Promtail not collecting logs

**Solutions**:
1. Verify Docker socket is mounted
2. Check Promtail configuration
3. Ensure containers have proper labels

### Performance Issues

**Problem**: Grafana slow or timing out

**Solutions**:
1. Reduce dashboard refresh interval
2. Limit time range in queries
3. Optimize PromQL queries (use recording rules)
4. Increase Grafana memory:
```yaml
grafana:
  deploy:
    resources:
      limits:
        memory: 1G
```

---

## Advanced Topics

### Recording Rules

Pre-compute expensive queries in `prometheus/recording.yml`:
```yaml
groups:
  - name: api_performance
    interval: 30s
    rules:
      - record: job:http_request_rate:5m
        expr: rate(http_requests_total[5m])
```

### Service Discovery

Use Prometheus service discovery instead of static configs:
```yaml
scrape_configs:
  - job_name: 'dynamic-apps'
    docker_sd_configs:
      - host: unix:///var/run/docker.sock
```

### Distributed Tracing

Add OpenTelemetry for request tracing:
1. Install `opentelemetry-api` and `opentelemetry-sdk`
2. Configure Jaeger or Tempo
3. Instrument Flask with tracing decorators

### Custom Exporters

Create custom Prometheus exporters for third-party systems:
- Database exporters (PostgreSQL, MySQL)
- Message queue exporters (RabbitMQ, Kafka)
- Cloud provider exporters (AWS, Azure)

---

## Resources

- [Prometheus Documentation](https://prometheus.io/docs/)
- [Grafana Documentation](https://grafana.com/docs/)
- [Loki Documentation](https://grafana.com/docs/loki/latest/)
- [PromQL Guide](https://prometheus.io/docs/prometheus/latest/querying/basics/)
- [LogQL Guide](https://grafana.com/docs/loki/latest/logql/)
- [Alerting Best Practices](https://prometheus.io/docs/practices/alerting/)

---

**Questions or issues?** Open an issue on GitHub or check the troubleshooting section.
