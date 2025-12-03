# API Reference

Base URL: `http://localhost:5000`

## Health & Metrics
- GET `/api/health`
- GET `/api/metrics`
- GET `/metrics`
- GET `/api/database/health`
- GET `/api/database/connections`

## Incidents
- GET `/api/incidents`
- GET `/api/incidents/{id}`

## Remediation
- GET `/api/remediation/history`
- POST `/api/remediation/manual`

Example:
```json
POST /api/remediation/manual
{
  "action_type": "restart_container",
  "target": "ar_app",
  "reason": "Manual intervention"
}
```

## Configuration
- GET `/api/config`
- GET `/api/config/{key}`
- PUT `/api/config`

Example:
```json
PUT /api/config
{
  "key": "error_rate_threshold",
  "value": 0.10
}
```