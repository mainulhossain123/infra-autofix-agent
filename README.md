# Auto-Remediation Platform

# Auto-Remediation Platform

Automated monitoring and safe recovery for containerized services.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)



Automated infrastructure monitoring and remediation. Detects application failures and triggers safe recovery actions.



- Auto-remediation: container restart, cooldown, circuit breaker
- Observability: `/metrics` (Prometheus), WebSocket (2s), DB health



# Auto-Remediation Platform

Automated monitoring and safe recovery for containerized services.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## Overview

Detects crashes, CPU spikes, and error-rate anomalies. Applies safe container restarts with a circuit breaker. Streams metrics via WebSocket and exposes Prometheus.

## Features

- Incident detection: health, error rate, CPU, latency
- Auto-remediation: container restart, cooldown, circuit breaker
- Telemetry: `/metrics` (Prometheus), WebSocket (2s), DB health

## Architecture

- Backend: Flask, Flask-SocketIO, SQLAlchemy
- Bot: Python worker (detectors + remediation)
- Frontend: React (Vite, Tailwind), Socket.IO client
- Database: PostgreSQL
- Monitoring: Prometheus (scrapes app)
- Orchestration: Docker Compose (app, frontend, postgres, bot, prometheus)

## Quick start

```powershell
# Clone and start
- Netflix Chaos Engineering

- Uber's Reliability Engineering

# Result: Bot detects error rate >20%, restarts app**Core Services:**

Endpoints:
- Dashboard: http://localhost:3000
- API: http://localhost:5000
- Prometheus: http://localhost:9090

## Configuration

Use environment variables; don’t commit secrets.
- BOT_POLL_SECONDS (default 5)
- ERROR_RATE_THRESHOLD (default 0.2)
- CPU_THRESHOLD (default 80)
- MAX_RESTARTS_PER_5MIN (default 3)
- COOLDOWN_SECONDS (default 120)
- DATA_RETENTION_DAYS (default 180)

Update at runtime:
```json
PUT /api/config
{
  "key": "error_rate_threshold",
  "value": 0.10
}
```

## API (summary)

- GET /api/health
- GET /api/metrics
- GET /metrics
- GET /api/database/health
- GET /api/database/connections
- GET /api/incidents
- GET /api/incidents/{id}
- GET /api/remediation/history
- POST /api/remediation/manual
- GET /api/config
- GET /api/config/{key}
- PUT /api/config

## Operations

```powershell
# Start

# Logs

# Rebuild app
---
```

## Security

- Keep secrets in environment variables.
- Optional integrations (e.g., Slack) are disabled unless configured.

## Docs

- API: docs/API.md
- Docker & Containers: docs/docker.md
- Operations & Troubleshooting: docs/operations.md

## License

MIT © 2025 Mainul Hossain

⭐ **If this project helped you learn about auto-remediation, consider giving it a star!**



# Trigger multiple crashes (exceeds limit)**Observability Stack:**

for($i=1; $i -le 5; $i++) { - **Grafana**: http://localhost:3001 (Login: admin/admin) 📊 **12-panel dashboard**

    curl -X POST http://localhost:5000/crash- **Prometheus**: http://localhost:9090 🔍 **Metrics & queries**

    Start-Sleep -Seconds 10- **AlertManager**: http://localhost:9093 🚨 **Alert management**


}- **cAdvisor**: http://localhost:8080 📈 **Container stats**




### **6. Install frontend dependencies (first-time setup)**

## 🐳 Docker Commands

```bash

### Basic Operationscd frontend


```bashnpm install  # Installs React, Vite, socket.io-client, etc.







# Stop services### **7. Run demo scenarios**

docker compose down

**PowerShell (Windows):**

# Rebuild and start```powershell

docker compose up --build.\scripts\demo.ps1

```

# View logs

docker compose logs -f**Bash (Linux/macOS):**

```bash

# View logs for specific servicechmod +x scripts/demo.sh

docker compose logs -f ar_bot./scripts/demo.sh

```

# Restart service

docker compose restart ar_app---

```

## 📚 API Documentation

### Debugging

```bash### **Base URL**: `http://localhost:5000`

# Check running containers

docker compose ps### **Complete Endpoint Reference**



# View resource usage#### **Health & Monitoring**

docker stats

**1. Basic Health Check**

# Execute command in container```http

docker exec -it ar_app /bin/bashGET /health

GET /api/health

# Connect to database```

docker exec -it ar_postgres psql -U remediation_user -d remediation_dbReturns detailed health status with metrics, flags, and service info.

```

**Response:**

### Database Queries```json

```sql{

-- Connect to database  "status": "ok",

docker exec -it ar_postgres psql -U remediation_user -d remediation_db  "service": "ar_app",

  "replica": false,

-- View recent incidents  "uptime_seconds": 3600,

SELECT * FROM incidents ORDER BY timestamp DESC LIMIT 10;  "timestamp": "2025-12-03T10:30:00",

  "metrics": {

-- View remediation actions    "total_requests": 1250,

SELECT * FROM remediation_actions ORDER BY timestamp DESC LIMIT 10;    "total_errors": 15,

    "error_rate": 0.012,

-- Count active incidents    "cpu_usage_percent": 45.3,

SELECT COUNT(*) FROM incidents WHERE status = 'ACTIVE';    "memory_usage_mb": 128.5,

```    "active_connections": 5,

    "response_time_p50_ms": 45.2,

---    "response_time_p95_ms": 120.5,

    "response_time_p99_ms": 250.8

## ⚙️ Configuration  },

  "flags": {

### Environment Variables (`.env`)    "cpu_spike": false,

    "error_spike": false

| Variable | Default | Description |  }

|----------|---------|-------------|}

| `SLACK_WEBHOOK_URL` | - | Slack notifications |```

| `BOT_POLL_SECONDS` | 5 | Health check interval |

| `ERROR_RATE_THRESHOLD` | 0.2 | Error rate limit (20%) |**2. Get Metrics**

| `CPU_THRESHOLD` | 80 | CPU usage limit (%) |```http

| `MAX_RESTARTS_PER_5MIN` | 3 | Circuit breaker limit |GET /api/metrics

| `COOLDOWN_SECONDS` | 120 | Action cooldown period |```

| `DATA_RETENTION_DAYS` | 180 | Log retention (6 months) |Returns current application metrics and statistics.



### Dynamic Configuration**3. Prometheus Metrics**

```http

Update thresholds without restarting:GET /metrics

```

```bashExports Prometheus-compatible metrics for scraping.

curl -X PUT http://localhost:5000/api/config \

  -H "Content-Type: application/json" \**4. Database Health**

  -d '{```http

    "key": "error_rate_threshold",GET /api/database/health

    "value": 0.10```

  }'Returns PostgreSQL health metrics including connections, cache hit ratio, and deadlocks.

```

**Response:**

---```json

{

## 📁 Project Structure  "status": "healthy",

  "timestamp": "2025-12-03T10:30:00",

```  "metrics": {

infra-autofix-agent/    "total_connections": 15,

├── app/                    # Flask application    "available_connections": 85,

│   ├── app.py             # Main app + endpoints    "cache_hit_ratio": 98.5,

│   ├── models.py          # Database models    "database_size_mb": 45.2,

│   ├── websocket.py       # Real-time updates    "active_transactions": 2,

│   ├── db_monitor.py      # PostgreSQL health    "commits": 15000,

│   └── metrics.py         # Prometheus metrics    "rollbacks": 12,

├── bot/                   # Auto-remediation bot    "deadlocks": 0

│   ├── bot.py            # Main monitoring loop  },

│   ├── detectors.py      # Incident detection  "issues": []

│   ├── remediation.py    # Recovery actions}

│   ├── circuit_breaker.py # Restart protection```

│   └── cleanup.py        # Database cleanup

├── frontend/             # React dashboard**5. Database Connections**

│   ├── src/pages/       # Dashboard, Incidents, etc.```http

│   └── src/services/    # API client, WebSocketGET /api/database/connections

├── db/                   # Database schemas```

├── prometheus/           # Monitoring configReturns detailed connection pool statistics.

├── docker-compose.yml    # Service orchestration

└── README.md#### **Incidents Management**

```

**1. List Incidents**

---```http

GET /api/incidents?status=ACTIVE&severity=CRITICAL&type=cpu_spike&limit=50&offset=0

## 🗺️ Roadmap```



### ✅ Completed**Query Parameters:**

- [x] Backend API with 20+ endpoints- `status` - Filter by status: ACTIVE, RESOLVED, ESCALATED

- [x] Auto-remediation bot with detectors- `severity` - Filter by severity: CRITICAL, WARNING, INFO

- [x] Circuit breaker implementation- `type` - Filter by incident type: health_check, high_error_rate, cpu_spike, high_latency

- [x] React dashboard with real-time updates- `limit` - Number of results (default: 50, max: 500)

- [x] WebSocket metric streaming- `offset` - Pagination offset (default: 0)

- [x] PostgreSQL health monitoring

- [x] Prometheus metrics integration**Response:**

- [x] Database cleanup (6-month retention)```json

- [x] Docker Compose orchestration{

  "incidents": [

### 🚧 Future Enhancements    {

- [ ] Unit & integration tests      "id": 123,

- [ ] Kubernetes deployment (Helm charts)      "type": "cpu_spike",

- [ ] Machine learning anomaly detection      "severity": "CRITICAL",

- [ ] Multi-service monitoring      "status": "ACTIVE",

- [ ] PagerDuty integration      "description": "CPU usage exceeded 80% threshold",

- [ ] Advanced alerting rules      "timestamp": "2025-12-03T10:25:00",

      "metadata": {

---        "cpu_percent": 95.3,

        "threshold": 80

## 📄 License      }

    }

MIT License - Copyright (c) 2025 Mainul Hossain  ],

  "total": 1,

---  "limit": 50,

  "offset": 0

## 🙏 Acknowledgments}

```

Inspired by production SRE practices at Google, Netflix, and Uber.

**2. Get Incident Details**

---```http

GET /api/incidents/{id}

⭐ **If this helped you learn about auto-remediation, give it a star!**```

Returns detailed information about a specific incident including remediation actions.

**3. Get Incident Statistics**
```http
GET /api/incidents/stats
```
Returns aggregated statistics about incidents by type, severity, and status.

#### **Remediation Actions**

**1. Get Remediation History**
```http
GET /api/remediation/history?limit=50&offset=0
```
Returns history of all remediation actions with success/failure status.

**2. Manual Remediation**
```http
POST /api/remediation/manual
Content-Type: application/json

{
  "action_type": "restart_container",
  "target": "ar_app",
  "reason": "Manual intervention due to high memory usage"
}
```

**Valid action_type values:**
- `restart_container` - Restart the target container
- `scale_up` - Start a replica container
- `scale_down` - Stop replica containers
- `heal` - Run health check and auto-recover

**Response:**
```json
{
  "success": true,
  "action_id": 456,
  "message": "Container ar_app restarted successfully",
  "execution_time_ms": 1250
}
```

**3. Get Remediation Statistics**
```http
GET /api/remediation/stats
```
Returns success rates, execution times, and action counts.

#### **Configuration Management**

**1. Get Configuration**
```http
GET /api/config
GET /api/config/{key}
```
Retrieve all configuration or specific key.

**2. Update Configuration**
```http
PUT /api/config
Content-Type: application/json

{
  "key": "thresholds",
  "value": {
    "error_rate": 0.15,
    "cpu_percent": 85,
    "response_time_ms": 500
  }
}
```

**3. List All Config Keys**
```http
GET /api/config/keys
```

#### **Simulation & Testing Endpoints**

**1. Trigger Application Crash**
```http
POST /crash
POST /api/trigger/crash
```
Immediately crashes the application (exits process). Bot will detect and restart.

**2. Trigger CPU Spike**
```http
POST /spike/cpu?duration=15
POST /api/trigger/cpu-spike?duration=30
```
Simulates high CPU load for specified duration (seconds).

**Query Parameters:**
- `duration` - Duration in seconds (default: 10, max: 300)

**3. Trigger Error Spike**
```http
POST /spike/errors?duration=20
POST /api/trigger/error-spike?duration=30
```
Causes 50% of requests to return 500 errors for specified duration.

**4. Trigger High Latency**
```http
POST /api/trigger/latency-spike?duration=20
```
Simulates slow response times for specified duration.

**5. Stop All Simulations**
```http
POST /api/trigger/stop-all
```
Stops all active simulations immediately.

#### **System Information**

**1. Get Service Info**
```http
GET /api/info
```
Returns application version, environment, and service details.

**2. Check Readiness**
```http
GET /ready
```
Returns 200 if service is ready to accept traffic, 503 otherwise.

---

## 🎬 Demo Scenarios

### **Scenario 1: Application Crash & Auto-Recovery**

**Objective**: Test bot's ability to detect and restart crashed applications

```powershell
# PowerShell (Windows)
# 1. Trigger application crash
Invoke-RestMethod -Uri http://localhost:5000/crash -Method Post

# 2. Watch bot detect and restart
docker compose logs -f ar_bot

# Expected Output:
# [INFO] Health check failed for ar_app
# [INFO] Creating incident: health_check_failure
# [INFO] Executing remediation: restart_container
# [INFO] Container ar_app restarted successfully
```

```bash
# Bash (Linux/macOS)
# 1. Trigger crash
curl -X POST http://localhost:5000/crash

# 2. Monitor bot
docker compose logs -f ar_bot
```

**Verification:**
- ✅ App becomes unreachable after crash
- ✅ Bot detects health check failure within 5 seconds
- ✅ Incident created in database (type: health_check)
- ✅ Container automatically restarts
- ✅ App returns to healthy state
- ✅ Slack notification sent (if configured)

---

### **Scenario 2: CPU Spike & Auto-Scaling**

**Objective**: Test bot's response to high CPU usage

```powershell
# PowerShell
# 1. Trigger CPU spike (30 seconds)
Invoke-RestMethod -Uri "http://localhost:5000/api/trigger/cpu-spike?duration=30" -Method Post

# 2. Monitor CPU in real-time
docker stats ar_app

# 3. Watch bot detect high CPU
docker compose logs -f ar_bot

# Expected Output:
# [WARNING] CPU usage 95% exceeds threshold 80%
# [INFO] Creating incident: cpu_spike
# [INFO] Executing remediation: restart_container
```

```bash
# Bash
curl -X POST "http://localhost:5000/api/trigger/cpu-spike?duration=30"
docker stats ar_app
```

**Verification:**
- ✅ CPU usage spikes to >80% (visible in `docker stats`)
- ✅ Bot detects within 10 seconds
- ✅ Incident severity: CRITICAL
- ✅ Remediation action: Container restart
- ✅ CPU returns to normal after remediation

---

### **Scenario 3: High Error Rate & Circuit Breaker**

**Objective**: Test error detection and circuit breaker preventing restart loops

```powershell
# PowerShell
# 1. Trigger error spike (30 seconds, 50% error rate)
Invoke-RestMethod -Uri "http://localhost:5000/api/trigger/error-spike?duration=30" -Method Post

# 2. Generate traffic to trigger errors
1..100 | ForEach-Object { 
    try { Invoke-RestMethod http://localhost:5000/ } 
    catch { Write-Host "Error: $_" }
}

# 3. Monitor bot response
docker compose logs -f ar_bot

# Expected Output:
# [ERROR] Error rate 52% exceeds threshold 20%
# [INFO] Creating incident: high_error_rate
# [INFO] Executing remediation: restart_container
```

```bash
# Bash
curl -X POST "http://localhost:5000/api/trigger/error-spike?duration=30"

# Generate traffic
for i in {1..100}; do 
    curl http://localhost:5000/ || true
done
```

**Verification:**
- ✅ Error rate increases to >20%
- ✅ Incident created (type: high_error_rate)
- ✅ Container restarts automatically
- ✅ Error rate returns to normal after simulation ends

---

### **Scenario 4: Circuit Breaker Protection**

**Objective**: Verify circuit breaker prevents infinite restart loops

```powershell
# PowerShell
# 1. Trigger multiple rapid crashes (exceeds threshold)
1..5 | ForEach-Object { 
    Write-Host "Crash attempt $_"
    Invoke-RestMethod -Uri http://localhost:5000/crash -Method Post
    Start-Sleep -Seconds 10
}

# 2. Watch circuit breaker activate
docker compose logs -f ar_bot

# Expected Output:
# [INFO] Restart 1/3 for ar_app
# [INFO] Restart 2/3 for ar_app
# [INFO] Restart 3/3 for ar_app
# [CRITICAL] Circuit breaker OPEN for ar_app - Maximum restarts exceeded
# [CRITICAL] Escalating incident - manual intervention required
```

**Verification:**
- ✅ First 3 crashes → Container restarts
- ✅ 4th crash → Circuit breaker opens
- ✅ No more automatic restarts
- ✅ Incident escalated to CRITICAL
- ✅ Alert sent to Slack/console

**Reset Circuit Breaker:**
```powershell
# Wait 120 seconds (cooldown period) or restart bot
docker compose restart ar_bot
```

---

### **Scenario 5: Manual Remediation**

**Objective**: Test manual remediation triggers via API

```powershell
# PowerShell
# 1. Manually restart application
$body = @{
    action_type = "restart_container"
    target = "ar_app"
    reason = "Manual intervention - investigating memory leak"
} | ConvertTo-Json

Invoke-RestMethod -Uri http://localhost:5000/api/remediation/manual `
    -Method Post `
    -ContentType "application/json" `
    -Body $body

# Expected Response:
# {
#   "success": true,
#   "action_id": 42,
#   "message": "Container ar_app restarted successfully",
#   "execution_time_ms": 1250
# }
```

```bash
# Bash
curl -X POST http://localhost:5000/api/remediation/manual \
  -H "Content-Type: application/json" \
  -d '{
    "action_type": "restart_container",
    "target": "ar_app",
    "reason": "Manual intervention"
  }'
```

**Other Manual Actions:**
```powershell
# Scale up (start replica)
$body = @{ action_type = "scale_up"; target = "ar_app"; reason = "Load testing" } | ConvertTo-Json
Invoke-RestMethod -Uri http://localhost:5000/api/remediation/manual -Method Post -ContentType "application/json" -Body $body

# Scale down (stop replica)
$body = @{ action_type = "scale_down"; target = "ar_app"; reason = "Reduce costs" } | ConvertTo-Json
Invoke-RestMethod -Uri http://localhost:5000/api/remediation/manual -Method Post -ContentType "application/json" -Body $body

# Health check
$body = @{ action_type = "heal"; target = "ar_app"; reason = "Verify recovery" } | ConvertTo-Json
Invoke-RestMethod -Uri http://localhost:5000/api/remediation/manual -Method Post -ContentType "application/json" -Body $body
```

---

### **Scenario 6: Configuration Update (Zero Downtime)**

**Objective**: Dynamically update thresholds without restarting services

```powershell
# PowerShell
# 1. Get current configuration
Invoke-RestMethod -Uri http://localhost:5000/api/config | ConvertTo-Json

# 2. Update error rate threshold from 20% to 10%
$body = @{
    key = "error_rate_threshold"
    value = 0.10
} | ConvertTo-Json

Invoke-RestMethod -Uri http://localhost:5000/api/config `
    -Method Put `
    -ContentType "application/json" `
    -Body $body

# 3. Verify new threshold is active
Invoke-RestMethod -Uri http://localhost:5000/api/config/error_rate_threshold
```

```bash
# Bash
# Get current config
curl http://localhost:5000/api/config | jq

# Update threshold
curl -X PUT http://localhost:5000/api/config \
  -H "Content-Type: application/json" \
  -d '{
    "key": "error_rate_threshold",
    "value": 0.10
  }'
```

**Update Multiple Thresholds:**
```powershell
$body = @{
    key = "thresholds"
    value = @{
        error_rate = 0.10
        cpu_percent = 90
        response_time_ms = 300
    }
} | ConvertTo-Json

Invoke-RestMethod -Uri http://localhost:5000/api/config -Method Put -ContentType "application/json" -Body $body
```

---

### **Scenario 7: Database Health Monitoring**

**Objective**: Monitor PostgreSQL health and performance

```powershell
# PowerShell
# 1. Check database health
Invoke-RestMethod -Uri http://localhost:5000/api/database/health | ConvertTo-Json

# Expected Response:
# {
#   "status": "healthy",
#   "metrics": {
#     "total_connections": 15,
#     "available_connections": 85,
#     "cache_hit_ratio": 98.5,
#     "database_size_mb": 45.2,
#     "deadlocks": 0
#   },
#   "issues": []
# }

# 2. Get connection pool stats
Invoke-RestMethod -Uri http://localhost:5000/api/database/connections | ConvertTo-Json
```

```bash
# Bash
curl http://localhost:5000/api/database/health | jq
curl http://localhost:5000/api/database/connections | jq
```

**Simulating Database Issues:**
```bash
# Create many connections to trigger warning
for i in {1..85}; do
    docker exec -d ar_postgres psql -U remediation_user -d remediation_db -c "SELECT pg_sleep(60);"
done

# Check health again (should show warning)
curl http://localhost:5000/api/database/health
```

---

### **Scenario 8: Full Demo Script**

**PowerShell (Windows):**
```powershell
.\scripts\demo.ps1
```

The script will:
1. ✅ Verify all services are running
2. ✅ Run health check tests
3. ✅ Test CPU spike detection
4. ✅ Test error spike detection
5. ✅ Test application crash recovery
6. ✅ Display incident history
7. ✅ Display remediation statistics

**Bash (Linux/macOS):**
```bash
chmod +x scripts/demo.sh
./scripts/demo.sh
```

---

### **Scenario 9: Real-Time Dashboard Monitoring**

**Objective**: Monitor system in real-time via React dashboard

```
1. Open dashboard: http://localhost:3000

2. Navigate to pages:
   - Dashboard → View real-time CPU, memory, error rate charts
   - Incidents → See active/resolved incidents with filtering
   - Remediation → View action history and success rates
   - Manual Control → Trigger manual actions via UI
   - Configuration → Update thresholds dynamically

3. Trigger CPU spike:
   POST http://localhost:5000/api/trigger/cpu-spike?duration=60

4. Watch dashboard update in real-time:
   - CPU chart shows spike
   - New incident appears in Incidents page
   - Remediation action logged
   - Metrics auto-refresh every 5 seconds
```

**WebSocket Real-Time Updates:**
```javascript
// Dashboard connects via WebSocket at http://localhost:5000
// Receives metric updates every 2 seconds
// Auto-subscribes to: metrics, incidents, health updates
// Shows connection status: "WebSocket: Connected" or "Polling Mode"
```

---

### **Scenario 10: Observability Stack Integration**

**Objective**: Use Prometheus + Grafana for advanced monitoring

```bash
# 1. Start all services including observability stack
docker compose up -d

# 2. Access Grafana
# Open: http://localhost:3001
# Login: admin / admin

# 3. Navigate to Auto-Remediation Platform dashboard
# - View 12 panels with real-time metrics
# - CPU/Memory trends (app + container)
# - HTTP request/error rates
# - Database connection pool
# - Incident rates
# - Remediation success rates

# 4. Access Prometheus
# Open: http://localhost:9090
# Try queries:
# - rate(flask_http_request_total[1m])
# - process_cpu_seconds_total
# - pg_stat_database_numbackends

# 5. Trigger alert
curl -X POST http://localhost:5000/api/trigger/cpu-spike?duration=600

# 6. Wait 5 minutes, then check AlertManager
# Open: http://localhost:9093/#/alerts
# Should see: HighCPUUsage alert firing

# 7. Alert creates incident in Flask app
curl http://localhost:5000/api/incidents | jq
```

---

## ⚙️ Configuration

### **Environment Variables** (`.env`)

| Variable | Default | Description |
|----------|---------|-------------|
| `SLACK_WEBHOOK_URL` | - | Slack webhook for notifications |
| `BOT_POLL_SECONDS` | 5 | Health check poll interval |
| `ERROR_RATE_THRESHOLD` | 0.2 | Error rate threshold (20%) |
| `CPU_THRESHOLD` | 80 | CPU usage threshold (%) |
| `MAX_RESTARTS_PER_5MIN` | 3 | Circuit breaker threshold |
| `COOLDOWN_SECONDS` | 120 | Cooldown between actions |
| `DATA_RETENTION_DAYS` | 180 | Delete logs older than N days (6 months default) |
| `CLEANUP_INTERVAL_HOURS` | 24 | How often to run cleanup (daily default) |

### **Dynamic Configuration** (Database)

Update thresholds without restarting:

```bash
curl -X PUT http://localhost:5000/api/config \
  -H "Content-Type: application/json" \
  -d '{
    "key": "thresholds",
    "value": {
      "error_rate": 0.15,
      "cpu_percent": 85
    }
  }'
```

### **Automatic Data Cleanup**

The bot automatically cleans up old incidents and remediation logs to prevent database bloat:

- **Default Retention**: 180 days (6 months)
- **Cleanup Schedule**: Every 24 hours (configurable)
- **What Gets Deleted**: Only incidents and remediation actions **older than** the retention period
- **What's Preserved**: All recent logs from the last 6 months (or configured retention)

**How it works:**
1. Bot runs cleanup check on every monitoring iteration
2. If 24 hours have passed since last cleanup, it triggers automatically
3. Deletes records where `timestamp < (today - retention_days)`
4. Logs statistics and sends notification about deleted records

**Manual cleanup:**
```bash
# Run cleanup manually from bot container
docker exec ar_bot python -c "from cleanup import run_cleanup; run_cleanup(retention_days=180)"
```

**Configure retention:**
```yaml
# docker-compose.yml or .env
DATA_RETENTION_DAYS=90     # Keep only 3 months
CLEANUP_INTERVAL_HOURS=12  # Run cleanup twice daily
```

---

## 💻 Development

### **Project Structure**

```
infra-autofix-agent/
├── app/                    # Flask application
│   ├── app.py             # Main Flask app with endpoints
│   ├── models.py          # SQLAlchemy database models
│   ├── config.py          # Configuration management
│   ├── metrics.py         # Prometheus metrics
│   ├── simulate.py        # Failure simulator
│   ├── websocket.py       # WebSocket server (real-time updates)
│   ├── db_monitor.py      # PostgreSQL health monitoring
│   ├── requirements.txt   # Python dependencies
│   └── Dockerfile         # Container image
├── bot/                   # Auto-remediation bot
│   ├── bot.py            # Main monitoring loop
│   ├── detectors.py      # Incident detectors
│   ├── remediation.py    # Remediation actions
│   ├── circuit_breaker.py # Prevents restart loops
│   ├── notifications.py  # Slack/console alerts
│   ├── cleanup.py        # Database cleanup (6-month retention)
│   └── requirements.txt  # Python dependencies
├── frontend/             # React dashboard
│   ├── src/
│   │   ├── pages/       # Dashboard, Incidents, Remediation, Manual, Config
│   │   ├── services/    # API client, WebSocket client
│   │   ├── components/  # Reusable UI components
│   │   └── utils/       # Formatters, helpers
│   ├── package.json     # Node dependencies
│   └── Dockerfile       # Nginx container
├── db/                   # Database
│   ├── init.sql         # Schema (incidents, remediation_actions, etc.)
│   └── seed_data.sql    # Sample configuration data
├── prometheus/           # Prometheus monitoring
│   ├── prometheus.yml   # Scrape configuration
│   └── alert_rules.yml  # Alert definitions
├── grafana/             # Grafana dashboards
│   ├── provisioning/    # Auto-provisioning configs
│   └── dashboards/      # Dashboard JSON files
├── alertmanager/        # AlertManager
│   └── alertmanager.yml # Alert routing config
├── scripts/             # Helper scripts
│   ├── demo.ps1        # Demo scenarios (Windows PowerShell)
│   ├── demo.sh         # Demo scenarios (Linux/macOS)
│   └── health_check.ps1 # Health verification
├── docker-compose.yml   # Service orchestration
├── Makefile            # Build automation
├── .env.example        # Environment template
└── README.md           # This file
```

### **Docker Commands Reference**

#### **Building & Starting Services**

```bash
# Build all images from scratch
docker compose build

# Build with no cache (fresh build)
docker compose build --no-cache

# Build and start all services
docker compose up --build

# Start services in detached mode (background)
docker compose up -d

# Start specific service
docker compose up app
docker compose up bot

# Scale a service (create multiple instances)
docker compose up --scale app=2
```

#### **Stopping & Removing Services**

```bash
# Stop all services (keeps containers)
docker compose stop

# Stop specific service
docker compose stop ar_app

# Stop and remove all containers
docker compose down

# Stop and remove containers + volumes (⚠️ deletes database data)
docker compose down -v

# Remove all containers, networks, images, and volumes
docker compose down --rmi all -v
```

#### **Viewing Logs**

```bash
# View logs from all services
docker compose logs

# Follow logs in real-time
docker compose logs -f

# View logs from specific service
docker compose logs ar_bot
docker compose logs -f ar_app

# View last 50 lines
docker compose logs --tail=50 ar_app

# View logs with timestamps
docker compose logs -f -t ar_bot
```

#### **Service Management**

```bash
# Restart a service
docker compose restart ar_app

# Restart all services
docker compose restart

# View running containers
docker compose ps

# View all containers (including stopped)
docker compose ps -a

# Check service health status
docker compose ps
docker inspect ar_app | grep -A 10 Health
```

#### **Executing Commands in Containers**

```bash
# Open interactive shell in app container
docker exec -it ar_app /bin/bash

# Open shell in bot container
docker exec -it ar_bot /bin/bash

# Run Python command in app container
docker exec ar_app python -c "print('Hello from container')"

# Connect to PostgreSQL database
docker exec -it ar_postgres psql -U remediation_user -d remediation_db

# Run database query
docker exec ar_postgres psql -U remediation_user -d remediation_db \
  -c "SELECT * FROM incidents ORDER BY timestamp DESC LIMIT 5;"

# Check Flask app process
docker exec ar_app ps aux | grep python

# View app environment variables
docker exec ar_app env
```

#### **Database Operations**

```bash
# Connect to database interactively
docker exec -it ar_postgres psql -U remediation_user -d remediation_db

# Backup database
docker exec ar_postgres pg_dump -U remediation_user remediation_db > backup.sql

# Restore database
cat backup.sql | docker exec -i ar_postgres psql -U remediation_user -d remediation_db

# View database size
docker exec ar_postgres psql -U remediation_user -d remediation_db \
  -c "SELECT pg_size_pretty(pg_database_size('remediation_db'));"

# Count incidents
docker exec ar_postgres psql -U remediation_user -d remediation_db \
  -c "SELECT COUNT(*) FROM incidents;"

# View active connections
docker exec ar_postgres psql -U remediation_user -d remediation_db \
  -c "SELECT count(*) FROM pg_stat_activity;"

# Manually trigger cleanup (delete logs older than 180 days)
docker exec ar_bot python -c "from cleanup import run_cleanup; run_cleanup(retention_days=180)"
```

#### **Monitoring & Debugging**

```bash
# View resource usage (CPU, memory, network)
docker stats

# View stats for specific container
docker stats ar_app

# Inspect container details
docker inspect ar_app

# View container IP address
docker inspect ar_app | grep IPAddress

# View container environment variables
docker inspect ar_app | grep -A 20 Env

# View mounted volumes
docker inspect ar_app | grep -A 10 Mounts

# Check container health
docker inspect ar_app --format='{{json .State.Health}}'

# View network details
docker network inspect infra-autofix-agent_remediation_network
```

#### **Image Management**

```bash
# List all images
docker images

# Remove specific image
docker rmi infra-autofix-agent-app

# Remove all unused images
docker image prune

# Remove all dangling images
docker image prune -a

# View image layers and size
docker history infra-autofix-agent-app
```

#### **Volume Management**

```bash
# List volumes
docker volume ls

# Inspect volume
docker volume inspect infra-autofix-agent_postgres_data

# Remove specific volume (⚠️ deletes data)
docker volume rm infra-autofix-agent_postgres_data

# Remove all unused volumes
docker volume prune
```

#### **Troubleshooting Commands**

```bash
# Check if port is in use
netstat -ano | findstr :5000    # Windows
lsof -i :5000                   # Linux/macOS

# View Docker daemon logs
# Windows: Check Docker Desktop → Troubleshoot → View logs
# Linux: journalctl -u docker

# Test network connectivity between containers
docker exec ar_bot ping ar_app
docker exec ar_app ping ar_postgres

# Check DNS resolution
docker exec ar_app nslookup ar_postgres

# Test database connection from app
docker exec ar_app python -c "
from config import Config
from models import init_db
engine = init_db(Config.DATABASE_URL)
print('Database connected successfully!')
"

# View failed container logs
docker compose logs ar_app | grep ERROR
docker compose logs ar_bot | grep CRITICAL

# Rebuild single service
docker compose up --build --force-recreate ar_app

# Check Docker disk usage
docker system df
```

#### **Development Workflow**

```bash
# 1. Make code changes in app/ or bot/
# (edit files locally)

# 2. Rebuild and restart affected service
docker compose up --build app

# 3. View logs to verify changes
docker compose logs -f app

# 4. Test API endpoint
curl http://localhost:5000/api/health

# 5. If needed, restart dependent services
docker compose restart bot

# 6. Clean rebuild everything
docker compose down
docker compose build --no-cache
docker compose up -d
```

#### **Testing Specific Scenarios**

```bash
# Test CPU spike detection
curl -X POST http://localhost:5000/api/trigger/cpu-spike?duration=30
docker compose logs -f ar_bot  # Watch bot detect and remediate

# Test error spike detection  
curl -X POST http://localhost:5000/api/trigger/error-spike?duration=30
# Send test requests
for i in {1..50}; do curl http://localhost:5000/; done

# Test application crash
curl -X POST http://localhost:5000/crash
docker compose logs -f ar_bot  # Watch bot restart container

# Test manual remediation
curl -X POST http://localhost:5000/api/remediation/manual \
  -H "Content-Type: application/json" \
  -d '{"action_type":"restart_container","target":"ar_app","reason":"Testing"}'

# Check database health
curl http://localhost:5000/api/database/health

# View Prometheus metrics
curl http://localhost:5000/metrics
```

#### **Observability Stack Commands**

```bash
# Start with observability services
docker compose up --build app bot frontend postgres prometheus grafana alertmanager cadvisor postgres-exporter

# Access Prometheus UI
# Open: http://localhost:9090
# Query: rate(flask_http_request_total[1m])

# Access Grafana dashboards
# Open: http://localhost:3001
# Login: admin / admin
# Navigate to: Dashboards → Auto-Remediation Platform

# Access AlertManager
# Open: http://localhost:9093

# Access cAdvisor (container metrics)
# Open: http://localhost:8080

# Test alert flow
curl -X POST http://localhost:5000/api/trigger/cpu-spike?duration=600
# Wait 5 minutes for HighCPUUsage alert
# Check: http://localhost:9093/#/alerts

# View Grafana logs
docker compose logs -f grafana

# Reload Prometheus config without restart
docker exec ar_prometheus kill -HUP 1

# Check Prometheus targets
curl http://localhost:9090/api/v1/targets
```

### **Makefile Commands** (Linux/macOS)

```bash
make build          # Build Docker images
make up             # Start all services
make down           # Stop all services
make logs           # View all logs
make logs-app       # View app logs only
make logs-bot       # View bot logs only
make restart        # Restart all services
make clean          # Clean up containers and volumes
make demo           # Run demo scenarios
make test           # Run tests (coming soon)
make shell-app      # Open shell in app container
make shell-bot      # Open shell in bot container
make db-connect     # Connect to PostgreSQL
```

### **Frontend Development**

```bash
# Install dependencies
cd frontend
npm install

# Run development server (without Docker)
npm run dev
# Open: http://localhost:5173

# Build for production
npm run build

# Preview production build
npm run preview

# Lint code
npm run lint

# Rebuild frontend container
docker compose up --build frontend
```

---

## 🗺️ Roadmap

### **Weekend 1** ✅ (Complete - Backend Infrastructure)
- [x] Project structure and Docker setup
- [x] PostgreSQL database with comprehensive schema
- [x] Flask REST API with 20+ endpoints
- [x] Monitoring bot with intelligent detectors
- [x] Circuit breaker implementation with cooldowns
- [x] Docker Compose orchestration (4 services)
- [x] Demo scripts (PowerShell + Bash)
- [x] Database cleanup with 6-month retention

### **Weekend 2** ✅ (Complete - React Frontend)
- [x] React 18 + Vite + Tailwind CSS setup
- [x] Dashboard with real-time metrics and charts (Recharts)
- [x] Incidents page with filtering, sorting, and detail modal
- [x] Remediation history with statistics and success rates
- [x] Manual control page with action triggers
- [x] Configuration UI with dynamic threshold management
- [x] Docker integration with Nginx reverse proxy
- [x] Auto-refresh (5s polling) and responsive design
- [x] Badge alignment fixes and timestamp formatting

### **Weekend 3** ✅ (Complete - Observability & Real-Time)
- [x] **WebSocket Integration** - Real-time metric streaming (2s push vs 5s polling)
  - Flask-SocketIO backend with auto-reconnect
  - Socket.IO client on frontend
  - Live metric/incident broadcasts
  - Connection status indicator
- [x] **PostgreSQL Monitoring** - Database health tracking
  - Connection pool monitoring
  - Cache hit ratio (target: >95%)
  - Transaction statistics
  - Deadlock detection
  - Health endpoints with thresholds
- [x] **Prometheus + Grafana Stack** - Enterprise observability
  - Prometheus metrics scraping (5-10s intervals)
  - 12-panel Grafana dashboard (auto-provisioned)
  - Alert rules (CPU, errors, connections, incidents)
  - AlertManager integration with webhook routing
- [x] **Container Metrics** - Infrastructure monitoring
  - cAdvisor for Docker container stats
  - postgres-exporter for database metrics
  - Multi-target Prometheus scraping
- [x] **Enhanced Docker Compose** - 8 total services
  - app, bot, frontend, postgres ✅
  - prometheus, grafana, alertmanager, cadvisor, postgres-exporter ✅

### **Future Enhancements** 🚧

#### **Testing & Quality (Weekend 4)**
- [ ] Unit tests for detectors, remediation, circuit breaker
- [ ] Integration tests for API endpoints
- [ ] E2E tests for frontend workflows
- [ ] Test coverage reporting (pytest-cov)
- [ ] CI/CD pipeline (GitHub Actions)

#### **Advanced Features**
- [ ] **Kubernetes Deployment**
  - Helm charts for multi-cluster deployment
  - Horizontal Pod Autoscaling (HPA)
  - Ingress controller setup
  - ConfigMaps and Secrets management

- [ ] **Machine Learning**
  - Anomaly detection using Isolation Forest
  - Predictive failure analysis with LSTM
  - Auto-tuning of thresholds based on historical data
  - Intelligent alert correlation

- [ ] **LLM Integration**
  - Automated postmortem generation using GPT-4
  - Natural language incident summaries
  - Remediation playbook recommendations
  - Root cause analysis suggestions

- [ ] **Multi-Service Monitoring**
  - Support multiple application targets
  - Service dependency mapping
  - Cross-service incident correlation
  - Distributed tracing (Jaeger/Zipkin)

- [ ] **SLO & Error Budget Tracking**
  - Define SLOs (99.9% uptime, <200ms p95 latency)
  - Error budget calculation and visualization
  - Burn rate alerts
  - SLO compliance reporting

- [ ] **Enhanced Alerting**
  - PagerDuty integration
  - Microsoft Teams webhooks
  - Email notifications
  - Alert routing based on severity/time
  - On-call rotation support

- [ ] **Security Enhancements**
  - OAuth 2.0 / JWT authentication
  - Role-based access control (RBAC)
  - Secrets management (HashiCorp Vault)
  - Audit logging for all actions
  - TLS/SSL encryption

- [ ] **Extended Observability**
  - ELK Stack integration (Elasticsearch, Logstash, Kibana)
  - Distributed tracing with Jaeger
  - APM (Application Performance Monitoring)
  - Custom dashboards per service

- [ ] **Advanced Remediation**
  - Auto-rollback on failed deployments
  - Canary deployments
  - Blue-green deployment automation
  - Self-healing infrastructure patterns

---

## 🤝 Contributing

Contributions welcome! Please:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgments

- Inspired by production SRE practices at Google, Netflix, and Uber
- Circuit breaker pattern from [Martin Fowler](https://martinfowler.com/bliki/CircuitBreaker.html)
- Built as a portfolio project demonstrating SRE → Full-Stack transition

---

## 📧 Contact

**Mainul Hossain** - [GitHub](https://github.com/mainulhossain123)

**Project**: [infra-autofix-agent](https://github.com/mainulhossain123/infra-autofix-agent)

---

⭐ **If this project helped you learn about auto-remediation and SRE practices, consider giving it a star!**
