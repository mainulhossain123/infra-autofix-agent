# Infrastructure Auto-Remediation Platform

[![CI Pipeline](https://github.com/mainulhossain123/infra-autofix-agent/actions/workflows/ci.yml/badge.svg)](https://github.com/mainulhossain123/infra-autofix-agent/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

An open-source AI-powered platform for automated infrastructure monitoring, incident detection, and self-healing with integrated ML/AI capabilities.

> **AI Chat uses the [Groq API](https://console.groq.com) (free tier) — an internet connection and a free Groq API key are required for the AI Chat Assistant.** All other ML features (anomaly detection, forecasting, failure prediction) run entirely locally with no external dependencies.

---

## Features

### 🤖 AI-Powered Intelligence
- **AI Chat Assistant**: Interactive LLM-powered assistant (Groq — Llama 3.3 70B) for incident analysis and troubleshooting
- **Root Cause Analysis**: Automated LLM-based analysis with actionable recommendations
- **Natural Language Interface**: Ask questions about incidents, metrics, and system health in plain English

### 🔮 ML & Predictive Analytics (fully local, no API key needed)
- **Anomaly Detection**: Real-time detection using Isolation Forest (92-95% accuracy)
- **Failure Prediction**: Forecast infrastructure failures 1-72 hours ahead with LightGBM
- **Time-Series Forecasting**: Prophet-based predictions to prevent metric threshold breaches
- **Continuous Learning**: Auto-retraining models with performance tracking

### 🛡️ Auto-Remediation
- **Self-Healing Infrastructure**: Automatic remediation with circuit breaker protection
- **Manual Controls**: Override automation with one-click manual actions
- **Smart Detection**: Real-time monitoring of CPU, memory, error rates, and latency

### 📊 Observability & Dashboard
- **Real-Time Dashboard**: React UI with live WebSocket updates and incident timeline
- **Live Notification Bell**: Active incident count badge with dropdown showing severity and links
- **System Logs Page**: Health banner, CPU/memory/error rate/uptime cards, incident severity summary
- **Full Observability Stack**: Integrated Prometheus, Grafana, and Loki
- **Custom Metrics**: Comprehensive system and application metrics collection

### 🚀 Production Ready
- **Docker Compose**: Quick local development and production deployment
- **AWS EC2 Deployment**: Terraform-managed infrastructure on AWS free tier (t2.micro)
- **CI/CD Pipeline**: GitHub Actions for automated testing and one-click deployment to EC2

---

## Groq API Key Requirement

The AI Chat Assistant calls the [Groq API](https://console.groq.com) to run `llama-3.3-70b-versatile`. This is a **free external API** — Groq offers a generous free tier with no credit card required.

**Without a Groq key:**
- All dashboard features work normally
- All local ML features (anomaly detection, forecasting, failure prediction) work normally
- AI Chat will return an error: `"AI service not configured. Set the GROQ_API_KEY environment variable."`

**Getting a free Groq API key (takes ~1 minute):**
1. Go to [console.groq.com](https://console.groq.com)
2. Sign in with your GitHub account
3. Click **API Keys** → **Create API Key**
4. Copy the key and add it to your `.env` file as `GROQ_API_KEY=your_key_here`

---

## Quick Start (Local)

### Prerequisites

- **Docker Desktop 20.10+** with Docker Compose 2.0+
- **4GB RAM minimum** (no local LLM is run — Groq handles AI chat externally)
- **3GB disk space**
- **A free Groq API key** for the AI Chat feature (see above — optional, all other features work without it)

### 1. Clone the repository

```bash
git clone https://github.com/mainulhossain123/infra-autofix-agent.git
cd infra-autofix-agent
```

### 2. Configure environment variables

```bash
cp .env.example .env
```

Open `.env` and set your values. The minimum required change for AI chat is:

```bash
# Required for AI Chat Assistant
GROQ_API_KEY=your_groq_api_key_here

# Optional: change Grafana password (default is "admin")
GRAFANA_ADMIN_PASSWORD=your_grafana_password
```

### 3. Start all services

```bash
docker compose up -d
```

### 4. Verify everything is running

```bash
docker compose ps
```

All containers should show as `Up` or `healthy`:

| Container | Expected Status |
|-----------|----------------|
| `ar_postgres` | healthy |
| `ar_app` | healthy |
| `ar_bot` | Up |
| `ar_frontend` | healthy |
| `ar_prometheus` | Up |
| `ar_grafana` | Up |
| `ar_loki` | Up |
| `ar_promtail` | Up |

### 5. Access the application

| Service | URL | Credentials |
|---------|-----|-------------|
| **Dashboard** | http://localhost:3000 | — |
| **AI Chat** | http://localhost:3000/chat | Requires `GROQ_API_KEY` in `.env` |
| **System Logs** | http://localhost:3000/system-logs | — |
| **Incidents** | http://localhost:3000/incidents | — |
| **API** | http://localhost:5000 | — |
| **API Docs** | http://localhost:5000/api/docs | — |
| **Grafana** | http://localhost:3001 | `admin` / value of `GRAFANA_ADMIN_PASSWORD` |
| **Prometheus** | http://localhost:9090 | — |

---

## AWS Cloud Deployment

The project includes full Terraform infrastructure and GitHub Actions workflows for deploying to AWS EC2 (free tier eligible).

### Infrastructure

- **EC2**: `t2.micro` in `ap-southeast-1` (Singapore) — AWS free tier
- **Public IP**: Assigned dynamically — no Elastic IP (avoids ~$3.60/month charge under AWS's Feb 2024 IPv4 pricing policy)
- **Stable URL**: [DuckDNS](https://www.duckdns.org) free subdomain (e.g. `infra-autofix.duckdns.org`) — auto-updated by a cron job on EC2 whenever the IP changes after a stop/start
- **Security Group**: Ports 22 (SSH), 3000 (dashboard), 5000 (API), 3001 (Grafana), 9090 (Prometheus)
- **State Backend**: S3 bucket for Terraform state

### Required GitHub Secrets

Before deploying, add these secrets to your repository under **Settings → Secrets and variables → Actions**:

| Secret | Value |
|--------|-------|
| `AWS_ACCESS_KEY_ID` | Your AWS IAM access key |
| `AWS_SECRET_ACCESS_KEY` | Your AWS IAM secret key |
| `TF_VAR_key_pair_name` | EC2 key pair name in AWS |
| `TF_VAR_groq_api_key` | Your Groq API key |
| `TF_VAR_postgres_password` | Strong database password |
| `TF_VAR_grafana_password` | Grafana admin password |
| `EC2_HOST` | Your DuckDNS hostname: `infra-autofix.duckdns.org` |
| `EC2_SSH_PRIVATE_KEY` | Full contents of your `.pem` key file |
| `DUCKDNS_DOMAIN` | `infra-autofix` (just the subdomain, not the full hostname) |
| `DUCKDNS_TOKEN` | Your DuckDNS token (from duckdns.org dashboard) |

### Free Domain Setup (DuckDNS)

Because no Elastic IP is used, the EC2 instance gets a new public IP on every stop/start. DuckDNS keeps a stable hostname pointing to the current IP automatically.

**One-time setup (takes ~3 minutes):**

1. Go to [duckdns.org](https://www.duckdns.org) and log in with GitHub
2. Create a subdomain — e.g. `infra-autofix` → gives you `infra-autofix.duckdns.org`
3. Note your **token** from the top of the DuckDNS dashboard
4. SSH into your EC2 instance and install the cron job:

```bash
# Make the script executable
chmod +x /home/ubuntu/infra-autofix-agent/scripts/update_duckdns.sh

# Test it first
DUCKDNS_DOMAIN=your-subdomain DUCKDNS_TOKEN=your-token \
  /home/ubuntu/infra-autofix-agent/scripts/update_duckdns.sh
# Should print: OK — your-subdomain.duckdns.org updated successfully.

# Add the cron job (runs every 5 minutes)
crontab -e
```

Add this line to crontab (replace `your-subdomain` and `your-token`):
```
*/5 * * * * DUCKDNS_DOMAIN=your-subdomain DUCKDNS_TOKEN=your-token /home/ubuntu/infra-autofix-agent/scripts/update_duckdns.sh >> /home/ubuntu/duckdns.log 2>&1
```

5. Update the `EC2_HOST` GitHub Secret to your DuckDNS hostname:
   - **Settings → Secrets and variables → Actions → `EC2_HOST`**
   - Set value to: `infra-autofix.duckdns.org` (your actual subdomain)

**After this is set up, access the app at:** `http://infra-autofix.duckdns.org:3000`

> **The DuckDNS cron job is also automatically installed/updated every time you run the "Deploy App to EC2" GitHub Actions workflow** — so you don't need to SSH in to set it up manually. Just add `DUCKDNS_DOMAIN` and `DUCKDNS_TOKEN` as GitHub Secrets and the workflow handles it.

> **Note on Elastic IP:** If you already have an Elastic IP allocated, release it in the AWS Console → EC2 → Elastic IPs → Disassociate → Release. This stops the ~$3.60/month charge immediately.

---

### Deploying Infrastructure (Terraform)

The **"Deploy Infrastructure (Terraform)"** workflow provisions the EC2 instance, security group, and Elastic IP.

```
GitHub → Actions → "Deploy Infrastructure (Terraform)" → Run workflow → apply
```

The workflow also auto-triggers when files under `terraform/` change on `main`.

To tear down all AWS resources:

```
GitHub → Actions → "Deploy Infrastructure (Terraform)" → Run workflow → destroy
```

### Deploying Application Code (Docker)

The **"Deploy App to EC2"** workflow SSHs into the EC2 instance, pulls the latest code from `main`, and rebuilds all Docker containers. Trigger it manually whenever you push application changes:

```
GitHub → Actions → "Deploy App to EC2" → Run workflow
```

What it does on the server:
1. `git pull origin main`
2. `docker compose -f docker-compose.yml -f docker-compose.prod.yml up -d --build --remove-orphans`
3. `docker image prune -f` (reclaims disk space)

> **Note:** The production override (`docker-compose.prod.yml`) sets `FLASK_ENV=production`, applies memory limits per service (app: 350m, bot: 150m, postgres: 200m, prometheus: 256m, grafana: 256m, frontend: 50m), and suppresses port-forwarding for PostgreSQL so it is only accessible internally.

### Production Environment Variables on EC2

On the EC2 instance, create `/home/ubuntu/infra-autofix-agent/.env` from the template:

```bash
cp .env.production.example .env
nano .env   # fill in all <CHANGE_ME> values
```

Key values to set:
```bash
FLASK_ENV=production
POSTGRES_PASSWORD=<strong_password>
DATABASE_URL=postgresql://remediation_user:<strong_password>@postgres:5432/remediation_db
GRAFANA_PASSWORD=<grafana_password>
GROQ_API_KEY=<your_groq_api_key>
GROQ_MODEL=llama-3.3-70b-versatile
```

---

## Architecture

### Component Overview

```
┌────────────────────────────────────────────────────────────────┐
│                       User Interface                           │
│   React Dashboard · AI Chat · System Logs · Incidents (3000)   │
│   nginx proxies /api/, /health, /socket.io/ → Flask            │
└────────────────────┬───────────────────────────────────────────┘
                     │
                     ▼
┌────────────────────────────────────────────────────────────────┐
│                Application Layer (Port 5000)                   │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  Flask API Server                                        │  │
│  │  • REST Endpoints      • WebSocket (Socket.IO) Events   │  │
│  │  • Health Checks       • Configuration                  │  │
│  └──────────────────────────────────────────────────────────┘  │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  ML Engine (runs locally — no external deps)             │  │
│  │  • Anomaly Detection (Isolation Forest, scikit-learn)   │  │
│  │  • Time-Series Forecasting (Facebook Prophet)           │  │
│  │  • Failure Prediction (LightGBM)                        │  │
│  │  • Metrics export / model management (ml_routes.py)     │  │
│  └──────────────────────────────────────────────────────────┘  │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  AI Chat (external — requires internet + Groq key)       │  │
│  │  • Calls https://api.groq.com/openai/v1/chat/completions │  │
│  │  • Model: llama-3.3-70b-versatile                        │  │
│  │  • Context: recent incidents + system health injected    │  │
│  └──────────────────────────────────────────────────────────┘  │
└──────────┬──────────────────────┬───────────────────┬──────────┘
           │                      │                   │
           ▼                      ▼                   ▼
    ┌─────────────┐      ┌──────────────────┐  ┌─────────────────┐
    │  PostgreSQL │      │  Groq API (cloud) │  │ Remediation Bot │
    │  Database   │      │  Llama 3.3 70B    │  │  Port 8000      │
    └─────────────┘      └──────────────────┘  └────────┬────────┘
                                                         │
                          ┌──────────────────────────────┘
                          ▼
    ┌────────────────────────────────────────────────────────┐
    │                  Observability Stack                   │
    │  Prometheus (9090) · Grafana (3001) · Loki (3100)      │
    └────────────────────────────────────────────────────────┘
```

### What Runs Where

| Component | Runs Locally? | Notes |
|-----------|--------------|-------|
| Flask API | ✅ Yes | Docker container `ar_app` |
| PostgreSQL | ✅ Yes | Docker container `ar_postgres` |
| Anomaly Detection | ✅ Yes | scikit-learn inside `ar_app` |
| Forecasting | ✅ Yes | Prophet inside `ar_app` |
| Failure Prediction | ✅ Yes | LightGBM inside `ar_app` |
| Auto-Remediation Bot | ✅ Yes | Docker container `ar_bot` |
| React Frontend / nginx | ✅ Yes | Docker container `ar_frontend` |
| Prometheus | ✅ Yes | Docker container `ar_prometheus` |
| Grafana | ✅ Yes | Docker container `ar_grafana` |
| Loki / Promtail | ✅ Yes | Docker containers |
| **AI Chat (LLM)** | ❌ No | Calls Groq API over internet — requires `GROQ_API_KEY` |

### Data Flow

```
Metrics Collection → Feature Engineering → ML Models → Incident Detection
        ↓                                                      ↓
   PostgreSQL ←─── Incident Created ─────────────────────────┘
        │                  │
        │                  ├─→ Failure Prediction (local LightGBM)
        │                  ├─→ Time Series Forecast (local Prophet)
        │                  └─→ AI Chat context (sent to Groq API)
        │                               │
        ↓                               ↓
  Continuous Learning ←──── LLM Response displayed in Chat
  (Auto-retraining)
```

---

## UI Pages

| Page | Route | Description |
|------|-------|-------------|
| **Dashboard** | `/` | CPU/memory/error rate charts with live WebSocket updates, incident timeline |
| **Incidents** | `/incidents` | Full incident list with filters by status and severity |
| **System Logs** | `/system-logs` | Health banner, metric cards, incident severity summary, raw health JSON, 15s auto-refresh |
| **AI Chat** | `/chat` | Chat with Groq Llama 3.3 70B — incident-aware contextual answers |
| **Remediation** | `/remediation` | Remediation action history and status |
| **Manual Control** | `/manual-control` | Trigger manual remediation actions |
| **Configuration** | `/config` | Adjust thresholds and bot behaviour |

### Notification Bell (top navbar)
- Fetches active incidents every 15 seconds
- Shows a red badge with the count of active incidents
- Clicking opens a dropdown listing the most recent incidents with severity colours and links to the Incidents and System Logs pages

---

## ML/AI Capabilities

### Anomaly Detection (local)
- **Algorithm**: Isolation Forest (scikit-learn)
- **Accuracy**: 92-95%
- **Inference latency**: <10ms
- **Features**: 100+ engineered metrics from `metrics_history` table

### Time-Series Forecasting (local)
- **Algorithm**: Facebook Prophet
- **Prediction window**: 1-24 hours ahead
- **Use case**: Proactive threshold breach detection

### Failure Prediction (local)
- **Algorithm**: LightGBM
- **Prediction window**: 1-72 hours
- **Risk levels**: High / Medium / Low

### AI Chat Assistant (external — Groq API)
- **Provider**: [Groq](https://console.groq.com) (free tier available)
- **Model**: `llama-3.3-70b-versatile`
- **Endpoint**: `https://api.groq.com/openai/v1/chat/completions`
- **Context injection**: Recent incidents, current system health, and metrics are automatically included in every request
- **Requires**: `GROQ_API_KEY` environment variable — get one free at [console.groq.com](https://console.groq.com)
- **Capabilities**:
  - Natural language incident querying
  - Root cause analysis with actionable recommendations
  - Interactive troubleshooting assistant

### Continuous Learning (local)
- **Auto-retraining**: Every 24 hours
- **Performance tracking**: Accuracy, precision, MAE stored in database
- **Model versioning**: Full history in `ml_models` table

---

## API Reference

### Core Endpoints

```bash
# Health check (returns full metrics JSON)
GET /health

# Get incidents
GET /api/incidents?status=active&severity=critical&limit=50

# Trigger manual remediation
POST /api/remediation/manual
{
  "action_type": "restart_container",
  "target": "ar_app",
  "reason": "Manual restart"
}
```

### ML / AI Endpoints

```bash
# AI Chat Assistant (requires GROQ_API_KEY)
POST /api/ml/chat
{
  "message": "What incidents occurred in the last 24 hours?",
  "include_context": true
}

# Anomaly detection
POST /api/ml/predict/anomaly
GET /api/ml/anomaly/status

# Time-series forecast
GET /api/ml/forecast/predict?target_metric=cpu&hours_ahead=6

# Failure prediction
POST /api/ml/failure-prediction/predict

# Metrics export (JSON or CSV)
GET /api/ml/metrics/export?start_date=2026-01-01&format=csv

# Metrics statistics
GET /api/ml/metrics/stats

# List ML models
GET /api/ml/models
GET /api/ml/models/<id>

# Train anomaly detector
POST /api/ml/train/anomaly-detector

# Generate synthetic training data
POST /api/ml/train/generate-synthetic
```

**Interactive API documentation**: http://localhost:5000/api/docs

---

## Configuration

### Key Environment Variables

```bash
# ── Application ───────────────────────────────────────────────
FLASK_ENV=development          # development | production
APP_PORT=5000
ML_ENABLED=true                # set false to disable all ML/AI routes

# ── AI Chat (Groq — required for /chat page) ──────────────────
GROQ_API_KEY=your_key_here     # free key at https://console.groq.com
GROQ_MODEL=llama-3.3-70b-versatile

# ── Thresholds ────────────────────────────────────────────────
CPU_THRESHOLD=80
ERROR_RATE_THRESHOLD=0.2
RESPONSE_TIME_THRESHOLD_MS=500

# ── Remediation Bot ───────────────────────────────────────────
BOT_POLL_SECONDS=5
MAX_RESTARTS_PER_5MIN=3
COOLDOWN_SECONDS=120

# ── Database ──────────────────────────────────────────────────
POSTGRES_USER=remediation_user
POSTGRES_PASSWORD=remediation_pass
POSTGRES_DB=remediation_db
DATABASE_URL=postgresql://remediation_user:remediation_pass@postgres:5432/remediation_db

# ── Grafana ───────────────────────────────────────────────────
GRAFANA_ADMIN_USER=admin
GRAFANA_ADMIN_PASSWORD=admin   # change this in production!

# ── Notifications (optional) ─────────────────────────────────
SLACK_WEBHOOK_URL=             # leave empty to disable

# ── Data Retention ────────────────────────────────────────────
DATA_RETENTION_DAYS=180
CLEANUP_INTERVAL_HOURS=24
```

Copy `.env.example` for local use, or `.env.production.example` for production/EC2 use.

---

## Monitoring

### Grafana Dashboards
- System Overview (incidents, remediations, success rate)
- ML Performance (accuracy, predictions, retraining history)
- Infrastructure Metrics (CPU, memory, disk, request rates)

**Grafana credentials**: `admin` / value of `GRAFANA_ADMIN_PASSWORD` (default: `admin` locally)

To reset the Grafana password on a running instance:
```bash
docker exec ar_grafana grafana-cli admin reset-admin-password NewPassword123
```

### Prometheus Alerts
- High error rate (>5%)
- CPU usage (>90%)
- Memory usage (>85%)
- Incident rate spike

### Logs (Loki)
Access via Grafana → Explore, using these LogQL queries:
```
{container="ar_app"}         # Flask application logs
{container="ar_bot"}         # Remediation bot logs
{container="ar_frontend"}    # nginx / frontend logs
```

---

## Troubleshooting

**Services not starting?**
```bash
docker compose ps              # check status
docker compose logs app        # Flask logs
docker compose logs bot        # bot logs
docker compose logs frontend   # nginx logs
```

**Dashboard shows "Failed to load dashboard data"?**
```bash
# Check Flask is healthy
curl http://localhost:5000/health

# Check nginx is proxying correctly
docker compose logs frontend
```

**AI Chat returns "AI service not configured"?**
- You need to set `GROQ_API_KEY` in your `.env` file
- Get a free key at [console.groq.com](https://console.groq.com)
- Restart the app container after adding the key: `docker compose restart app`

**WebSocket not connecting (live metrics not updating)?**
- The frontend connects Socket.IO via nginx to `/socket.io/` which is proxied to Flask
- Check: `docker compose logs frontend | grep socket`
- Ensure `ar_app` is healthy: `docker compose ps`

**Grafana password forgotten (on EC2)?**
```bash
# SSH into EC2 then:
grep GRAFANA_PASSWORD /home/ubuntu/infra-autofix-agent/.env
# or reset it:
docker exec ar_grafana grafana-cli admin reset-admin-password NewPassword123
```

**Out of memory on Docker Desktop (local)?**
```bash
docker stats    # check per-container usage
# Increase Docker Desktop memory limit in Settings → Resources (4GB minimum recommended)
```

---

## Development

### Running Tests

```bash
# Backend tests
cd tests
pytest test_app.py -v
pytest test_bot.py -v

# Or from project root
docker compose exec app pytest tests/ --cov
```

### Running Without Docker

```bash
# Backend (requires a running PostgreSQL instance)
cd app
python -m venv venv
source venv/bin/activate       # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp ../.env.example .env        # then edit .env
python app.py

# Frontend (Vite dev server — proxies /api/ and /health to http://app:5000)
cd frontend
npm install
npm run dev
# Access at http://localhost:3000

# Bot
cd bot
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python bot.py
```

> **Note:** The Vite dev server (`vite.config.js`) already proxies `/api/` and `/health` to `http://app:5000`, so local frontend development works correctly when the backend container is running.

---

## Contributing

Contributions are welcome!

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/amazing-feature`
3. Commit your changes: `git commit -m 'Add amazing feature'`
4. Push to the branch: `git push origin feature/amazing-feature`
5. Open a Pull Request

---

## Documentation

- [API Documentation](docs/API.md) — Complete API reference
- [Operations Guide](docs/operations.md) — Configuration and troubleshooting
- [Docker Guide](docs/docker.md) — Docker Compose details

---

## License

MIT License — see [LICENSE](LICENSE) for details.

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Frontend | React 18, Vite, Tailwind CSS, Socket.IO client |
| Backend | Python 3.11, Flask, Flask-SocketIO, SQLAlchemy |
| Database | PostgreSQL 15 |
| Local ML | scikit-learn (Isolation Forest), LightGBM, Facebook Prophet |
| AI Chat | Groq API — `llama-3.3-70b-versatile` (external, free tier) |
| Observability | Prometheus, Grafana, Loki, Promtail |
| Infrastructure | Docker Compose, Terraform (AWS EC2 t2.micro), GitHub Actions |

---

**Project Status**: Production Ready | **Version**: 1.0 | **License**: MIT

> **⚠️ Important**: Grafana dashboards need to be imported manually in Kubernetes. See [Quick Start Guide](docs/quick-start.md#6-configure-grafana-dashboards).

See [Kubernetes Deployment Guide](docs/kubernetes.md) for detailed instructions.

### Access Interfaces

**Docker Compose URLs:**

| Service | URL | Credentials | Notes |
|---------|-----|-------------|-------|
| 🎨 **React Dashboard** | **http://localhost:3000** | - | **Main UI with ML insights** |
| 📖 **Swagger API Docs** | **http://localhost:5000/api/docs** | - | **Interactive ML API testing** |
| 🔧 Backend API | http://localhost:5000 | - | REST + WebSocket |
| 📊 Grafana | http://localhost:3001 | admin/admin | Dashboards & alerts |
| 📈 Prometheus | http://localhost:9090 | - | Metrics query UI |
| 📝 Loki | http://localhost:3100 | - | Log aggregation |
| 🤖 Ollama (LLM) | http://localhost:11434 | - | Local AI model API |

**ML/AI Feature Access:**
- **Dashboard UI**: http://localhost:3000 - View incidents with AI analysis, predictions, and anomaly scores
- **Swagger API**: http://localhost:5000/api/docs - Test all ML endpoints interactively
- **Direct API**: http://localhost:5000/api/ml/* - Programmatic access to ML features
  - `/api/ml/anomaly/*` - Anomaly detection
  - `/api/ml/forecast/*` - Time series predictions
  - `/api/ml/failure-prediction/*` - Failure forecasting
  - `/api/ml/analyze/*` - LLM incident analysis
  - `/api/ml/continuous-learning/*` - Model management

**Kubernetes URLs (Docker Desktop):**

| Service | URL | Credentials | Purpose |
|---------|-----|-------------|---------|
| 🎨 **Dashboard** | **http://localhost** | - | **Main UI with ML insights** |
| 📖 **Swagger API** | **http://localhost:5000/api/docs** | - | **Interactive ML API docs** |
| 🔧 Backend API | http://localhost:5000 | - | REST API + WebSocket |
| 📊 Grafana | http://localhost:3000 | admin/admin | Monitoring dashboards |
| 📈 Prometheus | http://localhost:9090 | - | Metrics database |

> **💡 ML Features**: All AI/ML insights are **integrated into the main dashboard**. No separate ML UI needed - anomaly scores, predictions, and AI analysis are displayed directly in the incidents view!

## 🏗️ Architecture

**Full System Architecture:**
```
┌─────────────────────────────────────────────────────────────────┐
│                        User Interfaces                          │
├─────────────────────────────────────────────────────────────────┤
│  🎨 React Dashboard (3000)    │  📖 Swagger API Docs (5000)    │
│  - Real-time monitoring        │  - Interactive ML API testing  │
│  - AI insights display         │  - All endpoints documented    │
│  - Incident management         │  - Try ML features live        │
└────────────────┬────────────────────────────┬───────────────────┘
                 │                            │
                 ▼                            ▼
       ┌─────────────────────────────────────────────────┐
       │         Flask API + ML Engine (5000)            │
       │  ┌──────────────────────────────────────────┐   │
       │  │  REST API  │  WebSocket  │  ML Routes   │   │
       │  └──────────────────────────────────────────┘   │
       │  ┌──────────────────────────────────────────┐   │
       │  │          6 ML Models Pipeline            │   │
       │  │  Phase 2: Anomaly Detection (IForest)    │   │
       │  │  Phase 3: Time Series Forecast (Prophet) │   │
       │  │  Phase 4: LLM Analysis (Ollama)          │   │
       │  │  Phase 5: Failure Prediction (LightGBM)  │   │
       │  │  Phase 6: Continuous Learning            │   │
       │  └──────────────────────────────────────────┘   │
       └────┬──────────────────┬─────────────────┬───────┘
            │                  │                 │
            ▼                  ▼                 ▼
   ┌────────────────┐  ┌─────────────┐  ┌──────────────┐
   │  PostgreSQL    │  │   Ollama    │  │ Remediation  │
   │  Database      │  │ LLM Service │  │     Bot      │
   │  - Metrics     │  │ Llama 3.2   │  │ - Auto-heal  │
   │  - Incidents   │  │ (3B params) │  │ - ML checks  │
   │  - ML Data     │  │  Port 11434 │  │ - Retraining │
   └────────────────┘  └─────────────┘  └──────┬───────┘
                                                │
            ┌───────────────────────────────────┴──────┐
            │                                          │
            ▼                                          ▼
   ┌──────────────────┐                    ┌──────────────────┐
   │  Observability   │                    │   Container      │
   │  Stack           │                    │   Infrastructure │
   ├──────────────────┤                    ├──────────────────┤
   │ • Prometheus     │◀───────────────────│ • App Containers │
   │ • Grafana        │                    │ • Docker/K8s     │
   │ • Loki + Promtail│                    │ • Health Checks  │
   └──────────────────┘                    └──────────────────┘
```

**ML Pipeline Data Flow:**
```
┌──────────────┐     ┌────────────────────┐     ┌─────────────────┐
│   Metrics    │────▶│ Feature Engineering│────▶│  Anomaly Model  │
│  Collection  │     │   (100+ features)  │     │ (Isolation Tree)│
└──────────────┘     └────────────────────┘     └────────┬────────┘
                                                          │
                     ┌────────────────────────────────────┘
                     │
                     ▼
         ┌──────────────────────┐
         │  Incident Created?   │
         └──────┬────────┬──────┘
                │ Yes    │ No
                ▼        └─────▶ Continue monitoring
    ┌──────────────────────┐
    │  Parallel ML Tasks   │
    ├──────────────────────┤
    │ 1. Failure Predictor │──▶ Risk: High/Med/Low
    │ 2. Time Series Fcst  │──▶ Breach in N hours
    │ 3. LLM Analyzer      │──▶ Root cause + fixes
    └──────┬───────────────┘
           │
           ▼
    ┌─────────────────┐      ┌──────────────────┐
    │  Store Results  │─────▶│  Display in UI   │
    │  in Database    │      │  & Send Alerts   │
    └─────────────────┘      └──────────────────┘
           │
           ▼
    ┌─────────────────────┐
    │ Continuous Learning │
    │ - Track performance │
    │ - Auto-retrain      │
    │ - Model versioning  │
    └─────────────────────┘
```

## 🤖 ML/AI Features Deep Dive
             └──────────────┘      └─────────────┘
                    │
     ┌──────────────┼──────────────┐
     ▼              ▼              ▼
┌─────────┐  ┌──────────┐  ┌──────────┐
│Prometheus│ │ Grafana  │  │   Loki   │
│  :9090   │ │  :3001   │  │  :3100   │
```

## 🤖 ML/AI Features Deep Dive

> **🎨 Access ML Features**: All AI insights are integrated into the **main dashboard** at http://localhost:3000. View anomaly scores, predictions, and AI analysis directly in the incidents view. For programmatic access, use the **Swagger UI** at http://localhost:5000/api/docs to test all ML endpoints interactively.

### Phase 2: Anomaly Detection
- **Algorithm**: Isolation Forest
- **Features**: 100+ engineered metrics
- **Performance**: 92-95% accuracy, <10ms inference
- **Triggers**: Automatic incident creation for ML-detected anomalies
- **UI**: Anomaly scores shown in dashboard incident cards
- **API**: `POST /api/ml/anomaly/train`, `POST /api/ml/anomaly/predict`
- **Test**: `.\scripts\test-phase2.ps1`

### Phase 3: Time Series Forecasting
- **Algorithm**: Facebook Prophet
- **Capabilities**: 1-24 hour ahead predictions
- **Features**: Daily/weekly seasonality detection
- **Use Case**: Proactive breach detection before thresholds hit
- **UI**: Predicted values displayed in metrics charts
- **API**: `POST /api/ml/forecast/train`, `GET /api/ml/forecast/predict`
- **Test**: `.\scripts\test-phase3.ps1`

### Phase 4: LLM Integration
- **Model**: Ollama + Llama 3.2 (3B parameters)
- **Cost**: 100% free (runs locally)
- **Features**: Root cause analysis, natural language reports, remediation suggestions
- **Requirements**: 4GB RAM, ~2GB model download
- **UI**: AI-generated insights shown in incident details
- **API**: `POST /api/ml/analyze/incident/<id>`, `GET /api/ml/generate-report/<id>`
- **Health Check**: `GET /api/ml/llm/health`
- **Setup**: `docker exec -it ar_ollama ollama pull llama3.2:3b`
- **Test**: `.\scripts\test-phase4.ps1`

### Phase 5: Failure Prediction
- **Algorithm**: LightGBM (gradient boosting)
- **Prediction Window**: 1-72 hours ahead
- **Risk Levels**: High (70%+), Medium (40-70%), Low (<40%)
- **Proactive Alerts**: Creates "predicted_failure" incidents
- **UI**: Risk indicators and predictions in dashboard alerts
- **API**: `POST /api/ml/failure-prediction/train`, `POST /api/ml/failure-prediction/predict`
- **Test**: `.\scripts\test-phase5.ps1`

### Phase 6: Continuous Learning
- **Auto-Retraining**: Every 24 hours or when 100+ new samples collected
- **Performance Monitoring**: Tracks accuracy, precision, MAE
- **Model Versioning**: Full training history in database
- **Triggers**: Time-based, data-volume, performance degradation
- **UI**: Model status and retraining history in config page (future enhancement)
- **API**: `GET /api/ml/continuous-learning/status`, `POST /api/ml/continuous-learning/check-retrain`
- **Test**: `.\scripts\test-phase6.ps1`

### How to Access ML Features

**1. Main Dashboard (http://localhost:3000)**
- View incidents with anomaly scores
- See AI-generated root cause analysis
- Monitor predicted failures
- Check risk indicators

**2. Swagger API (http://localhost:5000/api/docs)**
- Interactive ML endpoint testing
- Try predictions with custom data
- Explore all ML API capabilities
- View request/response schemas

**3. Grafana Dashboards (http://localhost:3001)**
- ML model performance metrics
- Prediction accuracy over time
- Model retraining history
- Anomaly detection rates

**4. Direct API Calls**
```bash
# Check ML system status
curl http://localhost:5000/api/ml/continuous-learning/status

# Get incident AI analysis
curl http://localhost:5000/api/ml/analyze/incident/1

# Check LLM health
curl http://localhost:5000/api/ml/llm/health

# Predict next hour failures
curl -X POST http://localhost:5000/api/ml/failure-prediction/predict
```

**Quick ML Setup:**
```bash
# Start with ML services
docker compose -f docker-compose.yml -f docker-compose.ml.yml up -d

# Download LLM model (one-time)
docker exec -it ar_ollama ollama pull llama3.2:3b

# Check ML system status
curl http://localhost:5000/api/ml/continuous-learning/status

# Run ML test scripts
.\scripts\test-phase4.ps1  # LLM integration
.\scripts\test-phase5.ps1  # Failure prediction
.\scripts\test-phase6.ps1  # Continuous learning
```

See [ML Setup Guide](docs/ml-setup.md) for complete documentation.

## Deployment Options

### 🐳 Docker Compose (Local/Development)
Single-command setup for local development and testing. All services run in containers with Docker networking.

```bash
docker compose up -d
```

### ☸️ Kubernetes (Production/Cloud)
Enterprise-grade deployment with auto-scaling, health checks, and high availability.

- **Raw Manifests**: Full control with `kubectl apply -k k8s/`
- **Helm Charts**: Environment management with `helm install`
- **Kustomize**: Overlay-based configuration

Features:
- Horizontal Pod Autoscaling (2-10 replicas)
- Persistent volumes for databases
- RBAC and service accounts
- LoadBalancers and Ingress
- Multi-environment support (dev/staging/prod)

See [Kubernetes Guide](docs/kubernetes.md) for full deployment instructions.

---

## Development

### Local Setup (Without Docker)

**Backend:**
```powershell
cd app
py -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python app.py
```

**Bot:**
```powershell
cd bot
py -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python bot.py
```

**Frontend:**
```powershell
cd frontend
npm install
npm run dev  # http://localhost:5173
```

### Testing

```powershell
# Backend
cd app
pytest tests/ --cov

# Linting
flake8 app bot

# Frontend
cd frontend
npm run build
```

## 📊 Monitoring & Observability

### Grafana Dashboards
Access at http://localhost:3001 (Docker) or http://localhost:3000 (K8s) with `admin/admin`

**Pre-built Dashboards:**
- **System Overview** - Real-time health, incidents, remediation success rate
- **Application Metrics** - Request rates, latency, error rates by service
- **Infrastructure** - CPU, memory, disk usage across all containers
- **Incident Analysis** - Incident types, frequency, MTTR (Mean Time To Remediation)
- **ML Performance** - Model accuracy, predictions, retraining history

### Prometheus Metrics
Query at http://localhost:9090

**Key Metrics:**
- `http_requests_total` - Total HTTP requests
- `http_request_duration_seconds` - Request latency
- `incidents_total` - Total incidents by type and severity
- `remediations_total` - Successful/failed remediations
- `container_cpu_usage_seconds_total` - Container CPU usage
- `ml_predictions_total` - ML model predictions
- `ml_model_accuracy` - Model performance metrics

### Loki Logs
Access at http://localhost:3100 or via Grafana Explore

**Log Labels:**
- `{container="ar_app"}` - Flask API logs
- `{container="ar_bot"}` - Remediation bot logs
- `{container="ar_frontend"}` - React UI logs

### Alerts
Pre-configured Prometheus alerts in `prometheus/alerts.yml`:
- High error rate (>5% errors)
- Latency spike (p95 > 500ms)
- Resource exhaustion (CPU >90%, Memory >85%)
- Incident rate spike (>10 incidents/5min)

See [Observability Guide](docs/observability.md) for detailed monitoring setup.

## Automation

Includes 7 GitHub Actions workflows for CI/CD:
- **CI** - Testing, linting, building
- **Docker Publish** - GHCR image publishing with semantic versioning
- **Security** - CodeQL, Trivy, dependency scanning
- **Deploy** - AWS ECS and VM deployment
- **Performance** - Locust load testing
- **Release** - Automated GitHub releases
- **Cleanup** - Artifact management

See [docs/github-actions.md](docs/github-actions.md) for details.

## 📚 Documentation

### Essential Guides
- 🚀 **[Quick Start Guide](docs/quick-start.md)** - Complete setup for Docker Compose and Kubernetes
- 🤖 **[ML Setup Guide](docs/ml-setup.md)** - All 6 ML phases with examples and API references
- 📖 **[API Reference](docs/API.md)** - REST endpoints, WebSocket events, request/response formats
- ☸️ **[Kubernetes Guide](docs/kubernetes.md)** - Production deployment with Helm charts

### Operations
- 🔧 **[Operations Guide](docs/operations.md)** - Configuration, testing, troubleshooting
- 📊 **[Observability](docs/observability.md)** - Metrics, dashboards, alerts, logging
- 🐳 **[Docker Commands](docs/docker.md)** - Container management reference

### Automation
- 🚀 **[GitHub Actions](docs/github-actions.md)** - CI/CD workflows and deployment

### API Documentation (Interactive)
- 📖 **Swagger UI**: http://localhost:5000/api/docs (Docker Compose)
- 📖 **Swagger UI**: http://localhost:5000/api/docs (Kubernetes)

**Key API Endpoints:**
- **Core**: `/api/health`, `/api/incidents`, `/api/metrics`, `/api/config`
- **ML Phase 2**: `/api/ml/anomaly/*` - Anomaly detection
- **ML Phase 3**: `/api/ml/forecast/*` - Time series forecasting
- **ML Phase 4**: `/api/ml/analyze/*`, `/api/ml/llm/*` - LLM analysis
- **ML Phase 5**: `/api/ml/failure-prediction/*` - Failure prediction
- **ML Phase 6**: `/api/ml/continuous-learning/*` - Model management

## 🔗 Important URLs

### Local Development (Docker Compose)
```
Main Dashboard:        http://localhost:3000
AI Chat Assistant:     http://localhost:3000/chat
Swagger API Docs:      http://localhost:5000/api/docs
REST API:              http://localhost:5000/api/*
WebSocket:             ws://localhost:5000/ws
Grafana:               http://localhost:3001
Prometheus:            http://localhost:9090
Loki:                  http://localhost:3100
Ollama LLM:            http://localhost:11434
```

### Kubernetes (Docker Desktop)
```
Main Dashboard:        http://localhost
Swagger API Docs:      http://localhost:5000/api/docs
REST API:              http://localhost:5000/api/*
Grafana:               http://localhost:3000
Prometheus:            http://localhost:9090
```

### GitHub Repository
```
Source Code:           https://github.com/mainulhossain123/infra-autofix-agent
CI Pipeline:           https://github.com/mainulhossain123/infra-autofix-agent/actions
Container Registry:    ghcr.io/mainulhossain123/infra-autofix-agent
Issues:                https://github.com/mainulhossain123/infra-autofix-agent/issues
```

## License

MIT © 2025
