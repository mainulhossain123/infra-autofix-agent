# Docker & Containers

## Services
- **app** - Flask backend (port 5000)
- **frontend** - React dashboard (port 3000)
- **postgres** - PostgreSQL database (port 5432)
- **bot** - Auto-remediation worker (port 8000 for metrics)
- **prometheus** - Metrics collection (port 9090)
- **grafana** - Dashboards and visualization (port 3001)
- **loki** - Log aggregation (port 3100)
- **promtail** - Log shipping agent

## Common commands (PowerShell)
```powershell
# Start
docker compose up -d

# Build
docker compose up --build -d

# Logs
docker compose logs -f

# Rebuild app service
docker compose up --build ar_app

# List services
docker compose ps

# Stop
docker compose down
```

## Database access (local only)
```powershell
docker exec -it ar_postgres psql -U remediation_user -d remediation_db
```