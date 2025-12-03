# Docker & Containers

## Services
- app (Flask backend)
- frontend (React dashboard)
- postgres (database)
- bot (auto-remediation worker)
- prometheus (metrics)

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