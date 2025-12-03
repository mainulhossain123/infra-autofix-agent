#!/bin/bash
# Quick health check script

echo "Checking Auto-Remediation Platform Health..."
echo ""

# Check if containers are running
echo "=== Container Status ==="
docker ps --filter "name=ar_" --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
echo ""

# Check app health
echo "=== Application Health ==="
curl -s http://localhost:5000/api/health | jq '.' || echo "App not responding"
echo ""

# Check database connection
echo "=== Database Connection ==="
docker exec ar_postgres pg_isready -U remediation_user && echo "Database is ready" || echo "Database not ready"
echo ""

# Check recent incidents
echo "=== Recent Incidents (last 5) ==="
curl -s "http://localhost:5000/api/incidents?limit=5" | jq '.incidents[] | {type, severity, status, timestamp}' || echo "Cannot fetch incidents"
echo ""

# Check remediation actions
echo "=== Recent Remediation Actions (last 5) ==="
curl -s "http://localhost:5000/api/remediation/history?limit=5" | jq '.actions[] | {action_type, target, success, timestamp}' || echo "Cannot fetch remediation history"
echo ""

echo "Health check complete!"
