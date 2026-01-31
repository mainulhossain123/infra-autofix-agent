# API Reference

> **🎯 Interactive API Documentation**: Visit the [Swagger UI](http://localhost:5000/api/docs) for an interactive API explorer with live testing!

Base URL: `http://localhost:5000`

## 📚 Swagger/OpenAPI Documentation

The API is fully documented using OpenAPI 3.0 specification with interactive Swagger UI.

### Access Points

| Resource | URL | Description |
|----------|-----|-------------|
| **Swagger UI** | [http://localhost:5000/api/docs](http://localhost:5000/api/docs) | Interactive API documentation and testing |
| **OpenAPI Spec** | [http://localhost:5000/apispec.json](http://localhost:5000/apispec.json) | Raw OpenAPI JSON specification |

### Features

- ✅ **Try It Out**: Execute API calls directly from the browser
- ✅ **Request/Response Examples**: See sample payloads for all endpoints
- ✅ **Schema Validation**: Understand required fields and data types
- ✅ **Authentication**: Test with different auth mechanisms
- ✅ **Download Spec**: Export OpenAPI spec for client SDK generation

---

## Quick Reference

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

## ML & AI Features

### AI Chat Assistant
- POST `/api/ml/chat`

Interact with the AI assistant for incident analysis and troubleshooting.

**Request:**
```json
{
  "message": "What incidents occurred in the last 24 hours?",
  "include_context": true,
  "incident_id": 123
}
```

**Response:**
```json
{
  "response": "Based on recent data, there are 4 high_response_time incidents...",
  "context_used": {
    "recent_incidents": [...],
    "recent_remediations": [...]
  },
  "timestamp": "2026-01-31T09:59:00.123456"
}
```

### ML Endpoints
- GET `/api/ml/metrics` - Export metrics for ML training
- POST `/api/ml/predict` - Get anomaly predictions
- GET `/api/ml/models` - List trained models
- POST `/api/ml/train` - Trigger model training