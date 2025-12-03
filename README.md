# infra-autofix-agent

A compact, production-oriented auto-remediation agent for containerized services. This repository contains a Flask backend, a remediation bot, a React dashboard, and a Prometheus scrape target.

This README contains only necessary, code-related information: how to run the project locally, the core services, key API endpoints, configuration options, and development notes.

## Table of contents

- Overview
- Quick start
- Services
- Key API endpoints
- Configuration
- Development notes
- Docs
- License

---

## Overview

infra-autofix-agent monitors a service, detects incidents (crashes, high error rates, CPU spikes, high latency), logs incidents to PostgreSQL, and performs safe remediation actions (container restarts) with a circuit breaker to avoid restart loops. It exposes metrics for Prometheus and pushes realtime updates to a React dashboard via WebSocket.

## Quick start (Docker, PowerShell)

1. Clone

```powershell
git clone https://github.com/mainulhossain123/infra-autofix-agent.git
cd infra-autofix-agent
```

2. Start services

```powershell
docker compose up --build -d
```

3. Validate

- Dashboard: http://localhost:3000
- API: http://localhost:5000
- Prometheus UI (if running): http://localhost:9090

## Services (compose)

- ar_app: Flask backend (API + /metrics)
- ar_frontend: React dashboard
- ar_postgres: PostgreSQL (incidents & actions)
- ar_bot: Remediation worker (detectors + remediation)
- ar_prometheus: Prometheus (optional - scrapes `ar_app`)

## Key API endpoints (summary)

Base URL: http://localhost:5000

Health & metrics
- GET /health
- GET /api/health
- GET /api/metrics
- GET /metrics  (Prometheus format)

Incidents
- GET /api/incidents
- GET /api/incidents/{id}

Remediation
- GET /api/remediation/history
- POST /api/remediation/manual

Simulations (test-only)
- POST /crash
- POST /api/trigger/cpu-spike?duration={s}
- POST /api/trigger/error-spike?duration={s}
- POST /api/trigger/latency-spike?duration={s}
- POST /api/trigger/stop-all

## Configuration

Config is sourced from environment variables and persisted configuration. Do not commit secrets.

Important environment variables (examples)
- BOT_POLL_SECONDS (default: 5)
- ERROR_RATE_THRESHOLD (default: 0.2)
- CPU_THRESHOLD (default: 80)
- MAX_RESTARTS_PER_5MIN (default: 3)
- COOLDOWN_SECONDS (default: 120)
- DATA_RETENTION_DAYS (default: 180)

Update runtime configuration via API

PUT /api/config
```json
{ "key": "error_rate_threshold", "value": 0.10 }
```

## Development

- Backend: Python 3.11, Flask, Flask-SocketIO, SQLAlchemy
- Frontend: React (Vite), Tailwind
- Database: PostgreSQL

Local development (run without Docker)

Backend
```powershell
cd app
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python app.py
```

Frontend
```powershell
cd frontend
npm install
npm run dev
```

Testing & troubleshooting

- View logs:
```powershell
docker compose logs -f
```
- Check services:
```powershell
docker compose ps
```
- Check Prometheus metrics (raw):
```powershell
curl http://localhost:5000/metrics
```

## Docs

- API reference: docs/API.md
- Docker commands: docs/docker.md
- Operations & troubleshooting: docs/operations.md

## License

MIT © 2025
