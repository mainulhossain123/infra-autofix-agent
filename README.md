# infra-autofix-agent

[![CI Pipeline](https://github.com/mainulhossain123/infra-autofix-agent/actions/workflows/ci.yml/badge.svg)](https://github.com/mainulhossain123/infra-autofix-agent/actions/workflows/ci.yml)
[![Security Scanning](https://github.com/mainulhossain123/infra-autofix-agent/actions/workflows/security.yml/badge.svg)](https://github.com/mainulhossain123/infra-autofix-agent/actions/workflows/security.yml)
[![Docker Publish](https://github.com/mainulhossain123/infra-autofix-agent/actions/workflows/docker-publish.yml/badge.svg)](https://github.com/mainulhossain123/infra-autofix-agent/actions/workflows/docker-publish.yml)

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

- Backend: Python 3.11+ (py launcher recommended), Flask, Flask-SocketIO, SQLAlchemy
- Frontend: Node.js (18+), React (Vite), Tailwind
- Database: PostgreSQL (via Docker Compose)

Local development (Windows PowerShell - simplest copy/paste commands)

1) Verify prerequisites (run each; install missing tools first):

```powershell
docker --version
docker compose version
py --version    # or: python --version
node --version
npm --version
```

2) Backend (app) - create virtualenv and install dependencies:

```powershell
cd app
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
python app.py
```

3) Bot - create virtualenv and install dependencies (bot uses Docker SDK):

```powershell
cd ..\bot
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
python bot.py
```

4) Frontend - install and run dev server (or build for production):

```powershell
cd ..\frontend
npm install
npm run dev        # development: uses Vite (http://localhost:5173)
# OR build static files for Docker/nginx
npm run build
```

5) (Recommended) Run entire stack with Docker Compose from project root:

```powershell
cd ..\           # project root (where docker-compose.yml lives)
docker compose up --build -d
docker compose ps
docker compose logs -f
```

6) Stop the stack:

```powershell
docker compose down
```

Testing & troubleshooting (quick checks)

```powershell
# API health:
curl http://localhost:5000/health

# Prometheus metrics endpoint:
curl http://localhost:5000/metrics

# Dashboard (when frontend container served on 3000):
start http://localhost:3000
```

Notes:
- On Windows use the `py` launcher when available (preferred for selecting installed Python versions).
- If you prefer WSL/Linux/macOS, replace PowerShell activation commands with `python3 -m venv .venv` and `source .venv/bin/activate`.
- Do not commit secrets. Use environment variables (see `docker-compose.yml`).

## Docs

- API reference: docs/API.md
- Docker commands: docs/docker.md
- Operations & troubleshooting: docs/operations.md

## GitHub Actions & Automation

This project includes automated CI/CD workflows:

**🔄 Continuous Integration (`ci.yml`)**
- Runs on every push and pull request
- Executes Python tests (pytest) with coverage
- Builds and tests all Docker images
- Lints Python (flake8) and frontend code
- Uploads build artifacts

**🐳 Docker Publishing (`docker-publish.yml`)**
- Automatically builds and publishes images to GitHub Container Registry (GHCR)
- Triggered on: pushes to `main`, version tags (`v*.*.*`), manual dispatch
- Multi-platform builds (amd64, arm64)
- Semantic versioning with tags

**🔒 Security Scanning (`security.yml`)**
- CodeQL analysis for Python and JavaScript
- Trivy vulnerability scanning for container images
- Python Safety dependency checks
- Runs weekly and on every PR

**🚀 Deployment (`deploy.yml`)**
- Manual or tag-triggered deployment
- Supports AWS ECS and VM/SSH deployment
- Environment selection (staging/production)
- Zero-downtime rolling updates

**📦 Dependabot (`dependabot.yml`)**
- Automatic dependency updates for Python, npm, Docker, and GitHub Actions
- Weekly PRs for security patches

### Using GitHub Actions

**Pull published images:**
```powershell
docker pull ghcr.io/mainulhossain123/infra-autofix-agent-app:latest
docker pull ghcr.io/mainulhossain123/infra-autofix-agent-bot:latest
docker pull ghcr.io/mainulhossain123/infra-autofix-agent-frontend:latest
```

**Trigger manual deployment:**
- Go to Actions → Deploy to Cloud → Run workflow
- Select environment and version

**Required GitHub Secrets for Deployment:**
- `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`, `AWS_REGION`
- `ECS_CLUSTER_NAME` (for ECS deployment)
- `DEPLOY_HOST`, `DEPLOY_USER`, `DEPLOY_SSH_KEY` (for VM deployment)

## License

MIT © 2025
